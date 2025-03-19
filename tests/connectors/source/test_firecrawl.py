import os
import pytest
import tempfile
import boto3
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

from connectors.source.firecrawl import (
    _ensure_valid_s3_uri,
    _upload_directory_to_s3,
    _invoke_firecrawl_job, 
    wait_for_job_completion,
    _check_job_status,
    _process_crawlhtml_results,
    _process_llmtxt_results,
    wait_for_crawlhtml_completion,
    invoke_firecrawl_crawlhtml,
    check_crawlhtml_status,
    invoke_firecrawl_llmtxt,
    check_llmtxt_status,
    JobType
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


@pytest.mark.asyncio
async def test_check_crawlhtml_status():
    """Test checking the status of a Firecrawl HTML crawl job."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock _check_job_status function
        with patch('connectors.source.firecrawl._check_job_status') as mock_check_job:
            mock_check_job.return_value = {
                "id": "test-id",
                "status": "completed",
                "completed_urls": 10,
                "total_urls": 10
            }
            
            # Call the function
            result = await check_crawlhtml_status(mock_ctx, "test-id")
            
            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "completed"
            assert result["completed_urls"] == 10
            assert result["total_urls"] == 10
            
            # Verify _check_job_status was called with the correct job type
            mock_check_job.assert_awaited_once_with(mock_ctx, "test-id", "crawlhtml")


@pytest.mark.asyncio
async def test_check_llmtxt_status():
    """Test checking the status of an LLM text generation job."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock _check_job_status function
        with patch('connectors.source.firecrawl._check_job_status') as mock_check_job:
            mock_check_job.return_value = {
                "id": "test-id",
                "status": "completed",
                "llmfulltxt": "Generated text content..."
            }
            
            # Call the function
            result = await check_llmtxt_status(mock_ctx, "test-id")
            
            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "completed"
            assert "llmfulltxt" in result
            
            # Verify _check_job_status was called with the correct job type
            mock_check_job.assert_awaited_once_with(mock_ctx, "test-id", "llmfulltxt")


@pytest.mark.asyncio
async def test_check_job_status_crawlhtml():
    """Test generic function for checking job status - crawlhtml type."""
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
            result = await _check_job_status(mock_ctx, "test-id", "crawlhtml")
            
            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "completed"
            assert result["completed_urls"] == 10
            assert result["total_urls"] == 10
            
            # Verify correct FirecrawlApp method was called
            mock_firecrawl.check_crawl_status.assert_called_once_with("test-id")


@pytest.mark.asyncio
async def test_check_job_status_llmtxt():
    """Test generic function for checking job status - llmtxt type."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock FirecrawlApp
        with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
            mock_firecrawl = MagicMock()
            mock_firecrawl.check_generate_llms_text_status.return_value = {
                "status": "completed", 
                "data": {
                    "llmsfulltxt": "Generated text content...",
                    "processedUrls": ["https://example.com/1", "https://example.com/2"]
                }
            }
            MockFirecrawlApp.return_value = mock_firecrawl
            
            # Call the function
            result = await _check_job_status(mock_ctx, "test-id", "llmfulltxt")
            
            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "completed"
            assert "llmfulltxt" in result
            assert result["llmfulltxt"] == "Generated text content..."
            
            # Verify correct FirecrawlApp method was called
            mock_firecrawl.check_generate_llms_text_status.assert_called_once_with("test-id")


@pytest.mark.asyncio
async def test_check_job_status_invalid_type():
    """Test generic function for checking job status with invalid job type."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Call the function with invalid job type
        result = await _check_job_status(mock_ctx, "test-id", "invalid_type")
        
        # Verify error response
        assert "error" in result
        assert "Unknown job type" in result["error"]


@pytest.mark.asyncio
async def test_invoke_firecrawl_crawlhtml():
    """Test starting a new HTML crawl job."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock _invoke_firecrawl_job function
    with patch('connectors.source.firecrawl._invoke_firecrawl_job') as mock_invoke:
        mock_invoke.return_value = {
            "id": "test-id",
            "status": "started",
            "s3_uri": "s3://bucket/path/test-id/",
            "message": "Firecrawl crawlhtml job started and will be automatically processed when complete"
        }
        
        # Call the function
        result = await invoke_firecrawl_crawlhtml(
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
        
        # Verify _invoke_firecrawl_job was called with the correct parameters
        mock_invoke.assert_awaited_once()
        args, kwargs = mock_invoke.call_args
        assert kwargs["ctx"] == mock_ctx
        assert kwargs["url"] == "https://example.com"
        assert kwargs["s3_uri"] == "s3://bucket/path/"
        assert kwargs["job_type"] == "crawlhtml"
        assert "limit" in kwargs["job_params"]
        assert kwargs["job_params"]["limit"] == 50


@pytest.mark.asyncio
async def test_invoke_firecrawl_llmtxt():
    """Test starting a new LLM text generation job."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock _invoke_firecrawl_job function
    with patch('connectors.source.firecrawl._invoke_firecrawl_job') as mock_invoke:
        mock_invoke.return_value = {
            "id": "test-id",
            "status": "started",
            "s3_uri": "s3://bucket/path/test-id/",
            "message": "Firecrawl llmtxt job started and will be automatically processed when complete"
        }
        
        # Call the function
        result = await invoke_firecrawl_llmtxt(
            ctx=mock_ctx,
            url="https://example.com",
            s3_uri="s3://bucket/path/",
            max_urls=20
        )
        
        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "started"
        assert result["s3_uri"] == "s3://bucket/path/test-id/"
        assert "message" in result
        
        # Verify _invoke_firecrawl_job was called with the correct parameters
        mock_invoke.assert_awaited_once()
        args, kwargs = mock_invoke.call_args
        assert kwargs["ctx"] == mock_ctx
        assert kwargs["url"] == "https://example.com"
        assert kwargs["s3_uri"] == "s3://bucket/path/"
        assert kwargs["job_type"] == "llmfulltxt"
        assert "maxUrls" in kwargs["job_params"]
        assert kwargs["job_params"]["maxUrls"] == 20
        assert "showFullText" in kwargs["job_params"]
        assert kwargs["job_params"]["showFullText"] == True


@pytest.mark.asyncio
async def test_invoke_firecrawl_job_crawlhtml():
    """Test generic function for starting a job - crawlhtml type."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock asyncio.create_task
    with patch('asyncio.create_task') as mock_create_task:
        # Mock environment variable
        with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
            # Mock FirecrawlApp
            with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
                mock_firecrawl = MagicMock()
                mock_firecrawl.async_crawl_url.return_value = {
                    "success": True,
                    "id": "test-id",
                    "status": "started"
                }
                MockFirecrawlApp.return_value = mock_firecrawl
                
                # Call the function
                result = await _invoke_firecrawl_job(
                    ctx=mock_ctx,
                    url="https://example.com",
                    s3_uri="s3://bucket/path/",
                    job_type="crawlhtml",
                    job_params={"limit": 50}
                )
                
                # Verify results
                assert result["id"] == "test-id"
                assert result["status"] == "started"
                assert result["s3_uri"] == "s3://bucket/path/test-id/"
                assert "message" in result
                
                # Verify correct FirecrawlApp method was called
                mock_firecrawl.async_crawl_url.assert_called_once()
                
                # Verify background task was created
                mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_invoke_firecrawl_job_llmtxt():
    """Test generic function for starting a job - llmtxt type."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock asyncio.create_task
    with patch('asyncio.create_task') as mock_create_task:
        # Mock environment variable
        with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
            # Mock FirecrawlApp
            with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
                mock_firecrawl = MagicMock()
                mock_firecrawl.async_generate_llms_text.return_value = {
                    "success": True,
                    "id": "test-id",
                    "status": "started"
                }
                MockFirecrawlApp.return_value = mock_firecrawl
                
                # Call the function
                result = await _invoke_firecrawl_job(
                    ctx=mock_ctx,
                    url="https://example.com",
                    s3_uri="s3://bucket/path/",
                    job_type="llmfulltxt",
                    job_params={"maxUrls": 20, "showFullText": True}
                )
                
                # Verify results
                assert result["id"] == "test-id"
                assert result["status"] == "started"
                assert result["s3_uri"] == "s3://bucket/path/test-id/"
                assert "message" in result
                
                # Verify correct FirecrawlApp method was called
                mock_firecrawl.async_generate_llms_text.assert_called_once()
                
                # Verify background task was created
                mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_invoke_firecrawl_job_invalid_type():
    """Test generic function for starting a job with invalid job type."""
    # Mock Context object
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Call the function with invalid job type
        result = await _invoke_firecrawl_job(
            ctx=mock_ctx,
            url="https://example.com",
            s3_uri="s3://bucket/path/",
            job_type="invalid_type",
            job_params={}
        )
        
        # Verify error response
        assert "error" in result
        assert "Unknown job type" in result["error"]


@pytest.mark.asyncio
async def test_wait_for_crawlhtml_completion():
    """Test waiting for HTML crawl completion using the specific function."""
    # Mock Context
    mock_ctx = MagicMock()
    
    # Mock wait_for_job_completion
    with patch('connectors.source.firecrawl.wait_for_job_completion') as mock_wait:
        mock_wait.return_value = {
            "id": "test-id",
            "status": "completed",
            "s3_uri": "s3://bucket/path/test-id/",
            "file_count": 5,
            "uploaded_files": 5,
            "failed_uploads": 0,
            "upload_size_bytes": 1024,
            "completed_urls": 5,
            "total_urls": 5,
            "elapsed_time": 10.5
        }
        
        # Call the function
        result = await wait_for_crawlhtml_completion(
            ctx=mock_ctx,
            crawl_id="test-id",
            s3_uri="s3://bucket/path/",
            poll_interval=30,
            timeout=3600
        )
        
        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "completed"
        assert result["s3_uri"] == "s3://bucket/path/test-id/"
        
        # Verify wait_for_job_completion was called with the correct parameters
        mock_wait.assert_awaited_once_with(
            mock_ctx, "test-id", "s3://bucket/path/", "crawlhtml", 30, 3600
        )


@pytest.mark.asyncio
async def test_wait_for_job_completion_crawlhtml():
    """Test waiting for job completion - crawlhtml type."""
    # Mock Context
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock FirecrawlApp
        with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
            # Configure mock for status checks
            mock_firecrawl = MagicMock()
            mock_firecrawl.check_crawl_status.side_effect = [
                {"status": "scraping"},
                {"status": "completed", "completed": 5, "total": 5}
            ]
            MockFirecrawlApp.return_value = mock_firecrawl
            
            # Mock the process functions - use AsyncMock for async function
            with patch('connectors.source.firecrawl._process_crawlhtml_results', new_callable=AsyncMock) as mock_process_crawl:
                with patch('connectors.source.firecrawl._upload_directory_to_s3') as mock_upload:
                    # Configure mocks
                    mock_process_crawl.return_value = 5
                    mock_upload.return_value = {
                        "uploaded_files": 5,
                        "failed_files": 0,
                        "total_bytes": 1024
                    }
                    
                    # Call the function with minimal poll interval for testing
                    result = await wait_for_job_completion(
                        ctx=mock_ctx,
                        job_id="test-id",
                        s3_uri="s3://bucket/path/",
                        job_type="crawlhtml",
                        poll_interval=0.1,
                        timeout=5
                    )
                    
                    # Verify results
                    assert result["id"] == "test-id"
                    assert result["status"] == "completed"
                    assert result["s3_uri"] == "s3://bucket/path/test-id/"
                    assert result["file_count"] == 5
                    assert result["uploaded_files"] == 5
                    assert "completed_urls" in result
                    assert "total_urls" in result
                    
                    # Verify process function was called
                    mock_process_crawl.assert_awaited_once()
                    mock_upload.assert_called_once()


@pytest.mark.asyncio
async def test_wait_for_job_completion_llmtxt():
    """Test waiting for job completion - llmtxt type."""
    # Mock Context
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock FirecrawlApp
        with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
            # Configure mock for status checks
            mock_firecrawl = MagicMock()
            mock_firecrawl.check_generate_llms_text_status.side_effect = [
                {"status": "processing"},
                {
                    "status": "completed", 
                    "data": {
                        "llmsfulltxt": "Generated text content...",
                        "processedUrls": ["https://example.com/1", "https://example.com/2"]
                    }
                }
            ]
            MockFirecrawlApp.return_value = mock_firecrawl
            
            # Mock the process functions
            with patch('connectors.source.firecrawl._process_llmtxt_results') as mock_process_llms:
                with patch('connectors.source.firecrawl._upload_directory_to_s3') as mock_upload:
                    # Configure mocks
                    mock_process_llms.return_value = 1
                    mock_upload.return_value = {
                        "uploaded_files": 1,
                        "failed_files": 0,
                        "total_bytes": 512
                    }
                    
                    # Call the function with minimal poll interval for testing
                    result = await wait_for_job_completion(
                        ctx=mock_ctx,
                        job_id="test-id",
                        s3_uri="s3://bucket/path/",
                        job_type="llmfulltxt",
                        poll_interval=0.1,
                        timeout=5
                    )
                    
                    # Verify results
                    assert result["id"] == "test-id"
                    assert result["status"] == "completed"
                    assert result["s3_uri"] == "s3://bucket/path/test-id/"
                    assert result["file_count"] == 1
                    assert result["uploaded_files"] == 1
                    assert "processed_urls_count" in result
                    
                    # Verify process function was called
                    mock_process_llms.assert_called_once()
                    mock_upload.assert_called_once()


@pytest.mark.asyncio
async def test_wait_for_job_completion_timeout():
    """Test that waiting for job completion times out correctly."""
    # Mock Context
    mock_ctx = MagicMock()
    
    # Mock environment variable
    with patch.dict(os.environ, {'FIRECRAWL_API_KEY': 'test-key'}):
        # Mock FirecrawlApp
        with patch('connectors.source.firecrawl.FirecrawlApp') as MockFirecrawlApp:
            # Configure mock to always return "in progress" status
            mock_firecrawl = MagicMock()
            mock_firecrawl.check_crawl_status.return_value = {"status": "scraping"}
            MockFirecrawlApp.return_value = mock_firecrawl
            
            # Call the function with very short timeout
            result = await wait_for_job_completion(
                ctx=mock_ctx,
                job_id="test-id",
                s3_uri="s3://bucket/path/",
                job_type="crawlhtml",
                poll_interval=0.1,
                timeout=0.3  # Very short timeout for testing
            )
            
            # Verify timeout was detected
            assert result["id"] == "test-id"
            assert result["status"] == "timeout"
            assert "error" in result
            assert "Timeout waiting for" in result["error"]


def test_process_llmtxt_results():
    """Test processing LLM text generation results."""
    # Create test result data
    llms_result = {
        "data": {
            "llmsfulltxt": "This is generated text content for testing..."
        }
    }
    
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call the function
        file_count = _process_llmtxt_results("test-id", llms_result, temp_dir)
        
        # Verify results
        assert file_count == 1
        
        # Verify file was created
        llmtxt_path = os.path.join(temp_dir, "llmfull.txt")
        assert os.path.exists(llmtxt_path)
        
        # Verify file contents
        with open(llmtxt_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert content == "This is generated text content for testing..." 