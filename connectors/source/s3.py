from typing import Dict, Optional
from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest, UpdateSourceRequest, DeleteSourceRequest,
    GetSourceRequest
)
from unstructured_client.models.shared import (
    CreateSourceConnector, UpdateSourceConnector
)

async def create_s3_source(
    ctx: Context,
    name: str,
    remote_url: str,
    key: Optional[str] = None,
    secret: Optional[str] = None,
    token: Optional[str] = None,
    anonymous: bool = False,
    endpoint_url: Optional[str] = None,
    recursive: bool = False
) -> str:
    """Create an S3 source connector.

    Args:
        name: A unique name for this connector
        remote_url: The S3 URI to the bucket or folder (e.g., s3://my-bucket/)
        key: The AWS access key ID (required if not using anonymous auth)
        secret: The AWS secret access key (required if not using anonymous auth)
        token: The AWS STS session token for temporary access (optional)
        anonymous: Whether to use anonymous authentication
        endpoint_url: Custom URL if connecting to a non-AWS S3 bucket
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client

    config = {
        "remote_url": remote_url,
        "recursive": recursive
    }

    if anonymous:
        config["anonymous"] = True
    else:
        if not key or not secret:
            return "When not using anonymous authentication, both key and secret are required"
        config["key"] = key
        config["secret"] = secret

    if token:
        config["token"] = token

    if endpoint_url:
        config["endpoint_url"] = endpoint_url

    source_connector = CreateSourceConnector(
        name=name,
        type="s3",
        config=config
    )

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(
                create_source_connector=source_connector
            )
        )

        info = response.source_connector_information

        result = [f"S3 Source Connector created:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config:
            # Don't print secrets in the output
            if key in ["secret", "token"] and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error creating S3 source connector: {str(e)}"

async def update_s3_source(
    ctx: Context,
    source_id: str,
    remote_url: Optional[str] = None,
    key: Optional[str] = None,
    secret: Optional[str] = None,
    token: Optional[str] = None,
    anonymous: Optional[bool] = None,
    endpoint_url: Optional[str] = None,
    recursive: Optional[bool] = None
) -> str:
    """Update an S3 source connector.

    Args:
        source_id: ID of the source connector to update
        remote_url: The S3 URI to the bucket or folder
        key: The AWS access key ID
        secret: The AWS secret access key
        token: The AWS STS session token for temporary access
        anonymous: Whether to use anonymous authentication
        endpoint_url: Custom URL if connecting to a non-AWS S3 bucket
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
        current_config = get_response.source_connector_information.config
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)
    
    if remote_url is not None:
        config["remote_url"] = remote_url
    
    if anonymous is not None:
        if anonymous:
            config["anonymous"] = True
            # Remove auth keys if switching to anonymous
            config.pop("key", None)
            config.pop("secret", None)
            config.pop("token", None)
        else:
            config.pop("anonymous", None)
    
    if key is not None:
        config["key"] = key
    
    if secret is not None:
        config["secret"] = secret
    
    if token is not None:
        config["token"] = token
    
    if endpoint_url is not None:
        config["endpoint_url"] = endpoint_url
    
    if recursive is not None:
        config["recursive"] = recursive

    source_connector = UpdateSourceConnector(config=config)

    try:
        response = await client.sources.update_source_async(
            request=UpdateSourceRequest(
                source_id=source_id,
                update_source_connector=source_connector
            )
        )

        info = response.source_connector_information

        result = [f"S3 Source Connector updated:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config:
            # Don't print secrets in the output
            if key in ["secret", "token"] and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error updating S3 source connector: {str(e)}"

async def delete_s3_source(ctx: Context, source_id: str) -> str:
    """Delete an S3 source connector.

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