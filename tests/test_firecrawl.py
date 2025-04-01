import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from uns_mcp.connectors.external.firecrawl import (
    _cancel_job,
    _check_job_status,
    _ensure_valid_s3_uri,
    _invoke_firecrawl_job,
    _process_llmtxt_results,
    _upload_directory_to_s3,
    cancel_crawlhtml_job,
    cancel_llmtxt_job,
    check_crawlhtml_status,
    check_llmtxt_status,
    invoke_firecrawl_crawlhtml,
    invoke_firecrawl_llmtxt,
    wait_for_crawlhtml_completion,
    wait_for_job_completion,
)


# Moved from conftest.py - Environment fixture
@pytest.fixture()
def mock_environment():
    """Fixture to set up environment variables for testing."""
    original_env = os.environ.copy()
    test_env = {
        "FIRECRAWL_API_KEY": "test-api-key",
        "AWS_KEY": "test-aws-key",
        "AWS_SECRET": "test-aws-secret",
    }

    # Add the test environment variables
    for key, value in test_env.items():
        os.environ[key] = value

    yield test_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Mock S3 client for testing uploads
@pytest.fixture()
def mock_s3_client():
    """Create a mock of boto3 S3 client."""
    with patch("boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3


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


# Test _upload_directory_to_s3
def test_upload_directory_to_s3(mock_s3_client, mock_environment):
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

        # Call the function (mock_environment fixture already sets up the environment variables)
        s3_uri = "s3://test-bucket/prefix/"
        result = _upload_directory_to_s3(temp_dir, s3_uri)

        # Verify S3 client was called correctly
        assert mock_s3_client.upload_file.call_count == 2

        # Verify result statistics
        assert result["uploaded_files"] == 2
        assert result["failed_files"] == 0
        assert result["total_bytes"] > 0


def test_upload_directory_to_s3_with_errors(mock_s3_client, mock_environment):
    """Test handling errors during S3 upload."""
    # Setup mock to raise an exception on upload
    mock_s3_client.upload_file.side_effect = Exception("Mock S3 error")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")

        # Call the function (mock_environment fixture already sets up the environment variables)
        s3_uri = "s3://test-bucket/prefix/"
        result = _upload_directory_to_s3(temp_dir, s3_uri)

        # Verify result statistics reflect the failure
        assert result["uploaded_files"] == 0
        assert result["failed_files"] == 1


@pytest.mark.asyncio()
async def test_check_crawlhtml_status(mock_environment):
    """Test checking the status of a Firecrawl HTML crawl job."""
    # Mock _check_job_status function
    with patch("uns_mcp.connectors.external.firecrawl._check_job_status") as mock_check_job:
        mock_check_job.return_value = {
            "id": "test-id",
            "status": "completed",
            "completed_urls": 10,
            "total_urls": 10,
        }

        # Call the function
        result = await check_crawlhtml_status("test-id")

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "completed"
        assert result["completed_urls"] == 10
        assert result["total_urls"] == 10

        # Verify _check_job_status was called with the correct job type
        mock_check_job.assert_awaited_once_with("test-id", "crawlhtml")


@pytest.mark.asyncio()
async def test_check_llmtxt_status(mock_environment):
    """Test checking the status of an LLM text generation job."""
    # Mock _check_job_status function
    with patch("uns_mcp.connectors.external.firecrawl._check_job_status") as mock_check_job:
        mock_check_job.return_value = {
            "id": "test-id",
            "status": "completed",
            "llmfulltxt": "Generated text content...",
        }

        # Call the function
        result = await check_llmtxt_status("test-id")

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "completed"
        assert "llmfulltxt" in result

        # Verify _check_job_status was called with the correct job type
        mock_check_job.assert_awaited_once_with("test-id", "llmfulltxt")


@pytest.mark.asyncio()
async def test_check_job_status_crawlhtml(mock_environment):
    """Test generic function for checking job status - crawlhtml type."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.check_crawl_status.return_value = {
            "status": "completed",
            "completed": 10,
            "total": 10,
        }
        MockFirecrawlApp.return_value = mock_firecrawl

        # Call the function
        result = await _check_job_status("test-id", "crawlhtml")

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "completed"
        assert result["completed_urls"] == 10
        assert result["total_urls"] == 10

        # Verify correct FirecrawlApp method was called
        mock_firecrawl.check_crawl_status.assert_called_once_with("test-id")


@pytest.mark.asyncio()
async def test_check_job_status_llmtxt(mock_environment):
    """Test generic function for checking job status - llmtxt type."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.check_generate_llms_text_status.return_value = {
            "status": "completed",
            "data": {
                "llmsfulltxt": "Generated text content...",
                "processedUrls": ["https://example.com/1", "https://example.com/2"],
            },
        }
        MockFirecrawlApp.return_value = mock_firecrawl

        # Call the function
        result = await _check_job_status("test-id", "llmfulltxt")

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "completed"
        assert "llmfulltxt" in result
        assert result["llmfulltxt"] == "Generated text content..."

        # Verify correct FirecrawlApp method was called
        mock_firecrawl.check_generate_llms_text_status.assert_called_once_with("test-id")


@pytest.mark.asyncio()
async def test_check_job_status_invalid_type(mock_environment):
    """Test generic function for checking job status with invalid job type."""
    # Call the function with invalid job type
    result = await _check_job_status("test-id", "invalid_type")

    # Verify error response
    assert "error" in result
    assert "Unknown job type" in result["error"]


@pytest.mark.asyncio()
async def test_invoke_firecrawl_crawlhtml(mock_environment):
    """Test invoking a Firecrawl HTML crawl job."""
    # Mock _invoke_firecrawl_job
    with patch("uns_mcp.connectors.external.firecrawl._invoke_firecrawl_job") as mock_invoke:
        mock_invoke.return_value = {
            "id": "test-id",
            "status": "started",
            "s3_uri": "s3://test-bucket/test-id/",
            "message": "Firecrawl crawlhtml job started and will be automatically "
            "processed when complete",
        }

        # Call the function
        result = await invoke_firecrawl_crawlhtml(
            url="https://example.com",
            s3_uri="s3://test-bucket/",
        )

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "started"
        assert result["s3_uri"] == "s3://test-bucket/test-id/"

        # Verify _invoke_firecrawl_job was called with the correct parameters
        mock_invoke.assert_awaited_once()
        call_args = mock_invoke.call_args[1]
        assert call_args["url"] == "https://example.com"
        assert call_args["s3_uri"] == "s3://test-bucket/"
        assert call_args["job_type"] == "crawlhtml"
        assert "limit" in call_args["job_params"]
        assert call_args["job_params"]["limit"] == 100


@pytest.mark.asyncio()
async def test_invoke_firecrawl_llmtxt(mock_environment):
    """Test invoking an LLM text generation job."""
    # Mock _invoke_firecrawl_job
    with patch("uns_mcp.connectors.external.firecrawl._invoke_firecrawl_job") as mock_invoke:
        mock_invoke.return_value = {
            "id": "test-id",
            "status": "started",
            "s3_uri": "s3://test-bucket/test-id/",
            "message": "Firecrawl llmfulltxt job started and will be automatically '"
            "processed when complete",
        }

        # Call the function
        result = await invoke_firecrawl_llmtxt(
            url="https://example.com",
            s3_uri="s3://test-bucket/",
            max_urls=5,
        )

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "started"
        assert result["s3_uri"] == "s3://test-bucket/test-id/"

        # Verify _invoke_firecrawl_job was called with the correct parameters
        mock_invoke.assert_awaited_once()
        call_args = mock_invoke.call_args[1]
        assert call_args["url"] == "https://example.com"
        assert call_args["s3_uri"] == "s3://test-bucket/"
        assert call_args["job_type"] == "llmfulltxt"
        assert "maxUrls" in call_args["job_params"]
        assert call_args["job_params"]["maxUrls"] == 5
        assert call_args["job_params"]["showFullText"] is False


@pytest.mark.asyncio()
async def test_invoke_firecrawl_job_crawlhtml(mock_environment):
    """Test generic function for invoking a Firecrawl job - crawlhtml type."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.async_crawl_url.return_value = {"id": "test-id", "status": "started"}
        MockFirecrawlApp.return_value = mock_firecrawl

        # Mock asyncio.create_task
        with patch("asyncio.create_task") as mock_create_task:
            # Call the function
            result = await _invoke_firecrawl_job(
                url="https://example.com",
                s3_uri="s3://test-bucket/",
                job_type="crawlhtml",
                job_params={"limit": 100},
            )

            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "started"
            assert result["s3_uri"] == "s3://test-bucket/test-id/"

            # Verify correct FirecrawlApp method was called
            mock_firecrawl.async_crawl_url.assert_called_once_with(
                "https://example.com",
                params={"limit": 100},
            )

            # Verify background task was created
            mock_create_task.assert_called_once()


@pytest.mark.asyncio()
async def test_invoke_firecrawl_job_llmtxt(mock_environment):
    """Test generic function for invoking a Firecrawl job - llmtxt type."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.async_generate_llms_text.return_value = {
            "id": "test-id",
            "status": "started",
        }
        MockFirecrawlApp.return_value = mock_firecrawl

        # Mock asyncio.create_task
        with patch("asyncio.create_task") as mock_create_task:
            # Call the function
            result = await _invoke_firecrawl_job(
                url="https://example.com",
                s3_uri="s3://test-bucket/",
                job_type="llmfulltxt",
                job_params={"maxUrls": 5, "showFullText": True},
            )

            # Verify results
            assert result["id"] == "test-id"
            assert result["status"] == "started"
            assert result["s3_uri"] == "s3://test-bucket/test-id/"

            # Verify correct FirecrawlApp method was called
            mock_firecrawl.async_generate_llms_text.assert_called_once_with(
                "https://example.com",
                params={"maxUrls": 5, "showFullText": True},
            )

            # Verify background task was created
            mock_create_task.assert_called_once()


@pytest.mark.asyncio()
async def test_invoke_firecrawl_job_invalid_type(mock_environment):
    """Test generic function for invoking a Firecrawl job with invalid job type."""
    # Call the function with invalid job type
    result = await _invoke_firecrawl_job(
        url="https://example.com",
        s3_uri="s3://test-bucket/",
        job_type="invalid_type",
        job_params={},
    )

    # Verify error response
    assert "error" in result
    assert "Unknown job type" in result["error"]


@pytest.mark.asyncio()
async def test_wait_for_crawlhtml_completion(mock_environment):
    """Test waiting for a Firecrawl HTML crawl job to complete."""
    # Mock wait_for_job_completion function
    with patch("uns_mcp.connectors.external.firecrawl.wait_for_job_completion") as mock_wait:
        mock_wait.return_value = {
            "id": "test-id",
            "status": "completed",
            "s3_uri": "s3://test-bucket/test-id/",
            "file_count": 10,
            "uploaded_files": 10,
            "failed_uploads": 0,
            "upload_size_bytes": 1000,
            "elapsed_time": 60,
            "completed_urls": 10,
            "total_urls": 10,
        }

        # Call the function
        result = await wait_for_crawlhtml_completion(
            crawl_id="test-id",
            s3_uri="s3://test-bucket/",
            poll_interval=10,
            timeout=300,
        )

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "completed"
        assert result["s3_uri"] == "s3://test-bucket/test-id/"

        # Verify wait_for_job_completion was called with the correct parameters
        mock_wait.assert_awaited_once_with("test-id", "s3://test-bucket/", "crawlhtml", 10, 300)


@pytest.mark.asyncio()
async def test_wait_for_job_completion_crawlhtml(mock_environment):
    """Test waiting for a job to complete - crawlhtml type."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.check_crawl_status.return_value = {
            "status": "completed",
            "completed": 10,
            "total": 10,
            "data": [
                {
                    "html": "<html><body>Test</body></html>",
                    "metadata": {"url": "https://example.com/1"},
                },
                {
                    "html": "<html><body>Test 2</body></html>",
                    "metadata": {"url": "https://example.com/2"},
                },
            ],
        }
        MockFirecrawlApp.return_value = mock_firecrawl

        # Mock _process_crawlhtml_results
        with patch(
            "uns_mcp.connectors.external.firecrawl._process_crawlhtml_results",
        ) as mock_process:
            mock_process.return_value = 2

            # Mock _upload_directory_to_s3
            with patch(
                "uns_mcp.connectors.external.firecrawl._upload_directory_to_s3",
            ) as mock_upload:
                mock_upload.return_value = {
                    "uploaded_files": 2,
                    "failed_files": 0,
                    "total_bytes": 1000,
                }

                # Mock asyncio.sleep to avoid actual waiting
                with patch("asyncio.sleep"):
                    # Call the function
                    result = await wait_for_job_completion(
                        job_id="test-id",
                        s3_uri="s3://test-bucket/",
                        job_type="crawlhtml",
                        poll_interval=1,
                        timeout=10,
                    )

                    # Verify results
                    assert result["id"] == "test-id"
                    assert result["status"] == "completed"
                    assert result["s3_uri"] == "s3://test-bucket/test-id/"
                    assert result["file_count"] == 2
                    assert result["uploaded_files"] == 2
                    assert result["failed_uploads"] == 0
                    assert result["upload_size_bytes"] == 1000
                    assert "elapsed_time" in result
                    assert result["completed_urls"] == 10
                    assert result["total_urls"] == 10


@pytest.mark.asyncio()
async def test_wait_for_job_completion_llmtxt(mock_environment):
    """Test waiting for a job to complete - llmtxt type."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.check_generate_llms_text_status.return_value = {
            "status": "completed",
            "data": {
                "llmsfulltxt": "Generated text content...",
                "processedUrls": ["https://example.com/1", "https://example.com/2"],
            },
        }
        MockFirecrawlApp.return_value = mock_firecrawl

        # Mock _process_llmtxt_results
        with patch("uns_mcp.connectors.external.firecrawl._process_llmtxt_results") as mock_process:
            mock_process.return_value = 1

            # Mock _upload_directory_to_s3
            with patch(
                "uns_mcp.connectors.external.firecrawl._upload_directory_to_s3",
            ) as mock_upload:
                mock_upload.return_value = {
                    "uploaded_files": 1,
                    "failed_files": 0,
                    "total_bytes": 500,
                }

                # Mock asyncio.sleep to avoid actual waiting
                with patch("asyncio.sleep"):
                    # Call the function
                    result = await wait_for_job_completion(
                        job_id="test-id",
                        s3_uri="s3://test-bucket/",
                        job_type="llmfulltxt",
                        poll_interval=1,
                        timeout=10,
                    )

                    # Verify results
                    assert result["id"] == "test-id"
                    assert result["status"] == "completed"
                    assert result["s3_uri"] == "s3://test-bucket/test-id/"
                    assert result["file_count"] == 1
                    assert result["uploaded_files"] == 1
                    assert result["failed_uploads"] == 0
                    assert result["upload_size_bytes"] == 500
                    assert "elapsed_time" in result
                    assert result["processed_urls_count"] == 2


@pytest.mark.asyncio()
async def test_wait_for_job_completion_timeout(mock_environment):
    """Test timeout while waiting for a job to complete."""
    # Mock FirecrawlApp
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        # Return a non-completed status
        mock_firecrawl.check_crawl_status.return_value = {
            "status": "in_progress",
            "completed": 5,
            "total": 10,
        }
        MockFirecrawlApp.return_value = mock_firecrawl

        # Mock time to force timeout
        with patch("time.time") as mock_time:
            # First call is for start time, subsequent calls for checking timeout
            mock_time.side_effect = [0, 20, 20]  # Ensure we exceed the timeout value of 10

            # Mock asyncio.sleep to avoid actual waiting
            with patch("asyncio.sleep"):
                # Call the function with a short timeout
                result = await wait_for_job_completion(
                    job_id="test-id",
                    s3_uri="s3://test-bucket/",
                    job_type="crawlhtml",
                    poll_interval=1,
                    timeout=10,  # 10 seconds timeout
                )

                # Verify timeout results
                assert "id" in result
                assert "status" in result
                assert result["status"] == "timeout"
                assert "error" in result
                assert "Timeout waiting for" in result["error"]
                assert "elapsed_time" in result


@pytest.mark.asyncio()
async def test_cancel_crawlhtml_job(mock_environment):
    """Test cancelling a Firecrawl HTML crawl job."""
    # Mock _cancel_job function
    with patch("uns_mcp.connectors.external.firecrawl._cancel_job") as mock_cancel_job:
        mock_cancel_job.return_value = {
            "id": "test-id",
            "status": "cancelled",
            "message": "Firecrawl crawlhtml job cancelled successfully",
            "details": {"status": "cancelled"},
        }

        # Call the function
        result = await cancel_crawlhtml_job("test-id")

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "cancelled"
        assert "message" in result

        # Verify _cancel_job was called with the correct job type
        mock_cancel_job.assert_awaited_once_with("test-id", "crawlhtml")


@pytest.mark.asyncio()
async def test_cancel_llmtxt_job(mock_environment):
    """Test cancelling an LLM text generation job."""
    # Mock _cancel_job function
    with patch("uns_mcp.connectors.external.firecrawl._cancel_job") as mock_cancel_job:
        mock_cancel_job.return_value = {
            "id": "test-id",
            "status": "error",
            "message": "Cancelling LLM text generation jobs is not supported.",
            "details": {"status": "error", "reason": "unsupported_operation"},
        }

        # Call the function
        result = await cancel_llmtxt_job("test-id")

        # Verify results
        assert result["id"] == "test-id"
        assert result["status"] == "error"
        assert "not supported" in result["message"]

        # Verify _cancel_job was called with the correct job type
        mock_cancel_job.assert_awaited_once_with("test-id", "llmfulltxt")


@pytest.mark.asyncio()
async def test_cancel_job_failure(mock_environment):
    """Test handling errors when cancelling a job."""
    # Mock FirecrawlApp to raise an exception
    with patch("uns_mcp.connectors.external.firecrawl.FirecrawlApp") as MockFirecrawlApp:
        mock_firecrawl = MagicMock()
        mock_firecrawl.cancel_crawl.side_effect = Exception("Test exception")
        MockFirecrawlApp.return_value = mock_firecrawl

        # Call the function
        result = await _cancel_job("test-id", "crawlhtml")

        # Verify error response
        assert "error" in result
        assert "Error cancelling crawlhtml job" in result["error"]


def test_process_llmtxt_results():
    """Test processing LLM text generation results."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test data
        result = {"data": {"llmsfulltxt": "This is the generated LLM text content for test."}}

        # Call the function
        file_count = _process_llmtxt_results(result, temp_dir)

        # Verify output file was created
        llmtxt_file = os.path.join(temp_dir, "llmfull.txt")
        assert os.path.exists(llmtxt_file)

        # Verify content of the file
        with open(llmtxt_file) as f:
            content = f.read()
            assert content == "This is the generated LLM text content for test."

        # Verify file count
        assert file_count == 1

        # Test with missing data
        file_count = _process_llmtxt_results({}, temp_dir)
        assert file_count == 0
