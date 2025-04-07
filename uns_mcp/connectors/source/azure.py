import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    CreateSourceResponse,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    AzureSourceConnectorConfig,
    AzureSourceConnectorConfigInput,
    CreateSourceConnector,
    SourceConnectorType,
    UpdateSourceConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


async def create_azure_source(
    ctx: Context,
    name: str,
    remote_url: str,
    recursive: bool = False,
) -> str:
    """Create an Azure source connector.

    Args:
        name: A unique name for this connector
        remote_url: The Azure Storage remote URL,
        with the format az://<container-name>/<path/to/file/or/folder/in/container/as/needed>
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_azure_source_config(remote_url, recursive)
    source_connector = CreateSourceConnector(
        name=name,
        type=SourceConnectorType.AZURE,
        config=config,
    )

    try:
        response: CreateSourceResponse = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="Azure",
            connector_type="Source",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating Azure source connector: {str(e)}"


async def update_azure_source(
    ctx: Context,
    source_id: str,
    remote_url: Optional[str] = None,
    recursive: Optional[bool] = None,
) -> str:
    """Update an azure source connector.

    Args:
        source_id: ID of the source connector to update
        remote_url: The Azure Storage remote URL, with the format
        az://<container-name>/<path/to/file/or/folder/in/container/as/needed>
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the updated source connector information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        get_response = await client.sources.get_source_async(
            request=GetSourceRequest(source_id=source_id),
        )
        current_config: AzureSourceConnectorConfig = (
            get_response.source_connector_information.config
        )
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    input_config = AzureSourceConnectorConfigInput(**current_config.model_dump())

    if remote_url is not None:
        input_config.remote_url = remote_url

    if recursive is not None:
        input_config.recursive = recursive

    config = _prepare_azure_source_config(input_config.remote_url, input_config.recursive)

    try:
        response = await client.sources.update_source_async(
            request=UpdateSourceRequest(
                source_id=source_id,
                update_source_connector=UpdateSourceConnector(config=config),
            ),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="Azure",
            connector_type="Source",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating Azure source connector: {str(e)}"


def _prepare_azure_source_config(
    remote_url: Optional[str],
    recursive: Optional[bool],
) -> AzureSourceConnectorConfigInput:
    """Prepare the Azure source connector configuration."""
    if os.getenv("AZURE_CONNECTION_STRING") and not (
        os.getenv("AZURE_ACCOUNT_NAME")
        or os.getenv("AZURE_ACCOUNT_KEY")
        or os.getenv("AZURE_SAS_TOKEN")
    ):
        return AzureSourceConnectorConfigInput(
            remote_url=remote_url,
            recursive=recursive,
            connection_string=os.getenv("AZURE_CONNECTION_STRING"),
        )
    elif (
        os.getenv("AZURE_ACCOUNT_NAME")
        and os.getenv("AZURE_ACCOUNT_KEY")
        and not (os.getenv("AZURE_SAS_TOKEN") or os.getenv("AZURE_CONNECTION_STRING"))
    ):
        return AzureSourceConnectorConfigInput(
            remote_url=remote_url,
            recursive=recursive,
            account_name=os.getenv("AZURE_ACCOUNT_NAME"),
            account_key=os.getenv("AZURE_ACCOUNT_KEY"),
        )
    elif (
        os.getenv("AZURE_ACCOUNT_NAME")
        and os.getenv("AZURE_SAS_TOKEN")
        and not (os.getenv("AZURE_ACCOUNT_KEY") or os.getenv("AZURE_CONNECTION_STRING"))
    ):
        return AzureSourceConnectorConfigInput(
            remote_url=remote_url,
            recursive=recursive,
            account_name=os.getenv("AZURE_ACCOUNT_NAME"),
            sas_token=os.getenv("AZURE_SAS_TOKEN"),
        )
    else:
        raise ValueError("No Azure credentials provided")
