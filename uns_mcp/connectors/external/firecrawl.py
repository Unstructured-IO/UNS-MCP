import asyncio
import hashlib
import os
import tempfile
import time
from typing import Any, Dict, Literal

import boto3

# Import the FirecrawlApp client
from firecrawl import FirecrawlApp

# Define job types
Firecrawl_JobType = Literal["crawlhtml", "llmfulltxt"]


def _prepare_firecrawl_config() -> Dict[str, str]:
    """Prepare the Firecrawl configuration by retrieving and validating the API key.

    Returns:
        A dictionary containing either an API key or an error message
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")

    if not api_key:
        return {
            "error": "Firecrawl API key is required. Set FIRECRAWL_API_KEY environment variable.",
        }

    return {"api_key": api_key}


def _ensure_valid_s3_uri(s3_uri: str) -> str:
    """Ensure S3 URI is properly formatted.

    Args:
        s3_uri: S3 URI to validate

    Returns:
        Properly formatted S3 URI

    Raises:
        ValueError: If S3 URI doesn't start with 's3://'
    """
    if not s3_uri:
        raise ValueError("S3 URI is required")

    if not s3_uri.startswith("s3://"):
        raise ValueError("S3 URI must start with 's3://'")

    # Ensure URI ends with a slash
    if not s3_uri.endswith("/"):
        s3_uri += "/"

    return s3_uri


async def invoke_firecrawl_crawlhtml(
    url: str,
    s3_uri: str,
    limit: int = 100,
) -> Dict[str, Any]:
    """Start an asynchronous web crawl job using Firecrawl to retrieve HTML content.

    Args:
        url: URL to crawl
        s3_uri: S3 URI where results will be uploaded
        limit: Maximum number of pages to crawl (default: 100)

    Returns:
        Dictionary with crawl job information including the job ID
    """
    # Call the generic invoke function with crawl-specific parameters
    params = {
        "limit": limit,
        "scrapeOptions": {
            "formats": ["html"],  # Only use HTML format TODO: Bring in other features of this API
        },
    }

    return await _invoke_firecrawl_job(
        url=url,
        s3_uri=s3_uri,
        job_type="crawlhtml",
        job_params=params,
    )


async def invoke_firecrawl_llmtxt(
    url: str,
    s3_uri: str,
    max_urls: int = 10,
) -> Dict[str, Any]:
    """Start an asynchronous llmfull.txt generation job using Firecrawl.
    This file is a standardized markdown file containing information to help LLMs
    use a website at inference time.
    The llmstxt endpoint leverages Firecrawl to crawl your website and extracts data
    using gpt-4o-mini
    Args:
        url: URL to crawl
        s3_uri: S3 URI where results will be uploaded
        max_urls: Maximum number of pages to crawl (1-100, default: 10)

    Returns:
        Dictionary with job information including the job ID
    """
    # Call the generic invoke function with llmfull.txt-specific parameters
    params = {"maxUrls": max_urls, "showFullText": False}

    return await _invoke_firecrawl_job(
        url=url,
        s3_uri=s3_uri,
        job_type="llmfulltxt",
        job_params=params,
    )


async def _invoke_firecrawl_job(
    url: str,
    s3_uri: str,
    job_type: Firecrawl_JobType,
    job_params: Dict[str, Any],
) -> Dict[str, Any]:
    """Generic function to start a Firecrawl job (either HTML crawl or llmfull.txt generation).

    Args:
        url: URL to process
        s3_uri: S3 URI where results will be uploaded
        job_type: Type of job ('crawlhtml' or 'llmtxt')
        job_params: Parameters specific to the job type

    Returns:
        Dictionary with job information including the job ID
    """
    # Get configuration with API key
    config = _prepare_firecrawl_config()

    # Check if config contains an error
    if "error" in config:
        return {"error": config["error"]}

    # Validate and normalize S3 URI first -
    # doing this outside the try block to handle validation errors specifically
    try:
        validated_s3_uri = _ensure_valid_s3_uri(s3_uri)
    except ValueError as ve:
        return {"error": f"Invalid S3 URI: {str(ve)}"}

    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=config["api_key"])

        # Start the job based on job_type
        if job_type == "crawlhtml":
            job_status = firecrawl.async_crawl_url(url, params=job_params)

        elif job_type == "llmfulltxt":
            job_status = firecrawl.async_generate_llms_text(url, params=job_params)
        else:
            return {"error": f"Unknown job type: {job_type}"}

        # Handle the response
        if "id" in job_status:
            job_id = job_status["id"]

            # Start background task without waiting for it
            asyncio.create_task(wait_for_job_completion(job_id, validated_s3_uri, job_type))

            # Prepare and return the response
            response = {
                "id": job_id,
                "status": job_status.get("status", "started"),
                "s3_uri": f"{validated_s3_uri}{job_id}/",
                "message": f"Firecrawl {job_type} job started "
                f"and will be auto-processed when complete",
            }

            return response
        else:
            return {"error": f"Failed to start Firecrawl {job_type} job", "details": job_status}

    except Exception as e:
        return {"error": f"Error starting Firecrawl {job_type} job: {str(e)}"}


async def check_crawlhtml_status(
    crawl_id: str,
) -> Dict[str, Any]:
    """Check the status of an existing Firecrawl HTML crawl job.

    Args:
        crawl_id: ID of the crawl job to check

    Returns:
        Dictionary containing the current status of the crawl job
    """
    return await _check_job_status(crawl_id, "crawlhtml")


async def check_llmtxt_status(
    job_id: str,
) -> Dict[str, Any]:
    """Check the status of an existing llmfull.txt generation job.

    Args:
        job_id: ID of the llmfull.txt generation job to check

    Returns:
        Dictionary containing the current status of the job and text content if completed
    """
    return await _check_job_status(job_id, "llmfulltxt")


async def _check_job_status(
    job_id: str,
    job_type: Firecrawl_JobType,
) -> Dict[str, Any]:
    """Generic function to check the status of a Firecrawl job.

    Args:
        job_id: ID of the job to check
        job_type: Type of job ('crawlhtml' or 'llmtxt')

    Returns:
        Dictionary containing the current status of the job
    """
    # Get configuration with API key
    config = _prepare_firecrawl_config()

    # Check if config contains an error
    if "error" in config:
        return {"error": config["error"]}

    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=config["api_key"])

        # Check status based on job type
        if job_type == "crawlhtml":
            result = firecrawl.check_crawl_status(job_id)

            # Return a more user-friendly response for crawl jobs
            status_info = {
                "id": job_id,
                "status": result.get("status", "unknown"),
                "completed_urls": result.get("completed", 0),
                "total_urls": result.get("total", 0),
            }

        elif job_type == "llmfulltxt":
            result = firecrawl.check_generate_llms_text_status(job_id)

            # Return a more user-friendly response for llmfull.txt jobs
            status_info = {
                "id": job_id,
                "status": result.get("status", "unknown"),
            }

            # Add llmfull.txt content if job is completed
            if result.get("status") == "completed" and "data" in result:
                status_info["llmfulltxt"] = result["data"].get("llmsfulltxt", "")

        else:
            return {"error": f"Unknown job type: {job_type}"}

        return status_info
    except Exception as e:
        return {"error": f"Error checking {job_type} status: {str(e)}"}


def _upload_directory_to_s3(local_dir: str, s3_uri: str) -> Dict[str, Any]:
    """Upload a directory to S3.

    Args:
        local_dir: Local directory to upload
        s3_uri: S3 URI to upload to (already validated)

    Returns:
        Dict with upload stats
    """
    # Parse the S3 URI to get bucket and prefix (assume already validated)
    # Remove s3:// prefix and split by first /
    uri_parts = s3_uri[5:].split("/", 1)
    bucket_name = uri_parts[0]
    prefix = uri_parts[1] if len(uri_parts) > 1 else ""

    # Initialize boto3 S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_KEY"),
        aws_secret_access_key=os.environ.get("AWS_SECRET"),
    )

    # Track upload stats
    stats = {"uploaded_files": 0, "failed_files": 0, "total_bytes": 0}

    # Walk through the directory
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)

            # Determine the S3 key (path within the bucket)
            # Remove the local_dir prefix from the file path to get relative path
            relative_path = os.path.relpath(local_path, local_dir)

            # Create the S3 key by joining the prefix with the relative path
            # Replace backslashes with forward slashes for S3
            s3_key = os.path.join(prefix, relative_path).replace("\\", "/")

            try:
                # Upload the file
                s3_client.upload_file(local_path, bucket_name, s3_key)

                # Update stats
                stats["uploaded_files"] += 1
                stats["total_bytes"] += os.path.getsize(local_path)
            except Exception as e:
                print(f"Error uploading {local_path}: {str(e)}")
                stats["failed_files"] += 1

    return stats


async def wait_for_crawlhtml_completion(
    crawl_id: str,
    s3_uri: str,
    poll_interval: int = 30,
    timeout: int = 3600,
) -> Dict[str, Any]:
    """Poll a Firecrawl HTML crawl job until completion and upload results to S3.

    Args:
        crawl_id: ID of the crawl job to monitor
        s3_uri: S3 URI where results will be uploaded (already validated)
        poll_interval: How often to check job status in seconds (default: 30)
        timeout: Maximum time to wait in seconds (default: 1 hour)

    Returns:
        Dictionary with information about the completed job and S3 URI
    """
    return await wait_for_job_completion(crawl_id, s3_uri, "crawlhtml", poll_interval, timeout)


async def wait_for_job_completion(
    job_id: str,
    s3_uri: str,
    job_type: Firecrawl_JobType,
    poll_interval: int = 30,
    timeout: int = 3600,
) -> Dict[str, Any]:
    """Poll a Firecrawl job until completion and upload results to S3.

    Args:
        job_id: ID of the job to monitor
        s3_uri: S3 URI where results will be uploaded (already validated)
        job_type: Type of job ('crawlhtml' or 'llmtxt')
        poll_interval: How often to check job status in seconds (default: 30)
        timeout: Maximum time to wait in seconds (default: 1 hour)

    Returns:
        Dictionary with information about the completed job and S3 URI
    """
    # Get configuration with API key
    config = _prepare_firecrawl_config()

    # Check if config contains an error
    if "error" in config:
        return {"error": config["error"]}

    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=config["api_key"])
        start_time = time.time()

        # Poll until completion or timeout
        while True:
            # Check status based on job type
            if job_type == "crawlhtml":
                result = firecrawl.check_crawl_status(job_id)
            elif job_type == "llmfulltxt":
                result = firecrawl.check_generate_llms_text_status(job_id)
            else:
                return {"error": f"Unknown job type: {job_type}", "id": job_id}

            # Check if job is completed
            if result.get("status") == "completed":
                break

            # Check for timeout
            if time.time() - start_time > timeout:
                return {
                    "id": job_id,
                    "status": "timeout",
                    "error": f"Timeout waiting for {job_type} job {job_id} to complete",
                    "elapsed_time": time.time() - start_time,
                }

            # Wait before polling again
            await asyncio.sleep(poll_interval)

        # Job completed - process results based on job type
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a job-specific subdirectory
            job_dir = os.path.join(temp_dir, job_id)
            os.makedirs(job_dir, exist_ok=True)

            # Process results based on job type
            if job_type == "crawlhtml":
                file_count = await _process_crawlhtml_results(result, job_dir)
            elif job_type == "llmfulltxt":
                file_count = _process_llmtxt_results(result, job_dir)
            else:
                return {"error": f"Unknown job type: {job_type}", "id": job_id}

            # Upload to S3
            final_s3_uri = f"{s3_uri}{job_id}/"
            upload_stats = _upload_directory_to_s3(job_dir, final_s3_uri)

            # Return combined results
            response = {
                "id": job_id,
                "status": "completed",
                "s3_uri": final_s3_uri,
                "file_count": file_count,
                "uploaded_files": upload_stats["uploaded_files"],
                "failed_uploads": upload_stats["failed_files"],
                "upload_size_bytes": upload_stats["total_bytes"],
                "elapsed_time": time.time() - start_time,
            }

            # Add job-type specific information
            if job_type == "crawlhtml":
                response.update(
                    {
                        "completed_urls": result.get("completed", 0),
                        "total_urls": result.get("total", 0),
                    },
                )
            elif job_type == "llmfulltxt" and "data" in result:
                response.update(
                    {
                        "processed_urls_count": len(result["data"].get("processedUrls", [])),
                    },
                )

            return response

    except Exception as e:
        return {"error": f"Error in wait_for_{job_type}_completion: {str(e)}", "id": job_id}


async def _process_crawlhtml_results(crawl_result: Dict[str, Any], output_dir: str) -> int:
    """Process HTML crawl results by saving HTML files.

    Args:
        crawl_result: The result from the completed crawl
        output_dir: Directory where to save the files

    Returns:
        Number of files created
    """
    file_paths = []

    # Process crawl_result['data'], which is a list of dicts, each with an 'html' key
    if "data" in crawl_result and isinstance(crawl_result["data"], list):
        for i, page_data in enumerate(crawl_result["data"]):
            # Skip if no HTML content
            if "html" not in page_data:
                continue

            # Get the URL from metadata if available, otherwise use index
            url = page_data.get("metadata", {}).get("url", f"page-{i}")
            content = page_data.get("html", f"<html><body>Content for {url}</body></html>")

            # Clean the URL to create a valid filename
            filename = _clean_url_to_filename(url)

            file_path = os.path.join(output_dir, filename)

            # Write the HTML content to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            file_paths.append(file_path)

    return len(file_paths)


def _clean_url_to_filename(url: str) -> str:
    """Convert a URL to a valid filename.

    Args:
        url: The URL to convert

    Returns:
        A valid filename derived from the URL
    """
    # Remove protocol prefixes
    filename = url.replace("https://", "").replace("http://", "")

    # Replace special characters with underscores
    filename = filename.replace("/", "_").replace("?", "_").replace("&", "_")
    filename = filename.replace(":", "_")  # Additional character cleaning

    # Ensure the filename isn't too long
    if len(filename) > 200:
        # Use the domain and a hash of the full URL if too long
        domain = filename.split("_")[0]
        filename_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{domain}_{filename_hash}.html"
    else:
        return f"{filename}.html"


def _process_llmtxt_results(result: Dict[str, Any], output_dir: str) -> int:
    """Process llmfull.txt generation results by saving text files.

    Args:
        result: The result from the completed job
        output_dir: Directory where to save the files

    Returns:
        Number of files created
    """
    file_count = 0

    # Save llmfull.txt to be accurate w firecrawl documentation
    if "data" in result and "llmsfulltxt" in result["data"]:
        llmtxt_path = os.path.join(output_dir, "llmfull.txt")
        with open(llmtxt_path, "w", encoding="utf-8") as f:
            f.write(result["data"]["llmsfulltxt"])
        file_count += 1

    return file_count


async def cancel_crawlhtml_job(
    crawl_id: str,
) -> Dict[str, Any]:
    """Cancel an in-progress Firecrawl HTML crawl job.

    Args:
        crawl_id: ID of the crawl job to cancel

    Returns:
        Dictionary containing the result of the cancellation
    """
    return await _cancel_job(crawl_id, "crawlhtml")


async def cancel_llmtxt_job(
    job_id: str,
) -> Dict[str, Any]:
    """Function to cancel an in-progress Firecrawl LLM text generation job.

    WARNING: This function is NOT SUPPORTED by the underlying Firecrawl
    API for LLM text generation jobs.
    It is provided for API consistency only but will fail when called. LLM text generation jobs
    cannot be cancelled once started and must run to completion.

    Args:
        job_id: ID of the LLM text generation job to cancel

    Returns:
        Dictionary containing an error message indicating the operation is not supported
    """
    return await _cancel_job(job_id, "llmfulltxt")


async def _cancel_job(
    job_id: str,
    job_type: Firecrawl_JobType,
) -> Dict[str, Any]:
    """Generic function to cancel a Firecrawl job.

    Args:
        job_id: ID of the job to cancel
        job_type: Type of job ('crawlhtml' or 'llmtxt')

    Returns:
        Dictionary containing the result of the cancellation
    """
    # Get configuration with API key
    config = _prepare_firecrawl_config()

    # Check if config contains an error
    if "error" in config:
        return {"error": config["error"]}

    # Special case for LLM text generation jobs - not supported
    if job_type == "llmfulltxt":
        return {
            "id": job_id,
            "status": "error",
            "message": (
                "Cancelling LLM text generation jobs is not supported." " The job must complete."
            ),
            "details": {"status": "error", "reason": "unsupported_operation"},
        }
    else:
        try:
            # Initialize the Firecrawl client
            firecrawl = FirecrawlApp(api_key=config["api_key"])

            # Cancel the job
            result = firecrawl.cancel_crawl(job_id)

            # Check if the cancellation was successful (result has 'status': 'cancelled')
            is_successful = result.get("status") == "cancelled"

            # Return a user-friendly response
            return {
                "id": job_id,
                "status": "cancelled" if is_successful else "error",
                "message": f"Firecrawl {job_type} job cancelled successfully"
                if is_successful
                else "Failed to cancel job",
                "details": result,
            }
        except Exception as e:
            return {"error": f"Error cancelling {job_type} job: {str(e)}"}
