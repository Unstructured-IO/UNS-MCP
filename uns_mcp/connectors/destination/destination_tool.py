from typing import Any

from mcp.server.fastmcp import Context
from typing_extensions import Literal
from unstructured_client.models.operations import DeleteDestinationRequest

from uns_mcp.connectors.destination.astra import (
    create_astradb_destination,
    update_astradb_destination,
)
from uns_mcp.connectors.destination.databricks_vdt import (
    create_databricks_delta_table_destination,
    update_databricks_delta_table_destination,
)
from uns_mcp.connectors.destination.databricksvolumes import (
    create_databricks_volumes_destination,
    update_databricks_volumes_destination,
)
from uns_mcp.connectors.destination.mongo import (
    create_mongodb_destination,
    update_mongodb_destination,
)
from uns_mcp.connectors.destination.neo4j import (
    create_neo4j_destination,
    update_neo4j_destination,
)
from uns_mcp.connectors.destination.pinecone import (
    create_pinecone_destination,
    update_pinecone_destination,
)
from uns_mcp.connectors.destination.s3 import (
    create_s3_destination,
    update_s3_destination,
)
from uns_mcp.connectors.destination.weaviate import (
    create_weaviate_destination,
    update_weaviate_destination,
)


async def create_destination_connector(
    ctx: Context,
    name: str,
    destination_type: Literal[
        "astradb",
        "databricks_delta_table",
        "databricks_volumes",
        "mongodb",
        "neo4j",
        "pinecone",
        "s3",
        "weaviate",
    ],
    type_specific_config: dict[str, Any],
) -> str:
    """Create a destination connector based on type.

    Args:
        ctx: Context object with the request and lifespan context
        name: A unique name for this connector
        destination_type: The type of destination being created

        type_specific_config:
            astradb:
                collection_name: The AstraDB collection name
                keyspace: The AstraDB keyspace
                batch_size: (Optional[int]) The batch size for inserting documents
            databricks_delta_table:
                catalog: Name of the catalog in Databricks Unity Catalog
                database: The database in Unity Catalog
                http_path: The cluster’s or SQL warehouse’s HTTP Path value
                server_hostname: The Databricks cluster’s or SQL warehouse’s Server Hostname value
                table_name: The name of the table in the schema
                volume: Name of the volume associated with the schema.
                schema: (Optional[str]) Name of the schema associated with the volume
                volume_path: (Optional[str]) Any target folder path within the volume, starting
                            from the root of the volume.
            databricks_volumes:
                catalog: Name of the catalog in Databricks
                host: The Databricks host URL
                volume: Name of the volume associated with the schema
                schema: (Optional[str]) Name of the schema associated with the volume. The default
                         value is "default".
                volume_path: (Optional[str]) Any target folder path within the volume,
                            starting from the root of the volume.
            mongodb:
                database: The name of the MongoDB database
                collection: The name of the MongoDB collection
            neo4j:
                database: The Neo4j database, e.g. "neo4j"
                uri: The Neo4j URI e.g. neo4j+s://<neo4j_instance_id>.databases.neo4j.io
                batch_size: (Optional[int]) The batch size for the connector
            pinecone:
                index_name: The Pinecone index name
                namespace: (Optional[str]) The pinecone namespace, a folder inside the
                           pinecone index
                batch_size: (Optional[int]) The batch size
            s3:
                remote_url: The S3 URI to the bucket or folder
            weaviate:
                cluster_url: URL of the Weaviate cluster
                collection: Name of the collection in the Weaviate cluster

                Note: Minimal schema is required for the collection, e.g. record_id: Text

    Returns:
        String containing the created destination connector information
    """
    destination_functions = {
        "astradb": create_astradb_destination,
        "databricks_delta_table": create_databricks_delta_table_destination,
        "databricks_volumes": create_databricks_volumes_destination,
        "mongodb": create_mongodb_destination,
        "neo4j": create_neo4j_destination,
        "pinecone": create_pinecone_destination,
        "s3": create_s3_destination,
        "weaviate": create_weaviate_destination,
    }

    if destination_type in destination_functions:
        destination_function = destination_functions[destination_type]
        return await destination_function(ctx=ctx, name=name, **type_specific_config)

    return (
        f"Unsupported destination type: {destination_type}. "
        f"Please use a supported destination type {list(destination_functions.keys())}."
    )


async def update_destination_connector(
    ctx: Context,
    destination_id: str,
    destination_type: Literal[
        "astradb",
        "databricks_delta_table",
        "databricks_volumes",
        "mongodb",
        "neo4j",
        "pinecone",
        "s3",
        "weaviate",
    ],
    type_specific_config: dict[str, Any],
) -> str:
    """Update a destination connector based on type.

    Args:
        ctx: Context object with the request and lifespan context
        destination_id: ID of the destination connector to update
        destination_type: The type of destination being updated

        type_specific_config:
            astradb:
                collection_name: (Optional[str]): The AstraDB collection name
                keyspace: (Optional[str]): The AstraDB keyspace
                batch_size: (Optional[int]) The batch size for inserting documents
            databricks_delta_table:
                catalog: (Optional[str]): Name of the catalog in Databricks Unity Catalog
                database: (Optional[str]): The database in Unity Catalog
                http_path: (Optional[str]): The cluster’s or SQL warehouse’s HTTP Path value
                server_hostname: (Optional[str]): The Databricks cluster’s or SQL warehouse’s
                                 Server Hostname value
                table_name: (Optional[str]): The name of the table in the schema
                volume: (Optional[str]): Name of the volume associated with the schema.
                schema: (Optional[str]) Name of the schema associated with the volume
                volume_path: (Optional[str]) Any target folder path within the volume, starting
                            from the root of the volume.
            databricks_volumes:
                catalog: (Optional[str]): Name of the catalog in Databricks
                host: (Optional[str]): The Databricks host URL
                volume: (Optional[str]): Name of the volume associated with the schema
                schema: (Optional[str]) Name of the schema associated with the volume. The default
                         value is "default".
                volume_path: (Optional[str]) Any target folder path within the volume,
                            starting from the root of the volume.
            mongodb:
                database: (Optional[str]): The name of the MongoDB database
                collection: (Optional[str]): The name of the MongoDB collection
            neo4j:
                database: (Optional[str]): The Neo4j database, e.g. "neo4j"
                uri: (Optional[str]): The Neo4j URI
                      e.g. neo4j+s://<neo4j_instance_id>.databases.neo4j.io
                batch_size: (Optional[int]) The batch size for the connector
            pinecone:
                index_name: (Optional[str]): The Pinecone index name
                namespace: (Optional[str]) The pinecone namespace, a folder inside the
                           pinecone index
                batch_size: (Optional[int]) The batch size
            s3:
                remote_url: (Optional[str]): The S3 URI to the bucket or folder
            weaviate:
                cluster_url: (Optional[str]): URL of the Weaviate cluster
                collection: (Optional[str]): Name of the collection in the Weaviate cluster

                Note: Minimal schema is required for the collection, e.g. record_id: Text

    Returns:
        String containing the updated destination connector information
    """
    update_functions = {
        "astradb": update_astradb_destination,
        "databricks_delta_table": update_databricks_delta_table_destination,
        "databricks_volumes": update_databricks_volumes_destination,
        "mongodb": update_mongodb_destination,
        "neo4j": update_neo4j_destination,
        "pinecone": update_pinecone_destination,
        "s3": update_s3_destination,
        "weaviate": update_weaviate_destination,
    }

    if destination_type in update_functions:
        update_function = update_functions[destination_type]
        return await update_function(ctx=ctx, destination_id=destination_id, **type_specific_config)

    return (
        f"Unsupported destination type: {destination_type}. "
        f"Please use a supported destination type: {list(update_functions.keys())}."
    )


async def delete_destination_connector(ctx: Context, destination_id: str) -> str:
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
