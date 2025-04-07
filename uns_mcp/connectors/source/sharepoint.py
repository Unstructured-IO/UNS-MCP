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
    SharePointSourceConnectorConfigInput,
    UpdateSourceConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_sharepoint_source_config(
    site: str,
    user_pname: str,
    path: Optional[str],
    recursive: Optional[bool],
    authority_url: Optional[str],
) -> SharePointSourceConnectorConfigInput:
    """Prepare the SharePoint source connector configuration."""
    config = SharePointSourceConnectorConfigInput(
        site=site,
        user_pname=user_pname,
        client_id=os.getenv("SHAREPOINT_CLIENT_ID"),
        client_cred=os.getenv("SHAREPOINT_CLIENT_CRED"),
        tenant=os.getenv("SHAREPOINT_TENANT_ID"),
        path=path,
        recursive=recursive,
    )
    if authority_url:
        config.authority_url = authority_url
    return config


async def create_sharepoint_source(
    ctx: Context,
    name: str,
    site: str,
    user_pname: str,
    path: Optional[str] = None,
    recursive: bool = False,
    authority_url: Optional[str] = None,
) -> str:
    """Create a SharePoint source connector.

    Args:
        name: A unique name for this connector
        site: The SharePoint site to connect to
        user_pname: The username for the SharePoint site
        path: The path within the SharePoint site
        recursive: Whether to access subfolders within the site
        authority_url: The authority URL for authentication

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_sharepoint_source_config(site, user_pname, path, recursive, authority_url)
    source_connector = CreateSourceConnector(name=name, type="sharepoint", config=config)

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="SharePoint",
            connector_type="Source",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating SharePoint source connector: {str(e)}"


async def update_sharepoint_source(
    ctx: Context,
    source_id: str,
    site: Optional[str] = None,
    user_pname: Optional[str] = None,
    path: Optional[str] = None,
    recursive: Optional[bool] = None,
    authority_url: Optional[str] = None,
) -> str:
    """Update a SharePoint source connector.

    Args:
        source_id: ID of the source connector to update
        site: The SharePoint site to connect to
        user_pname: The username for the SharePoint site
        path: The path within the SharePoint site
        recursive: Whether to access subfolders within the site
        authority_url: The authority URL for authentication

    Returns:
        String containing the updated source connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current source connector configuration
    try:
        get_response = await client.sources.get_source_async(
            request=GetSourceRequest(source_id=source_id),
        )
        current_config = get_response.source_connector_information.config
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)

    if site is not None:
        config["site"] = site
    if user_pname is not None:
        config["user_pname"] = user_pname
    if path is not None:
        config["path"] = path
    if recursive is not None:
        config["recursive"] = recursive
    if authority_url is not None:
        config["authority_url"] = authority_url

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
            connector_name="SharePoint",
            connector_type="Source",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating SharePoint source connector: {str(e)}"
