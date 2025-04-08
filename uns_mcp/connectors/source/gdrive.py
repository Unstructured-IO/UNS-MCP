import os
from typing import List, Optional

from mcp.server.fastmcp import Context
from unstructured_client import UNSET, OptionalNullable
from unstructured_client.models.operations import (
    CreateSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    GoogleDriveSourceConnectorConfigInput,
    UpdateSourceConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_gdrive_source_config(
    drive_id: str,
    recursive: Optional[bool],
    extensions: OptionalNullable[List[str]] = UNSET,
) -> GoogleDriveSourceConnectorConfigInput:
    """Prepare the gdrive source connector configuration."""
    return GoogleDriveSourceConnectorConfigInput(
        drive_id=drive_id,
        recursive=recursive,
        extensions=extensions,
        service_account_key=os.getenv("GOOGLEDRIVE_SERVICE_ACCOUNT_KEY"),
    )


async def create_gdrive_source(
    ctx: Context,
    name: str,
    drive_id: str,
    recursive: bool = False,
    extensions: OptionalNullable[list[str]] = UNSET,
) -> str:
    """Create a gdrive source connector.

    Args:
        name: A unique name for this connector
        drive_id: The gdrive URI to the bucket or folder (e.g., gdrive://my-bucket/)
        recursive: Whether to access subfolders within the bucket
        extensions: (Optional[list[str]]) File extensions to filter

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_gdrive_source_config(drive_id, recursive, extensions)
    source_connector = CreateSourceConnector(name=name, type="google_drive", config=config)

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="GoogleDrive",
            connector_type="Source",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating gdrive source connector: {str(e)}"


async def update_gdrive_source(
    ctx: Context,
    source_id: str,
    drive_id: Optional[str] = None,
    recursive: Optional[bool] = None,
    extensions: OptionalNullable[List[str]] = UNSET,
) -> str:
    """Update an gdrive source connector.

    Args:
        source_id: ID of the source connector to update
        remote_url: The gdrive URI to the bucket or folder
        recursive: Whether to access subfolders within the bucket

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

    if drive_id is not None:
        config["drive_id"] = drive_id

    if recursive is not None:
        config["recursive"] = recursive

    if extensions is not None:
        config["extensions"] = extensions

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
            connector_name="GoogleDrive",
            connector_type="Source",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating gdrive source connector: {str(e)}"
