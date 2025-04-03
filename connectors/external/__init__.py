"""External connectors for the Unstructured MCP system.

This package contains connectors to external services and APIs.
"""

from mcp.server.fastmcp import FastMCP


def register_external_connectors(mcp: FastMCP):
    """Register all external connector tools with the MCP server."""
    # Register Firecrawl tools
    from .firecrawl import (
        cancel_crawlhtml_job,
        check_crawlhtml_status,
        check_llmtxt_status,
        invoke_firecrawl_crawlhtml,
        invoke_firecrawl_llmtxt,
    )

    mcp.tool()(invoke_firecrawl_crawlhtml)
    mcp.tool()(check_crawlhtml_status)
    mcp.tool()(invoke_firecrawl_llmtxt)
    mcp.tool()(check_llmtxt_status)
    mcp.tool()(cancel_crawlhtml_job)
    # mcp.tool()(cancel_llmtxt_job) # currently commented till firecrawl brings up a cancel feature
