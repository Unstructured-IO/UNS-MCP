from mcp.server.fastmcp import Context
from unstructured_client.models.operations import DeleteSourceRequest


async def delete_source(ctx: Context, source_id: str) -> str:
    """Delete a source connector.

    Args:
        source_id: ID of the source connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        await client.sources.delete_source_async(request=DeleteSourceRequest(source_id=source_id))
        return f"Source Connector with ID {source_id} deleted successfully"
    except Exception as e:
        return f"Error deleting source connector: {str(e)}"
