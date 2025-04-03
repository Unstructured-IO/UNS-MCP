from mcp.server.fastmcp import FastMCP


def register_destination_connectors(mcp: FastMCP):
    """Register all destination connector tools with the MCP server."""
    from connectors.destination.mongo import (
        create_mongodb_destination,
        update_mongodb_destination,
    )

    from .astra import create_astradb_destination, update_astradb_destination
    from .databricks_vdt import (
        create_databricks_delta_table_destination,
        update_databricks_delta_table_destination,
    )
    from .databricksvolumes import (
        create_databricks_volumes_destination,
        update_databricks_volumes_destination,
    )
    from .neo4j import create_neo4j_destination, update_neo4j_destination
    from .pinecone import create_pinecone_destination, update_pinecone_destination
    from .s3 import create_s3_destination, update_s3_destination
    from .weaviate import create_weaviate_destination, update_weaviate_destination

    # Register S3 destination connector tools
    mcp.tool()(create_s3_destination)
    mcp.tool()(update_s3_destination)

    # Register Weaviate destination connector tools
    mcp.tool()(create_weaviate_destination)
    mcp.tool()(update_weaviate_destination)

    # Register AstraDB destination connector tools
    mcp.tool()(create_astradb_destination)
    mcp.tool()(update_astradb_destination)

    # Register Neo4j destination connector tools
    mcp.tool()(create_neo4j_destination)
    mcp.tool()(update_neo4j_destination)

    # Register MongoDB destination connector tools
    mcp.tool()(create_mongodb_destination)
    mcp.tool()(update_mongodb_destination)

    # Register databricks destination connector tools
    mcp.tool()(create_databricks_volumes_destination)
    mcp.tool()(update_databricks_volumes_destination)

    # Register databricks delta table destination connector tools
    mcp.tool()(create_databricks_delta_table_destination)
    mcp.tool()(update_databricks_delta_table_destination)

    # Register Pinecone destination connector tools

    mcp.tool()(create_pinecone_destination)
    mcp.tool()(update_pinecone_destination)
