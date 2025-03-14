from mcp.server.fastmcp import FastMCP

def register_source_connectors(mcp: FastMCP):
    """Register all source connector tools with the MCP server."""
    from .s3 import create_s3_source, update_s3_source, delete_s3_source
    
    # Register S3 source connector tools
    mcp.tool()(create_s3_source)
    mcp.tool()(update_s3_source)
    mcp.tool()(delete_s3_source)
