from typing import Any

from mcp.server.fastmcp import Context
from typing_extensions import Literal
from unstructured_client.models.operations import DeleteSourceRequest

from uns_mcp.connectors.source.azure import create_azure_source, update_azure_source
from uns_mcp.connectors.source.gdrive import create_gdrive_source, update_gdrive_source
from uns_mcp.connectors.source.onedrive import (
    create_onedrive_source,
    update_onedrive_source,
)
from uns_mcp.connectors.source.s3 import create_s3_source, update_s3_source
from uns_mcp.connectors.source.salesforce import (
    create_salesforce_source,
    update_salesforce_source,
)
from uns_mcp.connectors.source.sharepoint import (
    create_sharepoint_source,
    update_sharepoint_source,
)


async def create_source_connector(
    ctx: Context,
    name: str,
    source_type: Literal["azure", "onedrive", "salesforce", "gdrive", "s3", "sharepoint"],
    type_specific_config: dict[str, Any],
) -> str:
    """Create a source connector based on type.

    Args:
        ctx: Context object with the request and lifespan context
        name: A unique name for this connector
        source_type: The type of source being created (e.g., 'azure', 'onedrive',
                     'salesforce', 'gdrive', 's3', 'sharepoint')

        type_specific_config:
            azure:
                remote_url: The Azure Storage remote URL with the format
                            az://<container-name>/<path/to/file/or/folder/in/container/as/needed>
                recursive: (Optional[bool]) Whether to access subfolders
            gdrive:
                drive_id: The Drive ID for the Google Drive source
                recursive: (Optional[bool]) Whether to access subfolders
                extensions: (Optional[list[str]]) File extensions to filter
            onedrive:
                path: The path to the target folder in the OneDrive account
                user_pname: The User Principal Name (UPN) for the OneDrive user account
                recursive: (Optional[bool]) Whether to access subfolders
                authority_url: (Optional[str]) The authentication token provider URL
            s3:
                remote_url: The S3 URI to the bucket or folder (e.g., s3://my-bucket/)
                recursive: (Optional[bool]) Whether to access subfolders
            salesforce:
                username: The Salesforce username
                categories: (Optional[list[str]]) Optional Salesforce domain,the names of the
                            Salesforce categories (objects) that you want to access, specified as
                            a comma-separated list. Available categories include Account, Campaign,
                            Case, EmailMessage, and Lead.
            sharepoint:
                site: The SharePoint site to connect to
                user_pname: The username for the SharePoint site
                path: (Optional) The path within the SharePoint site
                recursive: (Optional[bool]) Whether to access subfolders
                authority_url: (Optional[str]) The authority URL for authentication

    Returns:
        String containing the created source connector information
    """
    source_functions = {
        "azure": create_azure_source,
        "gdrive": create_gdrive_source,
        "onedrive": create_onedrive_source,
        "s3": create_s3_source,
        "salesforce": create_salesforce_source,
        "sharepoint": create_sharepoint_source,
    }

    if source_type in source_functions:
        source_function = source_functions[source_type]
        return await source_function(ctx=ctx, name=name, **type_specific_config)

    return (
        f"Unsupported source type: {source_type}. "
        f"Please use a supported source type: {list(source_functions.keys())}."
    )


async def update_source_connector(
    ctx: Context,
    source_id: str,
    source_type: Literal["azure", "onedrive", "salesforce", "gdrive", "s3", "sharepoint"],
    type_specific_config: dict[str, Any],
) -> str:
    """Update a source connector based on type.

    Args:
        ctx: Context object with the request and lifespan context
        source_id: ID of the source connector to update
        source_type: The type of source being updated (e.g., 'azure', 'onedrive',
                     'salesforce', 'gdrive', 's3', 'sharepoint')

        type_specific_config:
            azure:
                remote_url: (Optional[str]) The Azure Storage remote URL with the format
                            az://<container-name>/<path/to/file/or/folder/in/container/as/needed>
                recursive: (Optional[bool]) Whether to access subfolders
            gdrive:
                drive_id: (Optional[str]) The Drive ID for the Google Drive source
                recursive: (Optional[bool]) Whether to access subfolders
                extensions: (Optional[list[str]]) File extensions to filter
            onedrive:
                path: (Optional[str]) The path to the target folder in the OneDrive account
                user_pname: (Optional[str]) The User Principal Name (UPN) for the OneDrive
                            user account
                recursive: (Optional[bool]) Whether to access subfolders
                authority_url: (Optional[str]) The authentication token provider URL
            s3:
                remote_url: (Optional[str]) The S3 URI to the bucket or folder
                            (e.g., s3://my-bucket/)
                recursive: (Optional[bool]) Whether to access subfolders
            salesforce:
                username: (Optional[str]) The Salesforce username
                categories: (Optional[list[str]]) Optional Salesforce domain,the names of the
                            Salesforce categories (objects) that you want to access, specified as
                            a comma-separated list. Available categories include Account, Campaign,
                            Case, EmailMessage, and Lead.
            sharepoint:
                site: Optional([str]) The SharePoint site to connect to
                user_pname: Optional([str]) The username for the SharePoint site
                path: (Optional) The path within the SharePoint site
                recursive: (Optional[bool]) Whether to access subfolders
                authority_url: (Optional[str]) The authority URL for authentication

    Returns:
        String containing the updated source connector information
    """

    update_functions = {
        "azure": update_azure_source,
        "gdrive": update_gdrive_source,
        "onedrive": update_onedrive_source,
        "s3": update_s3_source,
        "salesforce": update_salesforce_source,
        "sharepoint": update_sharepoint_source,
    }

    if source_type in update_functions:
        update_function = update_functions[source_type]
        return await update_function(ctx=ctx, source_id=source_id, **type_specific_config)

    return (
        f"Unsupported source type: {source_type}. "
        f"Please use a supported source type: {list(update_functions.keys())}."
    )


async def delete_source_connector(ctx: Context, source_id: str) -> str:
    """Delete a source connector.

    Args:
        source_id: ID of the source connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        await client.sources.delete_source_async(request=DeleteSourceRequest(source_id=source_id))
        return f"Source Connector with ID {source_id} deleted successfully"
    except Exception as e:
        return f"Error deleting source connector: {str(e)}"
