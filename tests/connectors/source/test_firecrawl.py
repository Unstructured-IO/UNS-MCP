import os
import pytest
import tempfile
import boto3
import asyncio
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from connectors.source.firecrawl import (
    _ensure_valid_s3_uri,
    _upload_directory_to_s3,
    poll_crawl_until_complete,
    process_and_upload_crawl_results,
    wait_for_crawl_completion,
    invoke_firecrawl,
    check_crawl_status
)

# Test _ensure_valid_s3_uri
def test_ensure_valid_s3_uri_valid_input():
    """Test that valid S3 URIs are accepted and normalized."""
    # Test with already valid URI
    assert _ensure_valid_s3_uri("s3://bucket/path/") == "s3://bucket/path/"
    
    # Test with URI missing trailing slash
    assert _ensure_valid_s3_uri("s3://bucket/path") == "s3://bucket/path/"
    
    # Test with simple bucket URI
    assert _ensure_valid_s3_uri("s3://bucket") == "s3://bucket/"


def test_ensure_valid_s3_uri_invalid_input():
    """Test that invalid S3 URIs raise appropriate errors."""
    # Test with empty string
    with pytest.raises(ValueError, match="S3 URI is required"):
        _ensure_valid_s3_uri("")
    
    # Test with non-S3 URI
    with pytest.raises(ValueError, match="S3 URI must start with 's3://'"):
        _ensure_valid_s3_uri("http://example.com")
    
    # Test with None
    with pytest.raises(ValueError, match="S3 URI is required"):
        _ensure_valid_s3_uri(None)


# Mock S3 client for testing uploads
@pytest.fixture
def mock_s3_client():
    """Create a mock of boto3 S3 client."""
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3


# Test _upload_directory_to_s3
def test_upload_directory_to_s3(mock_s3_client):
    """Test uploading a directory to S3."""
    # Create a temporary directory with some test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a couple of test files
        test_file_1 = os.path.join(temp_dir, "test1.txt")
        test_file_2 = os.path.join(temp_dir, "test2.txt")
        
        with open(test_file_1, "w") as f:
            f.write("Test content 1")
        with open(test_file_2, "w") as f:
            f.write("Test content 2")
        
        # Set environment variables for S3 access
        with patch.dict(os.environ, {'AWS_KEY': 'test-key', 'AWS_SECRET': 'test-secret'}):
            # Call the function
            s3_uri = "s3://test-bucket/prefix/"
            result = _upload_directory_to_s3(temp_dir, s3_uri)
            
            # Verify S3 client was called correctly
            assert mock_s3_client.upload_file.call_count == 2
            
            # Verify result statistics
            assert result["uploaded_files"] == 2
            assert result["failed_files"] == 0
            assert result["total_bytes"] > 0


def test_upload_directory_to_s3_with_errors(mock_s3_client):
    """Test handling errors during S3 upload."""
    # Setup mock to raise an exception on upload
    mock_s3_client.upload_file.side_effect = Exception("Mock S3 error")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")
        
        # Set environment variables for S3 access
        with patch.dict(os.environ, {'AWS_KEY': 'test-key', 'AWS_SECRET': 'test-secret'}):
            # Call the function
            s3_uri = "s3://test-bucket/prefix/"
            result = _upload_directory_to_s3(temp_dir, s3_uri)
            
            # Verify result statistics reflect the failure
            assert result["uploaded_files"] == 0
            assert result["failed_files"] == 1


# Test async functions
@pytest.mark.asyncio
async def test_poll_crawl_until_complete():
    """Test polling a crawl job until completion."""
    # Mock the FirecrawlApp class
    with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
        # Configure the mock to return a completed status
        mock_firecrawl = MagicMock()
        MockFirecrawlApp.return_value = mock_firecrawl
        
        # First call returns in-progress, second call returns completed
        mock_firecrawl.check_crawl_status.side_effect = [
            {"status": "scraping"},
            {"status": "completed", "completed": 10, "total": 10}
        ]
        
        # Call the function with a short poll interval for testing
        result = await poll_crawl_until_complete(
            crawl_id="test-id",
            api_key="test-key",
            poll_interval=0.1,  # Short interval for testing
            timeout=10
        )
        
        # Verify results
        assert result["status"] == "completed"
        assert "result" in result
        assert "elapsed_time" in result


@pytest.mark.asyncio
async def test_poll_crawl_until_timeout():
    """Test that polling times out after the specified duration."""
    with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        MockFirecrawlApp.return_value = mock_firecrawl
        
        # Always return in-progress status
        mock_firecrawl.check_crawl_status.return_value = {"status": "scraping"}
        
        # Call with very short timeout
        result = await poll_crawl_until_complete(
            crawl_id="test-id",
            api_key="test-key",
            poll_interval=0.1,
            timeout=0.3  # Very short timeout for testing
        )
        
        # Verify timeout was detected
        assert result["status"] == "timeout"
        assert "error" in result


@pytest.mark.asyncio
async def test_process_and_upload_crawl_results():
    """Test processing crawl results and uploading to S3."""
    # Mock the _upload_directory_to_s3 function
    with patch('connectors.source.firecrawl._upload_directory_to_s3') as mock_upload:
        # Configure mock to return success stats
        mock_upload.return_value = {
            "uploaded_files": 5,
            "failed_files": 0,
            "total_bytes": 1024
        }
        
        # Create test crawl result data
        crawl_result = {
            "data": [
                {
                    "html": "<html><body>Test content</body></html>",
                    "metadata": {"url": "https://example.com/page1"}
                },
                {
                    "html": "<html><body>More test content</body></html>",
                    "metadata": {"url": "https://example.com/page2"}
                }
            ]
        }
        
        # Call the function
        result = await process_and_upload_crawl_results(
            crawl_id="test-id",
            crawl_result=crawl_result,
            s3_uri="s3://bucket/path/"
        )
        
        # Verify results
        assert result["status"] == "completed"
        assert result["file_count"] == 2
        assert result["uploaded_files"] == 5  # From mock
        assert result["s3_uri"] == "s3://bucket/path/test-id/"


@pytest.mark.asyncio
async def test_check_crawl_status():
    """Test checking the status of a crawl job."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock FirecrawlApp
        with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
            mock_firecrawl = MagicMock()
            mock_firecrawl.check_crawl_status.return_value = {
                "status": "completed",
                "completed": 10,
                "total": 10
            }
            MockFirecrawlApp.return_value = mock_firecrawl
            
            # Call the function
            result = await check_crawl_status(mock_ctx, "test-id")
            
            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "completed"
            assert result["completed_urls"] == 10
            assert result["total_urls"] == 10


@pytest.mark.asyncio
async def test_invoke_firecrawl():
    """Test starting a new crawl job."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock asyncio.create_task to avoid starting the background task
    with patch('asyncio.create_task') as mock_create_task:
        # Mock environment variable
        with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
            # Mock FirecrawlApp
            with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
                mock_firecrawl = MagicMock()
                mock_firecrawl.async_crawl_url.return_value = {
                    "id": "test-id",
                    "status": "started"
                }
                MockFirecrawlApp.return_value = mock_firecrawl
                
                # Call the function
                result = await invoke_firecrawl(
                    ctx=mock_ctx,
                    url="https://example.com",
                    s3_uri="s3://bucket/path/",
                    limit=50
                )
                
                # Verify results
                assert result["id"] == "test-id"
                assert result["status"] == "started"
                assert result["s3_uri"] == "s3://bucket/path/test-id/"
                assert "message" in result
                
                # Verify background task was created
                mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_wait_for_crawl_completion():
    """Test waiting for crawl completion and processing results."""
    # Mock Context
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock the poll_crawl_until_complete function
        with patch('connectors.source.firecrawl.poll_crawl_until_complete') as mock_poll:
            # Mock the process_and_upload_crawl_results function
            with patch('connectors.source.firecrawl.process_and_upload_crawl_results') as mock_process:
                # Configure mocks
                mock_poll.return_value = {
                    "status": "completed",
                    "result": {"status": "completed", "completed": 5, "total": 5},
                    "elapsed_time": 10.5
                }
                
                mock_process.return_value = {
                    "status": "completed",
                    "file_count": 5,
                    "s3_uri": "s3://bucket/path/test-id/",
                    "uploaded_files": 5,
                    "failed_uploads": 0,
                    "upload_size_bytes": 1024
                }
                
                # Call the function
                result = await wait_for_crawl_completion(
                    ctx=mock_ctx,
                    crawl_id="test-id",
                    s3_uri="s3://bucket/path/",
                    poll_interval=0.1,
                    timeout=5
                )
                
                # Verify results
                assert result["id"] == "test-id"
                assert result["status"] == "completed"
                assert result["s3_uri"] == "s3://bucket/path/test-id/"
                assert result["file_count"] == 5
                assert result["uploaded_files"] == 5 