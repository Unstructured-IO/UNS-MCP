import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest,
    GetDestinationRequest,
    UpdateDestinationRequest,
)
from unstructured_client.models.shared import (
    CreateDestinationConnector,
    DatabricksVDTDestinationConnectorConfigInput,
    DestinationConnectorType,
    UpdateDestinationConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_databricks_delta_table_dest_config(
    catalog: str,
    database: str,
    http_path: str,
    server_hostname: str,
    table_name: str,
    volume: str,
    schema: Optional[str] = "default",
    volume_path: Optional[str] = "/",
) -> DatabricksVDTDestinationConnectorConfigInput:

    """Prepare the Azure source connector configuration."""
    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
    if client_id is None or client_secret is None:
        raise ValueError(
            "Both Databricks client id and client secret environment variable are needed",
        )
    else:
        return DatabricksVDTDestinationConnectorConfigInput(
            catalog=catalog,
            database=database,
            http_path=http_path,
            server_hostname=server_hostname,
            table_name=table_name,
            schema_=schema,
            volume=volume,
            volume_path=volume_path,
            client_id=os.getenv("DATABRICKS_CLIENT_ID"),
            client_secret=os.getenv("DATABRICKS_CLIENT_SECRET"),
        )


async def create_databricks_delta_table_destination(
    ctx: Context,
    name: str,
    catalog: str,
    database: str,
    http_path: str,
    server_hostname: str,
    table_name: str,
    volume: str,
    schema: Optional[str] = "default",
    volume_path: Optional[str] = "/",
) -> str:
    """Create an databricks volume destination connector.

    Args:
        name: A unique name for this connector
        catalog: Name of the catalog in the Databricks Unity Catalog service for the workspace.
        database: The name of the schema (formerly known as a database)
        in Unity Catalog for the target table
        http_path: The cluster’s or SQL warehouse’s HTTP Path value
        server_hostname: The Databricks cluster’s or SQL warehouse’s Server Hostname value
        table_name: The name of the table in the schema
        volume: Name of the volume associated with the schema.
        schema: Name of the schema associated with the volume. The default value is "default".
        volume_path: Any target folder path within the volume, starting from the root of the volume.
    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_databricks_delta_table_dest_config(
        catalog,
        database,
        http_path,
        server_hostname,
        table_name,
        volume,
        schema,
        volume_path,
    )

    destination_connector = CreateDestinationConnector(
        name=name,
        type=DestinationConnectorType.DATABRICKS_VOLUME_DELTA_TABLES,
        config=config,
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="Databricks Volumes Delta Table",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating databricks volumes Delta Table destination connector: {str(e)}"


async def update_databricks_delta_table_destination(
    ctx: Context,
    destination_id: str,
    catalog: Optional[str] = None,
    database: Optional[str] = None,
    http_path: Optional[str] = None,
    server_hostname: Optional[str] = None,
    table_name: Optional[str] = None,
    schema: Optional[str] = None,
    volume: Optional[str] = None,
    volume_path: Optional[str] = None,
) -> str:
    """Update an databricks volumes destination connector.

    Args:
        destination_id: ID of the destination connector to update
        catalog: Name of the catalog in the Databricks Unity Catalog service for the workspace.
        database: The name of the schema (formerly known as a database)
        in Unity Catalog for the target table
        http_path: The cluster’s or SQL warehouse’s HTTP Path value
        server_hostname: The Databricks cluster’s or SQL warehouse’s Server Hostname value
        table_name: The name of the table in the schema
        volume: Name of the volume associated with the schema.
        schema: Name of the schema associated with the volume. The default value is "default".
        volume_path: Any target folder path within the volume, starting from the root of the volume.

    Returns:
        String containing the updated destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current destination connector configuration
    try:
        get_response = await client.destinations.get_destination_async(
            request=GetDestinationRequest(destination_id=destination_id),
        )
        current_config = get_response.destination_connector_information.config
    except Exception as e:
        return f"Error retrieving destination connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)
    if catalog is not None:
        config["catalog"] = catalog

    if database is not None:
        config["database"] = database
    if server_hostname is not None:
        config["server_hostname"] = server_hostname
    if http_path is not None:
        config["http_path"] = http_path
    if table_name is not None:
        config["table_name"] = table_name
    if volume is not None:
        config["volume"] = volume

    if schema is not None:
        config["schema_"] = schema
    if volume_path is not None:
        config["volume_path"] = volume_path

    destination_connector = UpdateDestinationConnector(config=config)

    try:
        response = await client.destinations.update_destination_async(
            request=UpdateDestinationRequest(
                destination_id=destination_id,
                update_destination_connector=destination_connector,
            ),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="Databricks Volumes Delta Table",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating databricks volumes Delta Table destination connector: {str(e)}"
