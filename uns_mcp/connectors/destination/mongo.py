import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest,
    GetDestinationRequest,
    UpdateDestinationRequest,
)
from unstructured_client.models.shared import (
    CreateDestinationConnector,
    DestinationConnectorType,
    MongoDBConnectorConfigInput,
    UpdateDestinationConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_mongodb_dest_config(
    database: str,
    collection: str,
) -> MongoDBConnectorConfigInput:
    """Prepare the MongoDB destination connector configuration."""
    config = MongoDBConnectorConfigInput(
        database=database,
        collection=collection,
        uri=os.getenv("MONGO_DB_CONNECTION_STRING"),
    )
    return config


async def create_mongodb_destination(
    ctx: Context,
    name: str,
    database: str,
    collection: str,
) -> str:
    """Create an MongoDB destination connector.

    Args:
        name: A unique name for this connector
        database: The name of the database to connect to.
        collection: The name of the target MongoDB collection
    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_mongodb_dest_config(database=database, collection=collection)

    destination_connector = CreateDestinationConnector(
        name=name,
        type=DestinationConnectorType.MONGODB,
        config=config,
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="MongoDB",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating MongoDB destination connector: {str(e)}"


async def update_mongodb_destination(
    ctx: Context,
    destination_id: str,
    database: Optional[str] = None,
    collection: Optional[str] = None,
) -> str:
    """Update an MongoDB destination connector.

    Args:
        destination_id: ID of the destination connector to update
        database: The name of the database to connect to.
        collection: The name of the target MongoDB collection

    Returns:
        String containing the updated destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current destination connector configuration
    try:
        get_response = await client.destinations.get_destination_async(
            request=GetDestinationRequest(destination_id=destination_id),
        )
        current_config = get_response.destination_connector_information.config
    except Exception as e:
        return f"Error retrieving destination connector: {str(e)}"

    input_config = MongoDBConnectorConfigInput(**current_config.model_dump())
    config: MongoDBConnectorConfigInput = _prepare_mongodb_dest_config(
        database=database or input_config.database,
        collection=collection or input_config.collection,
    )

    destination_connector = UpdateDestinationConnector(config=config)

    try:
        response = await client.destinations.update_destination_async(
            request=UpdateDestinationRequest(
                destination_id=destination_id,
                update_destination_connector=destination_connector,
            ),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="MongoDB",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating MongoDB destination connector: {str(e)}"
