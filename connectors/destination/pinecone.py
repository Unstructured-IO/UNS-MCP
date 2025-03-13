from typing import Dict, Optional
from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest, UpdateDestinationRequest, DeleteDestinationRequest,
    GetDestinationRequest
)
from unstructured_client.models.shared import (
    CreateDestinationConnector, UpdateDestinationConnector
)

async def create_pinecone_destination(
    ctx: Context,
    name: str,
    index_name: str,
    api_key: str,
    name_space: str="default",
    batch_size: str=50,
    
) -> str:
    """Create an pinecone vector database destination connector.

    Args:
        name: Name of the destination connector
        index_name: Name of the pinecone index
        name_space: Namespace of the pinecone index with default value of "default"
        batch_size: Batch size for indexing with default value of 50
        api_key: Pinecone API key


    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = {
        "index_name": index_name,
        "key": api_key,
        "namespace": name_space,
        "batch_size": batch_size
    }

    destination_connector = CreateDestinationConnector(
        name=name,
        type="pinecone",
        config=config
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(
                create_destination_connector=destination_connector
            )
        )

        info = response.destination_connector_information

        result = [f"PineCone Destination Connector created:"]
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
        return f"Error creating Pinecone destination connector: {str(e)}"

async def update_pinecone_destination(
    ctx: Context,
    destination_id: str,
    index_name: Optional[str] = None,
    api_key: Optional[str] = None,
    name_space: str="default",
    batch_size: str="50",
    

   
) -> str:
    """Update an Pinecone destination connector.

    Args:

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
    
    if index_name is not None:
        config["index_name"] = index_name
    
    if key is not None:
        config["key"] = api_key
    if name_space is not None:
        config["namespace"] = name_space
    if batch_size is not None:
        config["batch_size"] = batch_size

    destination_connector = UpdateDestinationConnector(config=config)

    try:
        response = await client.destinations.update_destination_async(
            request=UpdateDestinationRequest(
                destination_id=destination_id,
                update_destination_connector=destination_connector
            )
        )

        info = response.destination_connector_information

        result = [f"Pinecone Destination Connector updated:"]
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
        return f"Error updating Pinecone destination connector: {str(e)}"

async def delete_pinecone_destination(ctx: Context, destination_id: str) -> str:
    """Delete an Pinecone destination connector.

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
        return f"Pinecone Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting Pinecone destination connector: {str(e)}" 