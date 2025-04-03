from mcp.server.fastmcp import FastMCP

from connectors.source.azure import delete_azure_source
from connectors.source.gdrive import delete_gdrive_source
from connectors.source.onedrive import delete_onedrive_source
from connectors.source.s3 import delete_s3_source
from connectors.source.salesforce import delete_salesforce_source
from connectors.source.sharepoint import delete_sharepoint_source
from connectors.source.source_tool import (
    create_source_connector,
    update_source_connector,
)


def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""
    mcp.tool()(create_source_connector)
    mcp.tool()(update_source_connector)
    mcp.tool()(delete_s3_source)
    mcp.tool()(delete_azure_source)
    mcp.tool()(delete_gdrive_source)
    mcp.tool()(delete_onedrive_source)
    mcp.tool()(delete_salesforce_source)
    mcp.tool()(delete_sharepoint_source)
