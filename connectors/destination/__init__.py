from mcp.server.fastmcp import FastMCP

from connectors.destination.destination_tool import (
    create_destination_connector,
    update_destination_connector,
)
from connectors.destination.mongo import (
    delete_mongodb_destination,
)

from .astra import (
    delete_astradb_destination,
)
from .databricks_vdt import (
    delete_databricks_delta_table_destination,
)
from .databricksvolumes import (
    delete_databricks_volumes_destination,
)
from .neo4j import (
    delete_neo4j_destination,
)
from .pinecone import (
    delete_pinecone_destination,
)
from .s3 import delete_s3_destination
from .weaviate import (
    delete_weaviate_destination,
)


def register_destination_connectors(mcp: FastMCP):
    """Register all destination connector tools with the MCP server."""

    mcp.tool()(create_destination_connector)
    mcp.tool()(update_destination_connector)

    mcp.tool()(delete_s3_destination)

    mcp.tool()(delete_weaviate_destination)

    mcp.tool()(delete_astradb_destination)

    mcp.tool()(delete_neo4j_destination)

    mcp.tool()(delete_mongodb_destination)

    mcp.tool()(delete_databricks_volumes_destination)

    mcp.tool()(delete_databricks_delta_table_destination)

    mcp.tool()(delete_pinecone_destination)
