from mcp.server.fastmcp import FastMCP


def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""
    from .s3 import create_s3_source, delete_s3_source, update_s3_source

    # Register S3 source connector tools
    mcp.tool()(create_s3_source)
    mcp.tool()(update_s3_source)
    mcp.tool()(delete_s3_source)

    from .azure import create_azure_source, delete_azure_source, update_azure_source

    mcp.tool()(create_azure_source)
    mcp.tool()(update_azure_source)
    mcp.tool()(delete_azure_source)

    from .gdrive import create_gdrive_source, delete_gdrive_source, update_gdrive_source

    mcp.tool()(create_gdrive_source)
    mcp.tool()(update_gdrive_source)
    mcp.tool()(delete_gdrive_source)

    from .onedrive import (
        create_onedrive_source,
        delete_onedrive_source,
        update_onedrive_source,
    )

    mcp.tool()(create_onedrive_source)
    mcp.tool()(update_onedrive_source)
    mcp.tool()(delete_onedrive_source)
