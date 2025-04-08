import os
from typing import List, Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    SalesforceSourceConnectorConfigInput,
    UpdateSourceConnector,
)

from uns_mcp.connectors.utils import (
    create_log_for_created_updated_connector,
)


def _prepare_salesforce_source_config(
    username: str,
    categories: Optional[List[str]] = None,
) -> SalesforceSourceConnectorConfigInput:
    """Prepare the Salesforce source connector configuration."""
    if os.getenv("SALESFORCE_CONSUMER_KEY") is None or os.getenv("SALESFORCE_PRIVATE_KEY") is None:
        raise ValueError(
            "SALESFORCE_CONSUMER_KEY or SALESFORCE_PRIVATE_KEY environment variables are not set",
        )
    config = SalesforceSourceConnectorConfigInput(
        username=username,
        consumer_key=os.getenv("SALESFORCE_CONSUMER_KEY"),
        private_key=os.getenv("SALESFORCE_PRIVATE_KEY"),
        categories=categories,
    )

    return config


async def create_salesforce_source(
    ctx: Context,
    name: str,
    username: str,
    categories: Optional[list[str]] = None,
) -> str:
    """Create a Salesforce source connector.

    Args:
        name: A unique name for this connector
        username: The Salesforce username
        categories: Optional Salesforce domain,the names of the Salesforce categories (objects)
        that you want to access, specified as a comma-separated list.
        Available categories include Account, Campaign, Case, EmailMessage, and Lead.

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_salesforce_source_config(username, categories)
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
    categories: Optional[List[str]] = None,
) -> str:
    """Update a Salesforce source connector.

    Args:
        source_id: ID of the source connector to update
        username: The Salesforce username
        categories: Optional Salesforce domain,the names of the Salesforce categories (objects)
        that you want to access, specified as a comma-separated list.
        Available categories include Account, Campaign, Case, EmailMessage, and Lead.

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

    if categories is not None:
        config["categories"] = categories

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
