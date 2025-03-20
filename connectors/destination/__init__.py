from mcp.server.fastmcp import FastMCP


def register_destination_connectors(mcp: FastMCP):
    """Register all destination connector tools with the MCP server."""
    from .s3 import create_s3_destination, delete_s3_destination, update_s3_destination
    from .weaviate import (
        create_weaviate_destination,
        delete_weaviate_destination,
        update_weaviate_destination,
    )

    # Register S3 destination connector tools
    mcp.tool()(create_s3_destination)
    mcp.tool()(update_s3_destination)
    mcp.tool()(delete_s3_destination)
    
    # Register Weaviate destination connector tools
    mcp.tool()(create_weaviate_destination)
    mcp.tool()(update_weaviate_destination)
    mcp.tool()(delete_weaviate_destination)
