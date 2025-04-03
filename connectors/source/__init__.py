from mcp.server.fastmcp import FastMCP


def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""
    from .generic import delete_source

    mcp.tool()(delete_source)

    from .s3 import create_s3_source, update_s3_source

    # Register S3 source connector tools
    mcp.tool()(create_s3_source)
    mcp.tool()(update_s3_source)

    from .azure import create_azure_source, update_azure_source

    mcp.tool()(create_azure_source)
    mcp.tool()(update_azure_source)

    from .gdrive import create_gdrive_source, update_gdrive_source

    mcp.tool()(create_gdrive_source)
    mcp.tool()(update_gdrive_source)

    from .onedrive import create_onedrive_source, update_onedrive_source

    mcp.tool()(create_onedrive_source)
    mcp.tool()(update_onedrive_source)

    from .salesforce import create_salesforce_source, update_salesforce_source

    mcp.tool()(create_salesforce_source)
    mcp.tool()(update_salesforce_source)

    from .sharepoint import create_sharepoint_source, update_sharepoint_source

    mcp.tool()(create_sharepoint_source)
    mcp.tool()(update_sharepoint_source)
