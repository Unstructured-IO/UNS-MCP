import os
from typing import Annotated, Optional

from mcp.server.fastmcp import Context
from pydantic import Field
from unstructured_client.models.operations import (
    CreateDestinationRequest,
    DeleteDestinationRequest,
    GetDestinationRequest,
    UpdateDestinationRequest,
)
from unstructured_client.models.shared import (
    CreateDestinationConnector,
    DatabricksVDTDestinationConnectorConfig,
    DatabricksVDTDestinationConnectorConfigInput,
    DestinationConnectorType,
    UpdateDestinationConnector,
)
from unstructured_client.types import (
    UNSET,
    BaseModel,
    OptionalNullable,
)

from connectors.utils import (
    create_log_for_created_updated_connector,
)


class DatabricksVDTDestinationConnectorConfigFused(BaseModel):
    # From DatabricksVDTDestinationConnectorConfigInput
    http_path: str
    server_hostname: str
    client_id: OptionalNullable[str] = UNSET
    client_secret: OptionalNullable[str] = UNSET
    token: OptionalNullable[str] = UNSET

    # From DatabricksVDTDestinationConnectorConfig
    catalog: str
    database: str  # This exists in both classes
    table_name: str
    volume: str
    schema_: Annotated[OptionalNullable[str], Field(alias="schema")] = UNSET

    # Common to both (with the same type and default)
    volume_path: OptionalNullable[str] = UNSET

    class Config:
        populate_by_name = True

    @classmethod
    def from_input_and_config(
        cls,
        input_config: DatabricksVDTDestinationConnectorConfigInput,
        dest_config: DatabricksVDTDestinationConnectorConfig,
    ) -> "DatabricksVDTDestinationConnectorConfigFused":
        """
        Create a fused config by combining input config and destination config.

        Args:
            input_config: The input connector configuration
            dest_config: The destination connector configuration

        Returns:
            A new fused configuration instance
        """

        # turn the input config to dictionary
        input_dict = input_config.model_dump()
        dest_dict = dest_config.model_dump()

        # merge the two dictionaries
        merged = {**dest_dict, **input_dict}
        return cls(**merged)


def _prepare_databricks_delta_table_dest_config(
    database: str,
    http_path: str,
    server_hostname: str,
    catalog: str,
    table_name: str,
    volume: str,
    schema: str = "default",
    volume_path: str = "/",
) -> DatabricksVDTDestinationConnectorConfigFused:

    """Prepare the Azure source connector configuration."""
    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
    if client_id is None or client_secret is None:
        raise ValueError(
            "Both Databricks client id and client secret environment variable are needed",
        )
    else:
        return DatabricksVDTDestinationConnectorConfigFused(
            http_path=http_path,
            server_hostname=server_hostname,
            catalog=catalog,
            database=database,
            schema_=schema,
            volume=volume,
            volume_path=volume_path,
            table_name=table_name,
            client_id=os.getenv("DATABRICKS_CLIENT_ID"),
            client_secret=os.getenv("DATABRICKS_CLIENT_SECRET"),
        )


async def create_databricks_delta_table_destination(
    ctx: Context,
    name: str,
    database: str,
    http_path: str,
    server_hostname: str,
    catalog: str,
    table_name: str,
    volume: str,
    schema: str = "default",
    volume_path: str = "/",
) -> str:
    """Create an databricks volume destination connector.

    Args:
        name: A unique name for this connector
        database: The name of the schema (formerly known as a database)
        in Unity Catalog for the target table
        http_path: The cluster’s or SQL warehouse’s HTTP Path value
        server_hostname: The Databricks cluster’s or SQL warehouse’s Server Hostname value
        catalog: Name of the catalog in the Databricks Unity Catalog service for the workspace.
        table_name: The name of the table in the schema
        volume: Name of the volume associated with the schema.
        schema: Name of the schema associated with the volume. The default value is "default".
        volume_path: Any target folder path within the volume, starting from the root of the volume.
    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_databricks_delta_table_dest_config(
        database,
        http_path,
        server_hostname,
        catalog,
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
    database: Optional[str] = None,
    http_path: Optional[str] = None,
    server_hostname: Optional[str] = None,
    volume_path: Optional[str] = None,
) -> str:
    """Update an databricks volumes destination connector.

    Args:
        destination_id: ID of the destination connector to update
        database: The name of the schema (formerly known as a database)
        in Unity Catalog for the target table
        http_path: The cluster’s or SQL warehouse’s HTTP Path value
        server_hostname: The Databricks cluster’s or SQL warehouse’s Server Hostname value
        volume_path: Any target folder path within the volume to update,
        starting from the root of the volume.



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

    if database is not None:
        config["database"] = database
    if server_hostname is not None:
        config["server_hostname"] = server_hostname
    if http_path is not None:
        config["http_path"] = http_path
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


async def delete_databricks_delta_table_destination(ctx: Context, destination_id: str) -> str:
    """Delete an databricks volumes destination connector.

    Args:
        destination_id: ID of the destination connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        _ = await client.destinations.delete_destination_async(
            request=DeleteDestinationRequest(destination_id=destination_id),
        )
        return f"Databricks volumes Delta Table Destination Connector with ID {destination_id} \
            deleted successfully"
    except Exception as e:
        return f"Error deleting Databricks volumes Delta Table destination connector: {str(e)}"
