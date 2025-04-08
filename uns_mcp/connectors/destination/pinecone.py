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
    PineconeDestinationConnectorConfigInput,
    UpdateDestinationConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_pinecone_dest_config(
    index_name: str,
    namespace: str = "default",
    batch_size: Optional[int] = 50,
) -> PineconeDestinationConnectorConfigInput:

    """Prepare the Azure source connector configuration."""
    if os.getenv("PINECONE_API_KEY") is None:
        raise ValueError("PINECONE_API_KEY environment variable is not set")
    else:
        return PineconeDestinationConnectorConfigInput(
            index_name=index_name,
            namespace=namespace,
            batch_size=batch_size,
            api_key=os.getenv("PINECONE_API_KEY"),
        )


async def create_pinecone_destination(
    ctx: Context,
    name: str,
    index_name: str,
    namespace: Optional[str] = "default",
    batch_size: Optional[int] = 50,
) -> str:
    """Create an pinecone destination connector.

    Args:
        name: A unique name for this connector
        index_name: The pinecone index name, used to insert vectors,
        query for similar vectors, and delete them.
        namespace: The pinecone namespace, a folder inside the pinecone index
        batch_size: The batch size refers to the number of vectors you upsert or delete

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_pinecone_dest_config(index_name, namespace, batch_size)

    destination_connector = CreateDestinationConnector(name=name, type="pinecone", config=config)

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="Pinecone",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating pinecone destination connector: {str(e)}"


async def update_pinecone_destination(
    ctx: Context,
    destination_id: str,
    index_name: Optional[str] = None,
    namespace: Optional[str] = None,
    batch_size: Optional[int] = 50,
) -> str:
    """Update an Pinecone destination connector.

    Args:
        destination_id: ID of the destination connector to update
        index_name: The pinecone index name, used to insert vectors,
        query for similar vectors, and delete them.
        namespace: The pinecone namespace, a folder inside the pinecone index

        batch_size: The batch size refers to the number of vectors you upsert or delete


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

    if index_name is not None:
        config["index_name"] = index_name
    if namespace is not None:
        config["namespace"] = namespace
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
            connector_name="Pinecone",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating pinecone destination connector: {str(e)}"
