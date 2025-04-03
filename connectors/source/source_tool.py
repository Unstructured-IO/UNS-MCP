from typing import Any

from typing_extensions import Literal

from connectors.source.azure import create_azure_source, update_azure_source
from connectors.source.gdrive import create_gdrive_source, update_gdrive_source
from connectors.source.onedrive import create_onedrive_source, update_onedrive_source
from connectors.source.s3 import create_s3_source, update_s3_source
from connectors.source.salesforce import (
    create_salesforce_source,
    update_salesforce_source,
)
from connectors.source.sharepoint import (
    create_sharepoint_source,
    update_sharepoint_source,
)


async def create_source_connector(
    ctx: Any,
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
                remote_url: The Azure Storage remote URL
            onedrive:
                path: The path to the target folder in the OneDrive account
                user_pname: The User Principal Name (UPN) for the OneDrive user account
                authority_url: (Optional) The authentication token provider URL
            salesforce:
                username: The Salesforce username
                categories: (Optional) Salesforce domain
            gdrive:
                drive_id: The Drive ID for the Google Drive source
                recursive: (Optional) Whether to access subfolders
                extensions: (Optional) File extensions to filter
            s3:
                remote_url: The S3 URI to the bucket or folder
                recursive: (Optional) Whether to access subfolders
            sharepoint:
                site: The SharePoint site to connect to
                user_pname: The username for the SharePoint site
                path: (Optional) The path within the SharePoint site
                recursive: (Optional) Whether to access subfolders
                authority_url: (Optional) The authority URL for authentication

    Returns:
        String containing the created source connector information
    """
    if source_type == "azure":
        return await create_azure_source(ctx=ctx, name=name, **type_specific_config)
    elif source_type == "onedrive":
        return await create_onedrive_source(ctx=ctx, name=name, **type_specific_config)
    elif source_type == "salesforce":
        return await create_salesforce_source(ctx=ctx, name=name, **type_specific_config)
    elif source_type == "gdrive":
        return await create_gdrive_source(ctx=ctx, name=name, **type_specific_config)
    elif source_type == "s3":
        return await create_s3_source(ctx=ctx, name=name, **type_specific_config)
    elif source_type == "sharepoint":
        return await create_sharepoint_source(ctx=ctx, name=name, **type_specific_config)
    else:
        return f"Unsupported source type: {source_type}. Please use a supported source type."


async def update_source_connector(
    ctx: Any,
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
                remote_url: (Optional) The Azure Storage remote URL
                recursive: (Optional) Whether to access subfolders
            onedrive:
                path: (Optional) The path to the target folder in the OneDrive account
                user_pname: (Optional) The User Principal Name for the OneDrive user account
                authority_url: (Optional) The authentication token provider URL
                tenant: (Optional) The directory (tenant) ID of the app registration
                client_id: (Optional) The client ID for the app registration
            salesforce:
                username: (Optional) The Salesforce username
                categories: (Optional) Salesforce categories
            gdrive:
                drive_id: (Optional) The Drive ID for the Google Drive source
                recursive: (Optional) Whether to access subfolders
                extensions: (Optional) File extensions to filter
            s3:
                remote_url: (Optional) The S3 URI to the bucket or folder
                recursive: (Optional) Whether to access subfolders
            sharepoint:
                site: (Optional) The SharePoint site to connect to
                user_pname: (Optional) The username for the SharePoint site
                path: (Optional) The path within the SharePoint site
                recursive: (Optional) Whether to access subfolders
                authority_url: (Optional) The authority URL for authentication

    Returns:
        String containing the updated source connector information
    """
    if source_type == "azure":
        return await update_azure_source(ctx=ctx, source_id=source_id, **type_specific_config)
    elif source_type == "onedrive":
        return await update_onedrive_source(ctx=ctx, source_id=source_id, **type_specific_config)
    elif source_type == "salesforce":
        return await update_salesforce_source(ctx=ctx, source_id=source_id, **type_specific_config)
    elif source_type == "gdrive":
        return await update_gdrive_source(ctx=ctx, source_id=source_id, **type_specific_config)
    elif source_type == "s3":
        return await update_s3_source(ctx=ctx, source_id=source_id, **type_specific_config)
    elif source_type == "sharepoint":
        return await update_sharepoint_source(ctx=ctx, source_id=source_id, **type_specific_config)
    else:
        return f"Unsupported source type: {source_type}. Please use a supported source type."
