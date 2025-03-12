from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Dict, List
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP, Context
from unstructured_client import UnstructuredClient
from unstructured_client.models.operations import (
    ListSourcesRequest, ListWorkflowsRequest, GetSourceRequest,
    ListDestinationsRequest, GetDestinationRequest, GetWorkflowRequest,
    CreateWorkflowRequest, RunWorkflowRequest, UpdateWorkflowRequest,
    DeleteWorkflowRequest
)
from unstructured_client.models.shared import (
    SourceConnectorType, WorkflowState, DestinationConnectorType,
    WorkflowNode, WorkflowNodeType, CreateWorkflow, UpdateWorkflow,
    WorkflowType, Schedule
)

def load_environment_variables() -> None:
    """
    Load environment variables from .env file.
    Raises an error if critical environment variables are missing.
    """
    load_dotenv()
    required_vars = [
        "UNSTRUCTURED_API_KEY"
    ]

    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Missing required environment variable: {var}")


@dataclass
class AppContext:
    client: UnstructuredClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage Unstructured API client lifecycle"""
    api_key = os.getenv("UNSTRUCTURED_API_KEY")
    if not api_key:
        raise ValueError("UNSTRUCTURED_API_KEY environment variable is required")

    client = UnstructuredClient(api_key_auth=api_key)
    try:
        yield AppContext(client=client)
    finally:
        # No cleanup needed for the API client
        pass


# Create MCP server instance
mcp = FastMCP("Unstructured API", lifespan=app_lifespan)


@mcp.tool()
async def list_sources(ctx: Context, source_type: Optional[str] = None) -> str:
    """
    List available sources from the Unstructured API.

    Args:
        source_type: Optional source connector type to filter by

    Returns:
        String containing the list of sources
    """
    client = ctx.request_context.lifespan_context.client

    request = ListSourcesRequest()
    if source_type:
        try:
            request.source_type = SourceConnectorType[source_type]
        except KeyError:
            return f"Invalid source type: {source_type}"

    response = await client.sources.list_sources_async(request=request)

    # Sort sources by name
    sorted_sources = sorted(
        response.response_list_sources,
        key=lambda source: source.name.lower()
    )

    if not sorted_sources:
        return "No sources found"

    # Format response
    result = ["Available sources:"]
    for source in sorted_sources:
        result.append(f"- {source.name} (ID: {source.id})")

    return "\n".join(result)


@mcp.tool()
async def list_workflows(
        ctx: Context,
        destination_id: Optional[str] = None,
        source_id: Optional[str] = None,
        status: Optional[str] = None
) -> str:
    """
    List workflows from the Unstructured API.

    Args:
        destination_id: Optional destination connector ID to filter by
        source_id: Optional source connector ID to filter by
        status: Optional workflow status to filter by

    Returns:
        String containing the list of workflows
    """
    client = ctx.request_context.lifespan_context.client

    request = ListWorkflowsRequest(
        destination_id=destination_id,
        source_id=source_id
    )

    if status:
        try:
            request.status = WorkflowState[status]
        except KeyError:
            return f"Invalid workflow status: {status}"

    response = await client.workflows.list_workflows_async(request=request)

    # Sort workflows by name
    sorted_workflows = sorted(
        response.response_list_workflows,
        key=lambda workflow: workflow.name.lower()
    )

    if not sorted_workflows:
        return "No workflows found"

    # Format response
    result = ["Available workflows:"]
    for workflow in sorted_workflows:
        result.append(f"- {workflow.name} (ID: {workflow.id})")

    return "\n".join(result)


@mcp.tool()
async def get_source_info(ctx: Context, source_id: str) -> str:
    """Get detailed information about a specific source connector.

    Args:
        source_id: ID of the source connector to get information for

    Returns:
        String containing the source connector information
    """
    client = ctx.request_context.lifespan_context.client

    response = await client.sources.get_source_async(
        request=GetSourceRequest(source_id=source_id)
    )

    info = response.source_connector_information

    result = [f"Source Connector Information:"]
    result.append(f"Name: {info.name}")
    result.append("Configuration:")
    for key, value in info.config:
        result.append(f"  {key}: {value}")

    return "\n".join(result)


@mcp.tool()
async def list_destinations(ctx: Context, destination_type: Optional[str] = None) -> str:
    """List available destinations from the Unstructured API.

    Args:
        destination_type: Optional destination connector type to filter by

    Returns:
        String containing the list of destinations
    """
    client = ctx.request_context.lifespan_context.client

    request = ListDestinationsRequest()
    if destination_type:
        try:
            request.destination_type = DestinationConnectorType[destination_type]
        except KeyError:
            return f"Invalid destination type: {destination_type}"

    response = await client.destinations.list_destinations_async(request=request)

    sorted_destinations = sorted(
        response.response_list_destinations,
        key=lambda dest: dest.name.lower()
    )

    if not sorted_destinations:
        return "No destinations found"

    result = ["Available destinations:"]
    for dest in sorted_destinations:
        result.append(f"- {dest.name} (ID: {dest.id})")

    return "\n".join(result)


@mcp.tool()
async def get_destination_info(ctx: Context, destination_id: str) -> str:
    """Get detailed information about a specific destination connector.

    Args:
        destination_id: ID of the destination connector to get information for

    Returns:
        String containing the destination connector information
    """
    client = ctx.request_context.lifespan_context.client

    response = await client.destinations.get_destination_async(
        request=GetDestinationRequest(destination_id=destination_id)
    )

    info = response.destination_connector_information

    result = [f"Destination Connector Information:"]
    result.append(f"Name: {info.name}")
    result.append("Configuration:")
    for key, value in info.config:
        result.append(f"  {key}: {value}")

    return "\n".join(result)


@mcp.tool()
async def get_workflow_info(ctx: Context, workflow_id: str) -> str:
    """Get detailed information about a specific workflow.

    Args:
        workflow_id: ID of the workflow to get information for

    Returns:
        String containing the workflow information
    """
    client = ctx.request_context.lifespan_context.client

    response = await client.workflows.get_workflow_async(
        request=GetWorkflowRequest(workflow_id=workflow_id)
    )

    info = response.workflow_information

    result = ["Workflow Information:"]
    result.append(f"Name: {info.name}")
    result.append(f"ID: {info.id}")
    result.append(f"Status: {info.status}")
    result.append(f"Type: {info.workflow_type}")

    result.append("\nSources:")
    for source in info.sources:
        result.append(f"  - {source}")

    result.append("\nDestinations:")
    for destination in info.destinations:
        result.append(f"  - {destination}")

    result.append("\nSchedule:")
    for crontab_entry in info.schedule.crontab_entries:
        result.append(f"  - {crontab_entry.cron_expression}")

    return "\n".join(result)


@mcp.tool()
async def create_workflow(ctx: Context, workflow_config: Dict) -> str:
    """Create a new workflow.

    Args:
        workflow_config: Dictionary containing the workflow configuration
            Must include required fields as per CreateWorkflow model

    Returns:
        String containing the created workflow information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        workflow = CreateWorkflow(**workflow_config)
        response = await client.workflows.create_workflow_async(
            request=CreateWorkflowRequest(create_workflow=workflow)
        )

        info = response.workflow_information
        return await get_workflow_info(ctx, info.id)
    except Exception as e:
        return f"Error creating workflow: {str(e)}"


@mcp.tool()
async def run_workflow(ctx: Context, workflow_id: str) -> str:
    """Run a specific workflow.

    Args:
        workflow_id: ID of the workflow to run

    Returns:
        String containing the response from the workflow execution
    """
    client = ctx.request_context.lifespan_context.client

    try:
        response = await client.workflows.run_workflow_async(
            request=RunWorkflowRequest(workflow_id=workflow_id)
        )
        return f"Workflow execution initiated: {response.raw_response}"
    except Exception as e:
        return f"Error running workflow: {str(e)}"


@mcp.tool()
async def update_workflow(ctx: Context, workflow_id: str, workflow_config: Dict) -> str:
    """Update an existing workflow.

    Args:
        workflow_id: ID of the workflow to update
        workflow_config: Dictionary containing the updated workflow configuration
            Must include required fields as per UpdateWorkflow model

    Returns:
        String containing the updated workflow information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        workflow = UpdateWorkflow(**workflow_config)
        response = await client.workflows.update_workflow_async(
            request=UpdateWorkflowRequest(
                workflow_id=workflow_id,
                update_workflow=workflow
            )
        )

        info = response.workflow_information
        return await get_workflow_info(ctx, info.id)
    except Exception as e:
        return f"Error updating workflow: {str(e)}"


@mcp.tool()
async def delete_workflow(ctx: Context, workflow_id: str) -> str:
    """Delete a specific workflow.

    Args:
        workflow_id: ID of the workflow to delete

    Returns:
        String containing the response from the workflow deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        response = await client.workflows.delete_workflow_async(
            request=DeleteWorkflowRequest(workflow_id=workflow_id)
        )
        return f"Workflow deleted successfully: {response.raw_response}"
    except Exception as e:
        return f"Error deleting workflow: {str(e)}"

if __name__ == "__main__":
    load_environment_variables()
    mcp.run()