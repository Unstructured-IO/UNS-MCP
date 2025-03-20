import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest,
    DeleteDestinationRequest,
    GetDestinationRequest,
    UpdateDestinationRequest,
)
from unstructured_client.models.shared import (
    CreateDestinationConnector,
    Neo4jDestinationConnectorConfigInput,
    UpdateDestinationConnector,
)

from connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_neo4j_dest_config(
    database: str,
    uri: str,
    username: str,
    batch_size: Optional[int] = None,
) -> Neo4jDestinationConnectorConfigInput:

    """Prepare the Azure source connector configuration."""
    return Neo4jDestinationConnectorConfigInput(
        database=database,
        uri=uri,
        username=username,
        batch_size=batch_size,
        password=os.getenv("NEO4J_PASSWORD"),
    )


async def create_neo4j_destination(
    ctx: Context,
    name: str,
    database: str,
    uri: str,
    username: str,
    batch_size: Optional[int] = 100,
) -> str:
    """Create an neo4j destination connector.

    Args:
        name: A unique name for this connector
        database: The neo4j database, e.g. "neo4j"
        uri: The neo4j URI, e.g. neo4j+s://<neo4j_instance_id>.databases.neo4j.io
        username: The neo4j username


    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_neo4j_dest_config(database, uri, username, batch_size)

    destination_connector = CreateDestinationConnector(name=name, type="neo4j", config=config)

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="neo4j",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating neo4j destination connector: {str(e)}"


async def update_neo4j_destination(
    ctx: Context,
    destination_id: str,
    database: Optional[str] = None,
    uri: Optional[str] = None,
    username: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> str:
    """Update an neo4j destination connector.

    Args:
        destination_id: ID of the destination connector to update
        database: The neo4j database, e.g. "neo4j"
        uri: The neo4j URI, e.g. neo4j+s://<neo4j_instance_id>.databases.neo4j.io
        username: The neo4j username


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
    if uri is not None:
        config["uri"] = uri
    if username is not None:
        config["username"] = username
    if batch_size is not None:
        config["batch_size"] = batch_size

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
            connector_name="neo4j",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating neo4j destination connector: {str(e)}"


async def delete_neo4j_destination(ctx: Context, destination_id: str) -> str:
    """Delete an neo4j destination connector.

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
        return f"neo4j Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting neo4j destination connector: {str(e)}"
