import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest, UpdateSourceRequest, DeleteSourceRequest,
    GetSourceRequest, CreateSourceResponse
)
from unstructured_client.models.shared import (
    CreateSourceConnector, UpdateSourceConnector, SourceConnectorType,
    AzureSourceConnectorConfigInput, AzureSourceConnectorConfig, UpdateSourceConnectorConfig
)

from connectors.logging_utils import create_log_for_created_updated_connector


async def create_azure_source(
    ctx: Context,
    name: str,
    remote_url: str,
    recursive: bool = False
) -> str:
    """Create an Azure source connector.

    Args:
        name: A unique name for this connector
        remote_url: The Azure Storage remote URL, with the format az://<container-name>/<path/to/file/or/folder/in/container/as/needed>
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    source_connector=CreateSourceConnector(
        name=name,
        type=SourceConnectorType.AZURE,
        config=AzureSourceConnectorConfigInput(
            remote_url=remote_url,
            recursive=recursive,
            account_name=os.getenv("AZURE_ACCOUNT_NAME", None),
            account_key=os.getenv("AZURE_ACCOUNT_KEY", None),
            sas_token=os.getenv("AZURE_SAS_TOKEN", None),
            connection_string =os.getenv("AZURE_CONNECTION_STRING", None)
        )
    )

    try:
        response: CreateSourceResponse = await client.sources.create_source_async(
            request=CreateSourceRequest(
                create_source_connector=source_connector
            )
        )
        result = create_log_for_created_updated_connector(response, source_name='Azure', source_or_destination='Source', created_or_updated='Created')
        return result

    except Exception as e:
        return f"Error creating Azure source connector: {str(e)}"


async def delete_azure_source(ctx: Context, source_id: str) -> str:
    """Delete an azure source connector.

    Args:
        source_id: ID of the source connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        response = await client.sources.delete_source_async(
            request=DeleteSourceRequest(source_id=source_id)
        )
        return f"S3 Source Connector with ID {source_id} deleted successfully"
    except Exception as e:
        return f"Error deleting S3 source connector: {str(e)}"



async def update_azure_source(
        ctx: Context,
        source_id: str,
        remote_url: Optional[str] = None,
        recursive: Optional[bool] = None
) -> str:
    """Update an azure source connector.

    Args:
        source_id: ID of the source connector to update
        remote_url: The Azure Storage remote URL, with the format az://<container-name>/<path/to/file/or/folder/in/container/as/needed>
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the updated source connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current source connector configuration
    try:
        get_response = await client.sources.get_source_async(
            request=GetSourceRequest(source_id=source_id)
        )
        current_config: AzureSourceConnectorConfig = get_response.source_connector_information.config
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    input_config = AzureSourceConnectorConfigInput(**current_config.model_dump())

    await ctx.info(f"Current config: {input_config}")

    if remote_url is not None:
        input_config.remote_url = remote_url

    if recursive is not None:
        input_config.recursive = recursive

    if os.getenv("AZURE_ACCOUNT_NAME", None):
        input_config.account_name = os.getenv("AZURE_ACCOUNT_NAME", None)

    if os.getenv("AZURE_ACCOUNT_KEY", None):
        input_config.account_key = os.getenv("AZURE_ACCOUNT_KEY", None)

    if os.getenv("AZURE_SAS_TOKEN", None):
        input_config.sas_token = os.getenv("AZURE_SAS_TOKEN", None)

    if os.getenv("AZURE_CONNECTION_STRING", None):
        input_config.connection_string = os.getenv("AZURE_CONNECTION_STRING", None)

    update_source_connector=UpdateSourceConnector(
        config=input_config
    )
    request = UpdateSourceRequest(
        source_id=source_id,
        update_source_connector=update_source_connector
    )
    try:
        response = await client.sources.update_source_async(
            request=request
        )
        result = create_log_for_created_updated_connector(response, source_name='Azure', source_or_destination='Source', created_or_updated='Updated')
        return result

    except Exception as e:
        return f"Error creating Azure source connector: {str(e)}"