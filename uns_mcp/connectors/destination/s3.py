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
    S3DestinationConnectorConfigInput,
    UpdateDestinationConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_s3_dest_config(
    remote_url: Optional[str],
) -> S3DestinationConnectorConfigInput:
    """Prepare the S3 destination connector configuration."""
    config = S3DestinationConnectorConfigInput(
        remote_url=remote_url,
        key=os.getenv("AWS_KEY"),
        secret=os.getenv("AWS_SECRET"),
    )
    if os.getenv("TOKEN"):
        config.token = os.getenv("TOKEN")
    if os.getenv("ENDPOINT_URL"):
        config.endpoint_url = os.getenv("ENDPOINT_URL")
    return config


async def create_s3_destination(
    ctx: Context,
    name: str,
    remote_url: str,
) -> str:
    """Create an S3 destination connector.

    Args:
        name: A unique name for this connector
        remote_url: The S3 URI to the bucket or folder

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = _prepare_s3_dest_config(remote_url)

    destination_connector = CreateDestinationConnector(
        name=name,
        type=DestinationConnectorType.S3,
        config=config,
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(create_destination_connector=destination_connector),
        )

        result = create_log_for_created_updated_connector(
            response,
            connector_name="S3",
            connector_type="Destination",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating S3 destination connector: {str(e)}"


async def update_s3_destination(
    ctx: Context,
    destination_id: str,
    remote_url: Optional[str] = None,
    recursive: Optional[bool] = None,
) -> str:
    """Update an S3 destination connector.

    Args:
        destination_id: ID of the destination connector to update
        remote_url: The S3 URI to the bucket or folder

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

    # Update configuration with new values
    config = dict(current_config)

    if remote_url is not None:
        config["remote_url"] = remote_url
    if recursive is not None:
        config["recursive"] = recursive

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
            connector_name="S3",
            connector_type="Destination",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating S3 destination connector: {str(e)}"
