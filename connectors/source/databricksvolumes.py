import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    DeleteSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    DatabricksVolumesSourceConnectorConfigInput,
    UpdateSourceConnector,
)

from connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_databricks_volume_source_config(
    host: str,
    catalog: str,
    schema_name: str,
    volume: str,
    volume_path: str,
) -> DatabricksVolumesSourceConnectorConfigInput:
    """Prepare the Databricks Volumes source connector configuration."""
    # Always fetch credentials from environment variables

    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Environment variables DATABRICKS_CLIENT_ID, and DATABRICKS_CLIENT_SECRET must be set",
        )

    config = DatabricksVolumesSourceConnectorConfigInput(
        catalog=catalog,
        schema_name=schema_name,
        volume=volume,
        volume_path=volume_path,
        host=host,
        client_id=client_id,
        client_secret=client_secret,
    )

    return config


async def create_databricks_volume_source(
    ctx: Context,
    name: str,
    host: str,
    catalog: str,
    schema_name: str,
    volume: str,
    volume_path: str,
) -> str:
    """Create a Databricks Volumes source connector.

    Args:
        ctx: Context for the request
        name: A unique name for this connector
        host: The Databricks host URL (e.g., https://dbc-abc123-def.cloud.databricks.com)
        catalog: The Databricks catalog to use
        schema_name: The schema (database) name to use
        volume: The volume name to use
        volume_path: Path within the volume to access

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_databricks_volume_source_config(
        host,
        catalog,
        schema_name,
        volume,
        volume_path,
    )
    source_connector = CreateSourceConnector(name=name, type="databricks_volumes", config=config)

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="Databricks Volumes",
            connector_type="Source",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating Databricks Volumes source connector: {str(e)}"


async def update_databricks_volume_source(
    ctx: Context,
    source_id: str,
    catalog: Optional[str] = None,
    schema_name: Optional[str] = None,
    volume: Optional[str] = None,
    volume_path: Optional[str] = None,
) -> str:
    """Update a Databricks Volumes source connector.

    Args:
        ctx: Context for the request
        source_id: ID of the source connector to update
        catalog: The Databricks catalog to use
        schema_name: The schema (database) name to use
        volume: The volume name to use
        volume_path: Path within the volume to access
        host: The Databricks host URL
        client_id: Client ID for authentication
        client_secret: Client secret for authentication

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

    if catalog is not None:
        config["catalog"] = catalog
    if schema_name is not None:
        config["schema_name"] = schema_name
    if volume is not None:
        config["volume"] = volume
    if volume_path is not None:
        config["volume_path"] = volume_path

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
            connector_name="Databricks Volumes",
            connector_type="Source",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating Databricks Volumes source connector: {str(e)}"


async def delete_databricks_volume_source(ctx: Context, source_id: str) -> str:
    """Delete a Databricks Volumes source connector.

    Args:
        ctx: Context for the request
        source_id: ID of the source connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        _ = await client.sources.delete_source_async(
            request=DeleteSourceRequest(source_id=source_id),
        )
        return f"Databricks Volumes Source Connector with ID {source_id} deleted successfully"
    except Exception as e:
        return f"Error deleting Databricks Volumes source connector: {str(e)}"
