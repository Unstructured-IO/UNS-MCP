import os
import time
import tempfile
import asyncio
import boto3
import hashlib
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    DeleteSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    UpdateSourceConnector,
)

# Import the FirecrawlApp client
from firecrawl import FirecrawlApp


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
    
    if not s3_uri:
        return {"error": "S3 URI is required"}
    
    # Make sure S3 URI starts with s3:// and ends with /
    if not s3_uri.startswith("s3://"):
        return {"error": "S3 URI must start with 's3://'"}
    
    # Ensure URI ends with a slash
    if not s3_uri.endswith("/"):
        s3_uri += "/"
    
    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=api_key)
        
        # Prepare crawl parameters
        params = {
            "limit": limit,
            "scrapeOptions": {
                "formats": ["html"]  # Only use HTML format
            }
        }
        

        
        # Start the crawl
        crawl_status = firecrawl.async_crawl_url(url, params=params)
        
        # Start background processing in all cases
        if "id" in crawl_status:
            crawl_id = crawl_status["id"]
            # Start background task without waiting for it (fire and forget)
            asyncio.create_task(
                wait_for_crawl_completion(ctx, crawl_id, s3_uri)
            )
            
            # Update the response to indicate background processing
            crawl_status["auto_processing"] = True
            crawl_status["s3_uri"] = f"{s3_uri}{crawl_id}/"
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
        s3_uri: S3 URI to upload to
        
    Returns:
        Dict with upload stats
    """
    # Parse the S3 URI to get bucket and prefix
    if not s3_uri.startswith("s3://"):
        raise ValueError("S3 URI must start with 's3://'")
    
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
        s3_uri: S3 URI where results will be uploaded
        poll_interval: How often to check job status in seconds (default: 30)
        timeout: Maximum time to wait in seconds (default: 1 hour)

    Returns:
        Dictionary with information about the completed job and S3 URI
    """
    start_time = time.time()
    
    # Get the API key from environment variable
    api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not api_key:
        return {"error": "Firecrawl API key is required. Set FIRECRAWL_API_KEY environment variable."}
    
    # Validate S3 URI
    if not s3_uri:
        return {"error": "S3 URI is required"}
    
    try:
        # Initialize the Firecrawl client
        firecrawl = FirecrawlApp(api_key=api_key)
        
        # Poll until completion or timeout
        while True:
            # Check the crawl status
            result = firecrawl.check_crawl_status(crawl_id)
            
            if result.get("status") == "completed":
                break
                
            # Check for timeout
            if time.time() - start_time > timeout:
                return {"error": f"Timeout waiting for crawl job {crawl_id} to complete"}
                
            # Wait before polling again
            await asyncio.sleep(poll_interval)
        
        # Create a temporary directory for HTML files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a crawl-specific subdirectory to keep files organized
            crawl_dir = os.path.join(temp_dir, crawl_id)
            os.makedirs(crawl_dir, exist_ok=True)
            
            # Get the crawl results
            scrape_result = firecrawl.check_crawl_status(crawl_id)
            
            # Process scrape_result['data'], which is a list of dicts, each with an 'html' key
            file_paths = []
            if 'data' in scrape_result and isinstance(scrape_result['data'], list):
                for i, page_data in enumerate(scrape_result['data']):
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
            
            # Construct the final S3 URI with crawl_id directly
            final_s3_uri = f"{s3_uri}{crawl_id}/"
            
            # Upload all files to S3
            try:
                # Upload the entire directory to S3
                upload_stats = _upload_directory_to_s3(crawl_dir, final_s3_uri)
                
                # Return information about the completed job
                return {
                    "id": crawl_id,
                    "status": "completed",
                    "file_count": len(file_paths),
                    "s3_uri": final_s3_uri,
                    "uploaded_files": upload_stats["uploaded_files"],
                    "failed_uploads": upload_stats["failed_files"],
                    "upload_size_bytes": upload_stats["total_bytes"],
                    "completed_urls": result.get("completed", 0),
                    "total_urls": result.get("total", 0),
                    "elapsed_time": time.time() - start_time,
                }
            except Exception as upload_error:
                return {
                    "error": f"Failed to upload files to S3: {str(upload_error)}",
                    "id": crawl_id,
                    "file_count": len(file_paths),
                }
    except Exception as e:
        return {"error": f"Error in wait_for_crawl_completion: {str(e)}"} 