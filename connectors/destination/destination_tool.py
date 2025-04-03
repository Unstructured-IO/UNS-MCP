from typing import Any

from mcp.server.fastmcp import Context
from typing_extensions import Literal

from connectors.destination.astra import (
    create_astradb_destination,
    update_astradb_destination,
)
from connectors.destination.databricks_vdt import (
    create_databricks_delta_table_destination,
    update_databricks_delta_table_destination,
)
from connectors.destination.databricksvolumes import (
    create_databricks_volumes_destination,
    update_databricks_volumes_destination,
)
from connectors.destination.mongo import (
    create_mongodb_destination,
    update_mongodb_destination,
)
from connectors.destination.neo4j import (
    create_neo4j_destination,
    update_neo4j_destination,
)
from connectors.destination.pinecone import (
    create_pinecone_destination,
    update_pinecone_destination,
)
from connectors.destination.s3 import create_s3_destination, update_s3_destination
from connectors.destination.weaviate import (
    create_weaviate_destination,
    update_weaviate_destination,
)


# Function to create a destination connector
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

    Returns:
        String containing the created destination connector information
    """
    if destination_type == "astradb":
        return await create_astradb_destination(ctx=ctx, name=name, **type_specific_config)
    elif destination_type == "databricks_delta_table":
        return await create_databricks_delta_table_destination(
            ctx=ctx,
            name=name,
            **type_specific_config,
        )
    elif destination_type == "databricks_volumes":
        return await create_databricks_volumes_destination(
            ctx=ctx,
            name=name,
            **type_specific_config,
        )
    elif destination_type == "mongodb":
        return await create_mongodb_destination(ctx=ctx, name=name, **type_specific_config)
    elif destination_type == "neo4j":
        return await create_neo4j_destination(ctx=ctx, name=name, **type_specific_config)
    elif destination_type == "pinecone":
        return await create_pinecone_destination(ctx=ctx, name=name, **type_specific_config)
    elif destination_type == "s3":
        return await create_s3_destination(ctx=ctx, name=name, **type_specific_config)
    elif destination_type == "weaviate":
        return await create_weaviate_destination(ctx=ctx, name=name, **type_specific_config)
    else:
        return (
            f"Unsupported destination type: {destination_type}. "
            f"Please use a supported destination type."
        )


# Function to update a destination connector
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

    Returns:
        String containing the updated destination connector information
    """
    if destination_type == "astradb":
        return await update_astradb_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "databricks_delta_table":
        return await update_databricks_delta_table_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "databricks_volumes":
        return await update_databricks_volumes_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "mongodb":
        return await update_mongodb_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "neo4j":
        return await update_neo4j_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "pinecone":
        return await update_pinecone_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "s3":
        return await update_s3_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    elif destination_type == "weaviate":
        return await update_weaviate_destination(
            ctx=ctx,
            destination_id=destination_id,
            **type_specific_config,
        )
    else:
        return (
            f"Unsupported destination type: {destination_type}. "
            f"Please use a supported destination type."
        )
