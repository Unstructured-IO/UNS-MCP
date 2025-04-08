from mcp.server.fastmcp import FastMCP

from uns_mcp.connectors.source.source_tool import (
    create_source_connector,
    delete_source_connector,
    update_source_connector,
)


def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""

    mcp.tool()(create_source_connector)
    mcp.tool()(update_source_connector)
    mcp.tool()(delete_source_connector)
