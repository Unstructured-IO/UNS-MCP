import os
import time
import tempfile
import asyncio
import boto3
import hashlib
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import Context

# Import the FirecrawlApp client
from firecrawl import FirecrawlApp


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


async def invoke_firecrawl(
    ctx: Context,
    url: str,
    s3_uri: str,
    limit: int = 100,
) -> Dict[str, Any]:
    """Start an asynchronous web crawl job using Firecrawl.

    Args:
        url: URL to crawl
        s3_uri: S3 URI where results will be uploaded 
        limit: Maximum number of pages to crawl (default: 100)

    Returns:
        Dictionary with crawl job information including the job ID
    """
    # Get the API key from environment variable
    api_key = os.getenv("FIRECRAWL_API_KEY")
    
    # Validate parameters
    if not api_key:
        return {"error": "Firecrawl API key is required. Set FIRECRAWL_API_KEY environment variable."}
    
    # Validate and normalize S3 URI first - doing this outside the try block to handle validation errors specifically
    try:
        validated_s3_uri = _ensure_valid_s3_uri(s3_uri)
    except ValueError as ve:
        return {"error": f"Invalid S3 URI: {str(ve)}"}
    
    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=api_key)
        
        # Prepare crawl parameters
        params = {
            "limit": limit,
            "scrapeOptions": {
                "formats": ["html"]  # Only use HTML format TODO: Bring in other features of this API
            }
        }
        
        # Start the crawl
        crawl_status = firecrawl.async_crawl_url(url, params=params)
        
        # Start background processing in all cases
        if "id" in crawl_status:
            crawl_id = crawl_status["id"]
            # Start background task without waiting for it 
            asyncio.create_task(
                wait_for_crawl_completion(ctx, crawl_id, validated_s3_uri)
            )
            

            # The validated_s3_uri already has a trailing slash
            crawl_status["s3_uri"] = f"{validated_s3_uri}{crawl_id}/"
            crawl_status["message"] = "Crawl started and will be automatically processed when complete"
        
        return crawl_status
    except Exception as e:
        return {"error": f"Error starting firecrawl job: {str(e)}"}


async def check_crawl_status(
    ctx: Context,
    crawl_id: str,
) -> Dict[str, Any]:
    """Check the status of an existing Firecrawl crawl job.

    Args:
        crawl_id: ID of the crawl job to check

    Returns:
        Dictionary containing the current status of the crawl job
    """
    # Get the API key from environment variable
    api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not api_key:
        return {"error": "Firecrawl API key is required. Set FIRECRAWL_API_KEY environment variable."}
    
    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=api_key)
        
        # Check the crawl status
        result = firecrawl.check_crawl_status(crawl_id)
        
        # Return a more user-friendly response
        status_info = {
            "id": crawl_id,
            "status": result.get("status", "unknown"),
            "completed_urls": result.get("completed", 0),
            "total_urls": result.get("total", 0),
        }
        
            
        return status_info
    except Exception as e:
        return {"error": f"Error checking crawl status: {str(e)}"}


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
    uri_parts = s3_uri[5:].split('/', 1)
    bucket_name = uri_parts[0]
    prefix = uri_parts[1] if len(uri_parts) > 1 else ""
    
    # Initialize boto3 S3 client
    s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET')
        )
    
    # Track upload stats
    stats = {
        "uploaded_files": 0,
        "failed_files": 0,
        "total_bytes": 0
    }
    
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


async def poll_crawl_until_complete(
    crawl_id: str,
    api_key: str,
    poll_interval: int = 30,
    timeout: int = 3600
) -> Dict[str, Any]:
    """Poll a Firecrawl crawl job until it completes or times out.
    
    Args:
        crawl_id: ID of the crawl job to monitor
        api_key: Firecrawl API key for authentication
        poll_interval: How often to check job status in seconds (default: 30)
        timeout: Maximum time to wait in seconds (default: 1 hour)
        
    Returns:
        Dictionary containing the completed crawl result or error information
    """
    start_time = time.time()
    
    # Initialize the Firecrawl client
    firecrawl = FirecrawlApp(api_key=api_key)
    
    # Poll until completion or timeout
    while True:
        # Check the crawl status
        result = firecrawl.check_crawl_status(crawl_id)
        
        if result.get("status") == "completed":
            # Return the complete result
            return {
                "status": "completed",
                "result": result,
                "elapsed_time": time.time() - start_time
            }
            
        # Check for timeout
        if time.time() - start_time > timeout:
            return {
                "status": "timeout",
                "error": f"Timeout waiting for crawl job {crawl_id} to complete",
                "elapsed_time": time.time() - start_time
            }
            
        # Wait before polling again
        await asyncio.sleep(poll_interval)


async def process_and_upload_crawl_results(
    crawl_id: str, 
    crawl_result: Dict[str, Any], 
    s3_uri: str
) -> Dict[str, Any]:
    """Process crawl results by saving HTML files and uploading to S3.
    
    Args:
        crawl_id: ID of the crawl job
        crawl_result: The result from the completed crawl
        s3_uri: Base S3 URI where results will be uploaded (already validated)
        
    Returns:
        Dictionary with upload statistics and file information
    """
    # Create a temporary directory for HTML files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a crawl-specific subdirectory to keep files organized
        crawl_dir = os.path.join(temp_dir, crawl_id)
        os.makedirs(crawl_dir, exist_ok=True)
        
        # Process crawl_result['data'], which is a list of dicts, each with an 'html' key
        file_paths = []
        if 'data' in crawl_result and isinstance(crawl_result['data'], list):
            for i, page_data in enumerate(crawl_result['data']):
                # Skip if no HTML content
                if 'html' not in page_data:
                    continue
                
                # Get the URL from metadata if available, otherwise use index
                url = page_data.get("metadata", {}).get("url", f"page-{i}")
                content = page_data.get("html", f"<html><body>Content for {url}</body></html>")
                
                # Clean the URL to create a valid filename
                filename = url.replace("https://", "").replace("http://", "")
                filename = filename.replace("/", "_").replace("?", "_").replace("&", "_")
                filename = filename.replace(":", "_")  # Additional character cleaning
                
                # Ensure the filename isn't too long
                if len(filename) > 200:
                    # Use the domain and a hash of the full URL if too long
                    domain = filename.split('_')[0]
                    filename_hash = hashlib.md5(url.encode()).hexdigest()
                    filename = f"{domain}_{filename_hash}.html"
                else:
                    filename = f"{filename}.html"
                
                file_path = os.path.join(crawl_dir, filename)
                
                # Write the HTML content to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                file_paths.append(file_path)
        
        final_s3_uri = f"{s3_uri}{crawl_id}/"
        
        # Upload all files to S3
        try:
            # Upload the entire directory to S3
            upload_stats = _upload_directory_to_s3(crawl_dir, final_s3_uri)
            
            # Return information about the processed files and upload
            return {
                "status": "completed",
                "file_count": len(file_paths),
                "s3_uri": final_s3_uri,
                "uploaded_files": upload_stats["uploaded_files"],
                "failed_uploads": upload_stats["failed_files"],
                "upload_size_bytes": upload_stats["total_bytes"],
            }
        except Exception as upload_error:
            return {
                "status": "error",
                "error": f"Failed to upload files to S3: {str(upload_error)}",
                "file_count": len(file_paths),
            }


async def wait_for_crawl_completion(
    ctx: Context,
    crawl_id: str,
    s3_uri: str,
    poll_interval: int = 30,
    timeout: int = 3600,
) -> Dict[str, Any]:
    """Poll a Firecrawl crawl job until completion and upload results to S3.

    Args:
        crawl_id: ID of the crawl job to monitor
        s3_uri: S3 URI where results will be uploaded (already validated)
        poll_interval: How often to check job status in seconds (default: 30)
        timeout: Maximum time to wait in seconds (default: 1 hour)

    Returns:
        Dictionary with information about the completed job and S3 URI
    """
    # Get the API key from environment variable
    api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not api_key:
        return {"error": "Firecrawl API key is required. Set FIRECRAWL_API_KEY environment variable."}
    
    try:
        # First, poll until the crawl is complete
        poll_result = await poll_crawl_until_complete(
            crawl_id=crawl_id,
            api_key=api_key,
            poll_interval=poll_interval,
            timeout=timeout
        )
        
        # Check for polling errors
        if poll_result.get("status") != "completed":
            return {
                "error": poll_result.get("error", "Unknown error during crawl polling"),
                "id": crawl_id
            }
        
        # If successful, process and upload the results
        crawl_result = poll_result["result"]
        upload_result = await process_and_upload_crawl_results(
            crawl_id=crawl_id, 
            crawl_result=crawl_result, 
            s3_uri=s3_uri  
        )
        
        # Check if upload had an error
        if upload_result.get("status") == "error":
            return {
                "error": upload_result.get("error", "Unknown error during upload"),
                "id": crawl_id
            }
        
        # Combine the polling and upload results for a complete response
        return {
            "id": crawl_id,
            "status": "completed",
            "s3_uri": upload_result["s3_uri"],
            "file_count": upload_result.get("file_count", 0),
            "uploaded_files": upload_result.get("uploaded_files", 0),
            "failed_uploads": upload_result.get("failed_uploads", 0),
            "upload_size_bytes": upload_result.get("upload_size_bytes", 0),
            "completed_urls": crawl_result.get("completed", 0),
            "total_urls": crawl_result.get("total", 0),
            "elapsed_time": poll_result.get("elapsed_time", 0),
        }
    except Exception as e:
        return {"error": f"Error in wait_for_crawl_completion: {str(e)}", "id": crawl_id} 