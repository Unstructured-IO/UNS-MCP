from typing import Dict, Optional
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateDestinationRequest, UpdateDestinationRequest, DeleteDestinationRequest,
    GetDestinationRequest
)
from unstructured_client.models.shared import (
    CreateDestinationConnector, UpdateDestinationConnector
)

async def create_s3_destination(
    ctx: Context,
    name: str,
    remote_url: str,
    key: Optional[str] = None,
    secret: Optional[str] = None,
    token: Optional[str] = None,
    endpoint_url: Optional[str] = None
) -> str:
    """Create an S3 destination connector.

    Args:
        name: A unique name for this connector
        remote_url: The S3 URI to the bucket or folder (e.g., s3://my-bucket/)
        key: The AWS access key ID
        secret: The AWS secret access key
        token: The AWS STS session token for temporary access (optional)
        endpoint_url: Custom URL if connecting to a non-AWS S3 bucket

    Returns:
        String containing the created destination connector information
    """
    client = ctx.request_context.lifespan_context.client
    
    load_dotenv()
    
    if key is None:
        key = os.getenv("AWS_ACCESS_KEY_ID")
        if not key:
            print("AWS_ACCESS_KEY_ID not found in environment variables, provide it manually in chat")
    
    if secret is None:
        secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not secret:
            print("AWS_SECRET_ACCESS_KEY not found in environment variables, provide it manually in chat")

    config = {
        "remote_url": remote_url,
        "key": key,
        "secret": secret
    }

    if token:
        config["token"] = token

    if endpoint_url:
        config["endpoint_url"] = endpoint_url

    destination_connector = CreateDestinationConnector(
        name=name,
        type="s3",
        config=config
    )

    try:
        response = await client.destinations.create_destination_async(
            request=CreateDestinationRequest(
                create_destination_connector=destination_connector
            )
        )
        print(response)
        info = response.destination_connector_information

        result = [f"S3 Destination Connector created:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config.items():
            # Don't print secrets in the output
            if key in ["secret", "token"] and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error creating S3 destination connector: {str(e)}"

async def update_s3_destination(
    ctx: Context,
    destination_id: str,
    remote_url: Optional[str] = None,
    key: Optional[str] = None,
    secret: Optional[str] = None,
    token: Optional[str] = None,
    endpoint_url: Optional[str] = None
) -> str:
    """Update an S3 destination connector.

    Args:
        destination_id: ID of the destination connector to update
        remote_url: The S3 URI to the bucket or folder
        key: The AWS access key ID
        secret: The AWS secret access key
        token: The AWS STS session token for temporary access
        endpoint_url: Custom URL if connecting to a non-AWS S3 bucket

    Returns:
        String containing the updated destination connector information
    """
    client = ctx.request_context.lifespan_context.client
    
    load_dotenv()
    
    if key is None and secret is None:
        env_key = os.getenv("AWS_ACCESS_KEY_ID")
        env_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not env_key:
            print("AWS_ACCESS_KEY_ID not found in environment variables, provide it manually in chat")
        if not env_secret:
            print("AWS_SECRET_ACCESS_KEY not found in environment variables, provide it manually in chat")
        key = env_key
        secret = env_secret

    # Get the current destination connector configuration
    try:
        get_response = await client.destinations.get_destination_async(
            request=GetDestinationRequest(destination_id=destination_id)
        )
        current_config = get_response.destination_connector_information.config
    except Exception as e:
        return f"Error retrieving destination connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)
    
    if remote_url is not None:
        config["remote_url"] = remote_url
    
    if key is not None:
        config["key"] = key
    
    if secret is not None:
        config["secret"] = secret
    
    if token is not None:
        config["token"] = token
    
    if endpoint_url is not None:
        config["endpoint_url"] = endpoint_url

    destination_connector = UpdateDestinationConnector(config=config)

    try:
        response = await client.destinations.update_destination_async(
            request=UpdateDestinationRequest(
                destination_id=destination_id,
                update_destination_connector=destination_connector
            )
        )

        info = response.destination_connector_information

        result = [f"S3 Destination Connector updated:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config.items():
            # Don't print secrets in the output
            if key in ["secret", "token"] and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error updating S3 destination connector: {str(e)}"

async def delete_s3_destination(ctx: Context, destination_id: str) -> str:
    """Delete an S3 destination connector.

    Args:
        destination_id: ID of the destination connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        response = await client.destinations.delete_destination_async(
            request=DeleteDestinationRequest(destination_id=destination_id)
        )
        return f"S3 Destination Connector with ID {destination_id} deleted successfully"
    except Exception as e:
        return f"Error deleting S3 destination connector: {str(e)}" 