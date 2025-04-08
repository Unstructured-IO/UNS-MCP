from mcp.server.fastmcp import FastMCP

from uns_mcp.connectors.destination.destination_tool import (
    create_destination_connector,
    delete_destination_connector,
    update_destination_connector,
)


def register_destination_connectors(mcp: FastMCP):
    """Register all destination connector tools with the MCP server."""
    mcp.tool()(create_destination_connector)
    mcp.tool()(update_destination_connector)
    mcp.tool()(delete_destination_connector)
