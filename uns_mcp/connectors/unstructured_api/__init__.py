from mcp.server.fastmcp import FastMCP

from uns_mcp.connectors.unstructured_api.partition import partition_local_file


def register_unstructured_api_tools(mcp: FastMCP):
    mcp.tool()(partition_local_file)
