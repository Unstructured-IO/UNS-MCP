import logging
import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest,
    GetDestinationRequest,
    UpdateDestinationRequest,
)
from unstructured_client.models.shared import (
    AstraDBConnectorConfigInput,
    CreateDestinationConnector,
    UpdateDestinationConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_astra_dest_config(
    collection_name: Optional[str] = None,
    keyspace: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> AstraDBConnectorConfigInput:
    """Prepare the AstraDB destination connector configuration."""
    token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")

    # Validate required parameters
    if not token:
        return (
            "Error: AstraDB application token is required. "
            "Set ASTRA_DB_APPLICATION_TOKEN environment variable."
        )
    if not api_endpoint:
        return (
            "Error: AstraDB API endpoint is required. "
            "Set ASTRA_DB_API_ENDPOINT environment variable."
        )
    if not collection_name:
        return "Error: AstraDB collection name is required."
    if not keyspace:
        return "Error: AstraDB keyspace is required."

    config = AstraDBConnectorConfigInput(
        token=token,
        api_endpoint=api_endpoint,
        collection_name=collection_name,
        keyspace=keyspace,
    )

    # Set optional parameters if provided
    if batch_size is not None:
        # Use default if batch_size is not positive
        if batch_size <= 0:
            batch_size = 20
            logging.info(
                f"\n Note: Provided batch_size was invalid, using default value of {batch_size}",
            )
        config.batch_size = batch_size

    return config


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
        batch_size: The batch size for inserting documents, must be positive (default: 20)

        Note: A collection in AstraDB is a schemaless document store optimized for NoSQL workloads,
              equivalent to a table in traditional databases.
              A keyspace is the top-level namespace in AstraDB that groups multiple collections.
              We require the users to create their own collection and keyspace before
              creating the connector.

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Prepare the configuration
    try:
        config = _prepare_astra_dest_config(
            collection_name=collection_name,
            keyspace=keyspace,
            batch_size=batch_size,
        )
    except ValueError as e:
        return f"Error: {str(e)}"

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

        Note: We require the users to create their own collection and
                keyspace before creating the connector.

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

    # Use current values if new ones aren't provided
    current_config = dict(current_config)
    if collection_name is None and "collection_name" in current_config:
        collection_name = current_config["collection_name"]
    if keyspace is None and "keyspace" in current_config:
        keyspace = current_config["keyspace"]
    if batch_size is None and "batch_size" in current_config:
        batch_size = current_config["batch_size"]

    try:
        config = _prepare_astra_dest_config(
            collection_name=collection_name,
            keyspace=keyspace,
            batch_size=batch_size,
        )
    except ValueError as e:
        return f"Error: {str(e)}"

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
