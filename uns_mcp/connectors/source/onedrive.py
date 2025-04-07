import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    OneDriveSourceConnectorConfigInput,
    UpdateSourceConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_onedrive_source_config(
    path: str,
    user_pname: str,
    recursive: Optional[bool] = False,
    authority_url: Optional[str] = None,
) -> OneDriveSourceConnectorConfigInput:
    """Prepare the OneDrive source connector configuration."""
    config = OneDriveSourceConnectorConfigInput(
        path=path,
        user_pname=user_pname,
        recursive=recursive,
        client_cred=os.getenv("ONEDRIVE_CLIENT_CRED"),
        # client id and tenant id are not strictly sensitive
        # but they are cumbersome to pass in as arguments
        # so made them env vars
        client_id=os.getenv("ONEDRIVE_CLIENT_ID"),
        tenant=os.getenv("ONEDRIVE_TENANT_ID"),
    )
    if authority_url:
        config.authority_url = authority_url
    return config


async def create_onedrive_source(
    ctx: Context,
    name: str,
    path: str,
    user_pname: str,
    recursive: bool = False,
    authority_url: Optional[str] = "https://login.microsoftonline.com",
) -> str:
    """Create a OneDrive source connector.

    Args:
        name: A unique name for this connector
        path: The path to the target folder in the OneDrive account,
            starting with the account’s root folder
        user_pname: The User Principal Name (UPN) for the OneDrive user account in Entra ID.
            This is typically the user’s email address.
        recursive: Whether to access subfolders
        authority_url: The authentication token provider URL for the Entra ID app registration.
            The default is https://login.microsoftonline.com.

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_onedrive_source_config(path, user_pname, recursive, authority_url)
    source_connector = CreateSourceConnector(name=name, type="onedrive", config=config)

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="OneDrive",
            connector_type="Source",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating OneDrive source connector: {str(e)}"


async def update_onedrive_source(
    ctx: Context,
    source_id: str,
    path: Optional[str] = None,
    user_pname: Optional[str] = None,
    recursive: Optional[bool] = None,
    authority_url: Optional[str] = None,
    tenant: Optional[str] = None,
    client_id: Optional[str] = None,
) -> str:
    """Update a OneDrive source connector.

    Args:
        source_id: ID of the source connector to update
        path: The path to the target folder in the OneDrive account,
            starting with the account’s root folder
        user_pname: The User Principal Name (UPN) for the OneDrive user account in Entra ID.
            This is typically the user’s email address.
        recursive: Whether to access subfolders
        authority_url: The authentication token provider URL for the Entra ID app registration.
            The default is https://login.microsoftonline.com.
        tenant: The directory (tenant) ID of the Entra ID app registration.
        client_id: The application (client) ID of the Microsoft Entra ID app registration
            that has access to the OneDrive account.

    Returns:
        String containing the updated source connector information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        get_response = await client.sources.get_source_async(
            request=GetSourceRequest(source_id=source_id),
        )
        current_config = get_response.source_connector_information.config
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    config = dict(current_config)

    if path is not None:
        config["path"] = path
    if user_pname is not None:
        config["user_pname"] = user_pname
    if recursive is not None:
        config["recursive"] = recursive
    if authority_url is not None:
        config["authority_url"] = authority_url
    if tenant is not None:
        config["tenant"] = tenant
    if client_id is not None:
        config["client_id"] = client_id

    source_connector = UpdateSourceConnector(config=config)

    try:
        response = await client.sources.update_source_async(
            request=UpdateSourceRequest(
                source_id=source_id,
                update_source_connector=source_connector,
            ),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="OneDrive",
            connector_type="Source",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating OneDrive source connector: {str(e)}"
