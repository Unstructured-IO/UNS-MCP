from mcp.server.fastmcp import FastMCP


def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""
    from .s3 import create_s3_source, delete_s3_source, update_s3_source
    # Register S3 source connector tools
    mcp.tool()(create_s3_source)
    mcp.tool()(update_s3_source)
    mcp.tool()(delete_s3_source)
    
    # Register Firecrawl tools
    from .firecrawl import (
        invoke_firecrawl_crawlhtml, 
        check_crawlhtml_status, 
        invoke_firecrawl_llmtxt, 
        check_llmtxt_status,
        cancel_crawlhtml_job,
        cancel_llmtxt_job
    )
    mcp.tool()(invoke_firecrawl_crawlhtml)
    mcp.tool()(check_crawlhtml_status)
    mcp.tool()(invoke_firecrawl_llmtxt)
    mcp.tool()(check_llmtxt_status)
    mcp.tool()(cancel_crawlhtml_job)
    # mcp.tool()(cancel_llmtxt_job) # currently commented till firecrawl brings up a cancel feature

    from .azure import create_azure_source, delete_azure_source, update_azure_source

    mcp.tool()(create_azure_source)
    mcp.tool()(update_azure_source)
    mcp.tool()(delete_azure_source)

    from .gdrive import create_gdrive_source, delete_gdrive_source, update_gdrive_source

    mcp.tool()(create_gdrive_source)
    mcp.tool()(update_gdrive_source)
    mcp.tool()(delete_gdrive_source)
