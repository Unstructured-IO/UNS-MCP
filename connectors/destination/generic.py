from mcp.server.fastmcp import Context
from unstructured_client.models.operations import DeleteDestinationRequest


async def delete_destination(ctx: Context, destination_id: str) -> str:
    """Delete a destination connector.

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
        return f"Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting destination connector: {str(e)}"
