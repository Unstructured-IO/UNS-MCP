from mcp.server.fastmcp import FastMCP

def register_destination_connectors(mcp: FastMCP):
    """Register all destination connector tools with the MCP server."""
    from .s3 import create_s3_destination, update_s3_destination, delete_s3_destination
    from .pinecone import create_pinecone_destination, update_pinecone_destination, delete_pinecone_destination
    # Register S3 destination connector tools
    mcp.tool()(create_s3_destination)
    mcp.tool()(update_s3_destination)
    mcp.tool()(delete_s3_destination)
    mcp.tool()(create_pinecone_destination)
    mcp.tool()(update_pinecone_destination)
    mcp.tool()(delete_pinecone_destination)
