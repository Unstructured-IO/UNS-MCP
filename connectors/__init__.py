from mcp.server.fastmcp import FastMCP


def register_connectors(mcp: FastMCP):
    """Register all connector tools with the MCP server."""
    # Import registration functions from submodules
    from connectors.destination import register_destination_connectors
    from connectors.source import register_source_connectors

    # Register connectors
    register_source_connectors(mcp)
    register_destination_connectors(mcp)
