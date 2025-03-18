from mcp.server.fastmcp import FastMCP


def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""
    from .s3 import create_s3_source, delete_s3_source, update_s3_source
    from .firecrawl import (
        invoke_firecrawl, 
        check_crawl_status, 
        wait_for_crawl_completion,
    )

    # Register S3 source connector tools
    mcp.tool()(create_s3_source)
    mcp.tool()(update_s3_source)
    mcp.tool()(delete_s3_source)
    
    # Register Firecrawl connector tools
    mcp.tool()(invoke_firecrawl)
    mcp.tool()(check_crawl_status)
    mcp.tool()(wait_for_crawl_completion)
