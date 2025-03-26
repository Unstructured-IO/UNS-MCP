import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    DeleteSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    SalesforceSourceConnectorConfigInput,
    UpdateSourceConnector,
)

from connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_salesforce_source_config(
    username: str,
    domain: Optional[str] = None,
) -> SalesforceSourceConnectorConfigInput:
    """Prepare the Salesforce source connector configuration."""
    config = SalesforceSourceConnectorConfigInput(
        username=username,
        password=os.getenv("SALESFORCE_PASSWORD"),
        security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
    )
    if domain:
        config.domain = domain
    return config


async def create_salesforce_source(
    ctx: Context,
    name: str,
    username: str,
    domain: Optional[str] = None,
) -> str:
    """Create a Salesforce source connector.

    Args:
        name: A unique name for this connector
        username: The Salesforce username
        domain: Optional Salesforce domain

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_salesforce_source_config(username, domain)
    source_connector = CreateSourceConnector(name=name, type="salesforce", config=config)

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="Salesforce",
            connector_type="Source",
            created_or_updated="Created",
        )
        return result
    except Exception as e:
        return f"Error creating Salesforce source connector: {str(e)}"


async def update_salesforce_source(
    ctx: Context,
    source_id: str,
    username: Optional[str] = None,
    domain: Optional[str] = None,
) -> str:
    """Update a Salesforce source connector.

    Args:
        source_id: ID of the source connector to update
        username: The Salesforce username
        domain: Optional Salesforce domain

    Returns:
        String containing the updated source connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current source connector configuration
    try:
        get_response = await client.sources.get_source_async(
            request=GetSourceRequest(source_id=source_id),
        )
        current_config = get_response.source_connector_information.config
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)

    if username is not None:
        config["username"] = username

    if domain is not None:
        config["domain"] = domain

    source_connector = UpdateSourceConnector(config=config)

    try:
        response = await client.sources.update_source_async(
            request=UpdateSourceRequest(
                source_id=source_id,
                update_source_connector=source_connector,
            ),
        )
        result = create_log_for_created_updated_connector(
            response,
            connector_name="Salesforce",
            connector_type="Source",
            created_or_updated="Updated",
        )
        return result
    except Exception as e:
        return f"Error updating Salesforce source connector: {str(e)}"


async def delete_salesforce_source(ctx: Context, source_id: str) -> str:
    """Delete a Salesforce source connector.

    Args:
        source_id: ID of the source connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        _ = await client.sources.delete_source_async(
            request=DeleteSourceRequest(source_id=source_id),
        )
        return f"Salesforce Source Connector with ID {source_id} deleted successfully"
    except Exception as e:
        return f"Error deleting Salesforce source connector: {str(e)}"
