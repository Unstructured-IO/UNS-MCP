from typing import Optional
import os

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest,
    DeleteDestinationRequest,
    GetDestinationRequest,
    UpdateDestinationRequest,
)
from unstructured_client.models.shared import (
    CreateDestinationConnector,
    UpdateDestinationConnector,
)

from connectors.utils import (
    create_log_for_created_updated_connector,
)


async def create_astradb_destination(
    ctx: Context,
    name: str,
    collection_name: str,
    keyspace: str,
    batch_size: int = 20,
) -> str:
    """Create an AstraDB destination connector.

    Args:
        name: A unique name for this connector
        collection_name: The name of the collection to use 
        keyspace: The AstraDB keyspace 
        batch_size: The batch size for inserting documents (default: 20)

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get credentials from environment variables
    token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")

    # Validate required parameters
    if not token:
        return "Error: AstraDB application token is required. Set ASTRA_DB_APPLICATION_TOKEN environment variable."
    if not api_endpoint:
        return "Error: AstraDB API endpoint is required. Set ASTRA_DB_API_ENDPOINT environment variable."
    if not collection_name:
        return "Error: AstraDB collection name is required."
    if not keyspace:
        return "Error: AstraDB keyspace is required."

    config = {
        "token": token,
        "api_endpoint": api_endpoint,
        "collection_name": collection_name,
        "keyspace": keyspace,
        "batch_size": batch_size
    }

    destination_connector = CreateDestinationConnector(name=name, type="astradb", config=config)

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="AstraDB",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating AstraDB destination connector: {str(e)}"


async def update_astradb_destination(
    ctx: Context,
    destination_id: str,
    collection_name: Optional[str] = None,
    keyspace: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> str:
    """Update an AstraDB destination connector.

    Args:
        destination_id: ID of the destination connector to update
        collection_name: The name of the collection to use (optional)
        keyspace: The AstraDB keyspace (optional)
        batch_size: The batch size for inserting documents (optional)

    Returns:
        String containing the updated destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get credentials from environment variables
    token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")

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

    if token is not None:
        config["token"] = token

    if api_endpoint is not None:
        config["api_endpoint"] = api_endpoint

    if collection_name is not None:
        config["collection_name"] = collection_name

    if keyspace is not None:
        config["keyspace"] = keyspace

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
            connector_name="AstraDB",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating AstraDB destination connector: {str(e)}"


async def delete_astradb_destination(ctx: Context, destination_id: str) -> str:
    """Delete an AstraDB destination connector.

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
        return f"AstraDB Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting AstraDB destination connector: {str(e)}" 
