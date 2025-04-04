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
    DestinationConnectorType,
    UpdateDestinationConnector,
    WeaviateDestinationConnectorConfigInput,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_weaviate_dest_config(
    collection: str,
    cluster_url: str,
) -> WeaviateDestinationConnectorConfigInput:
    """Prepare the Azure source connector configuration."""
    return WeaviateDestinationConnectorConfigInput(
        cluster_url=cluster_url,
        api_key=os.getenv("WEAVIATE_CLOUD_API_KEY"),
        collection=collection,
    )


async def create_weaviate_destination(
    ctx: Context,
    name: str,
    cluster_url: str,
    collection: str,
) -> str:
    """Create an weaviate vector database destination connector.

    Args:
        cluster_url: URL of the weaviate cluster
        collection : Name of the collection to use in the weaviate cluster
        Note: The collection is a table in the weaviate cluster.
              In platform, there are dedicated code to generate collection for users
              here, due to the simplicity of the server, we are not generating it for users.

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_weaviate_dest_config(collection, cluster_url)

    destination_connector = CreateDestinationConnector(
        name=name,
        type=DestinationConnectorType.WEAVIATE_CLOUD,
        config=config,
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="Weaviate",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result

    except Exception as e:
        return f"Error creating weaviate destination connector: {str(e)}"


async def update_weaviate_destination(
    ctx: Context,
    destination_id: str,
    cluster_url: Optional[str] = None,
    collection: Optional[str] = None,
) -> str:
    """Update an weaviate destination connector.

    Args:
        destination_id: ID of the destination connector to update
        cluster_url (optional): URL of the weaviate cluster
        collection (optional): Name of the collection(like a file) to use in the weaviate cluster

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

    if cluster_url is not None:
        config["cluster_url"] = cluster_url

    if collection is not None:
        config["collection"] = collection

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
            connector_name="Weaviate",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating weaviate destination connector: {str(e)}"


async def delete_weaviate_destination(ctx: Context, destination_id: str) -> str:
    """Delete an weaviate destination connector.

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
        return f"weaviate Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting weaviate destination connector: {str(e)}"
