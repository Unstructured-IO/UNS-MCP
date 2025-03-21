"""External connectors for the Unstructured MCP system.

This package contains connectors to external services and APIs.
"""

from mcp.server.fastmcp import FastMCP

def register_external_connectors(mcp: FastMCP):
    """Register all external connector tools with the MCP server."""
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
