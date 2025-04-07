from mcp.server.fastmcp import FastMCP


def register_connectors(mcp: FastMCP):
    """Register all connector tools with the MCP server."""
    # Import registration functions from submodules
    from uns_mcp.connectors.destination import register_destination_connectors
    from uns_mcp.connectors.external import register_external_connectors
    from uns_mcp.connectors.source import register_source_connectors
    from uns_mcp.connectors.unstructured_api import register_unstructured_api_tools

    # Register connectors
    register_source_connectors(mcp)
    register_destination_connectors(mcp)
    register_external_connectors(mcp)
    register_unstructured_api_tools(mcp)
