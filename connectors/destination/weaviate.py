from typing import Dict, Optional
from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest, UpdateDestinationRequest, DeleteDestinationRequest,
    GetDestinationRequest
)
from unstructured_client.models.shared import (
    CreateDestinationConnector, UpdateDestinationConnector
)

async def create_weaviate_destination(
    ctx: Context,
    api_key: str,
    cluster_url: str,
    collection: Optional[str] = None,

    
) -> str:
    """Create an weaviate vector database destination connector.

    Args:
        api_key: API key for the weaviate cluster
        cluster_url: URL of the weaviate cluster
        collection (optional): Name of the collection to use in the weaviate cluster

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = {
        "key": api_key,
        "cluster_url": cluster_url,
        "collection": collection
    }

    destination_connector = CreateDestinationConnector(
        type="weaviate",
        config=config
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(
                create_destination_connector=destination_connector
            )
        )

        info = response.destination_connector_information

        result = [f"weaviate Destination Connector created:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config:
            # Don't print secrets in the output
            if key =="key" and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error creating weaviate destination connector: {str(e)}"

async def update_weaviate_destination(
    ctx: Context,
    destination_id: str,
    api_key: Optional[str] = None,
    cluster_url:Optional[str]=None,
    collection: Optional[str] = None,
    

   
) -> str:
    """Update an weaviate destination connector.

    Args:
        destination_id: ID of the destination connector to update
        api_key (optional): API key for the weaviate cluster
        cluster_url (optional): URL of the weaviate cluster
        collection (optional): Name of the collection to use in the weaviate cluster

    Returns:
        String containing the updated destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current destination connector configuration
    try:
        get_response = await client.destinations.get_destination_async(
            request=GetDestinationRequest(destination_id=destination_id)
        )
        current_config = get_response.destination_connector_information.config
    except Exception as e:
        return f"Error retrieving destination connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)
    
    if cluster_url is not None:
        config["cluster_url"] = cluster_url
    
    if key is not None:
        config["key"] = api_key
    if collection is not None:
        config["collection"] = collection

    destination_connector = UpdateDestinationConnector(config=config)

    try:
        response = await client.destinations.update_destination_async(
            request=UpdateDestinationRequest(
                destination_id=destination_id,
                update_destination_connector=destination_connector
            )
        )

        info = response.destination_connector_information

        result = [f"weaviate Destination Connector updated:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config:
            # Don't print secrets in the output
            if key =="key" and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
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
        response = await client.destinations.delete_destination_async(
            request=DeleteDestinationRequest(destination_id=destination_id)
        )
        return f"weaviate Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting weaviate destination connector: {str(e)}" 