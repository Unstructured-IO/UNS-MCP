import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from copy import deepcopy
from dataclasses import dataclass
from itertools import groupby
from typing import AsyncIterator, Optional

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.sse import SseServerTransport
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from unstructured_client import UnstructuredClient
from unstructured_client.models.operations import (
    CancelJobRequest,
    CreateWorkflowRequest,
    DeleteWorkflowRequest,
    GetDestinationRequest,
    GetJobRequest,
    GetSourceRequest,
    GetWorkflowRequest,
    ListDestinationsRequest,
    ListJobsRequest,
    ListSourcesRequest,
    ListWorkflowsRequest,
    RunWorkflowRequest,
    UpdateWorkflowRequest,
)
from unstructured_client.models.shared import (
    CreateWorkflow,
    DestinationConnectorInformation,
    DestinationConnectorType,
    JobInformation,
    JobStatus,
    SourceConnectorInformation,
    SourceConnectorType,
    UpdateWorkflow,
    WorkflowInformation,
    WorkflowState,
    WorkflowType,
)
from unstructured_client.models.shared.createworkflow import CreateWorkflowTypedDict

from uns_mcp.connectors import register_connectors
from uns_mcp.docstring_extras import add_custom_node_examples


def load_environment_variables() -> None:
    """
    Load environment variables from .env file.
    Raises an error if critical environment variables are missing.
    """
    load_dotenv(override=True)
    required_vars = ["UNSTRUCTURED_API_KEY"]

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

    DEBUG_API_REQUESTS = (
        os.environ.get("DEBUG_API_REQUESTS", "False").lower() == "true"
    )  # get env variable
    if DEBUG_API_REQUESTS:
        import httpx

        from uns_mcp.custom_http_client import CustomHttpClient

        client = UnstructuredClient(
            api_key_auth=api_key,
            async_client=CustomHttpClient(httpx.AsyncClient()),
        )
    else:
        client = UnstructuredClient(api_key_auth=api_key)

    try:
        yield AppContext(client=client)
    finally:
        # No cleanup needed for the API client
        pass


# Create MCP server instance
mcp = FastMCP(
    "Unstructured API",
    lifespan=app_lifespan,
    dependencies=["unstructured-client", "python-dotenv"],
)


register_connectors(mcp)


@mcp.tool()
async def list_sources(
    ctx: Context,
    source_type: Optional[SourceConnectorType | str] = None,
) -> str:
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
            source_type = (
                SourceConnectorType(source_type) if isinstance(source_type, str) else source_type
            )
            request.source_type = source_type
        except KeyError:
            return f"Invalid source type: {source_type}"

    response = await client.sources.list_sources_async(request=request)

    # Sort sources by name
    sorted_sources = sorted(response.response_list_sources, key=lambda source: source.name.lower())

    if not sorted_sources:
        return "No sources found"

    # Format response
    result = ["Available sources:"]
    for source in sorted_sources:
        result.append(f"- {source.name} (ID: {source.id})")

    return "\n".join(result)


@mcp.tool()
async def get_source_info(ctx: Context, source_id: str) -> str:
    """Get detailed information about a specific source connector.

    Args:
        source_id: ID of the source connector to get information for, should be valid UUID

    Returns:
        String containing the source connector information
    """
    client = ctx.request_context.lifespan_context.client

    response = await client.sources.get_source_async(request=GetSourceRequest(source_id=source_id))

    info = response.source_connector_information

    result = ["Source Connector Information:"]
    result.append(f"Name: {info.name}")
    result.append("Configuration:")
    for key, value in info.config:
        result.append(f"  {key}: {value}")

    return "\n".join(result)


@mcp.tool()
async def list_destinations(
    ctx: Context,
    destination_type: Optional[DestinationConnectorType | str] = None,
) -> str:
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
            destination_type = (
                DestinationConnectorType(destination_type)
                if isinstance(destination_type, str)
                else destination_type
            )
            request.destination_type = destination_type
        except KeyError:
            return f"Invalid destination type: {destination_type}"

    response = await client.destinations.list_destinations_async(request=request)

    sorted_destinations = sorted(
        response.response_list_destinations,
        key=lambda dest: dest.name.lower(),
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
        request=GetDestinationRequest(destination_id=destination_id),
    )

    info = response.destination_connector_information

    result = ["Destination Connector Information:"]
    result.append(f"Name: {info.name}")
    result.append("Configuration:")
    for key, value in info.config:
        result.append(f"  {key}: {value}")

    return "\n".join(result)


@mcp.tool()
async def list_workflows(
    ctx: Context,
    destination_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[WorkflowState | str] = None,
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

    request = ListWorkflowsRequest(destination_id=destination_id, source_id=source_id)

    if status:
        try:
            status = WorkflowState(status) if isinstance(status, str) else status
            request.status = status
        except KeyError:
            return f"Invalid workflow status: {status}"

    response = await client.workflows.list_workflows_async(request=request)

    # Sort workflows by name
    sorted_workflows = sorted(
        response.response_list_workflows,
        key=lambda workflow: workflow.name.lower(),
    )

    if not sorted_workflows:
        return "No workflows found"

    # Format response
    result = ["Available workflows:"]
    for workflow in sorted_workflows:
        result.append(f"- {workflow.name} (ID: {workflow.id})")

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
        request=GetWorkflowRequest(workflow_id=workflow_id),
    )

    info: WorkflowInformation = response.workflow_information

    result = ["Workflow Information:"]
    result.append(f"Name: {info.name}")
    result.append(f"ID: {info.id}")
    result.append(f"Status: {info.status.value}")
    if info.workflow_type is None:
        result.append("Type: Undefined")
    else:
        result.append(f"Type: {info.workflow_type.value}")

    result.append("\nSources:")
    for source in info.sources:
        result.append(f"  - {source}")

    if info.workflow_type and info.workflow_type == WorkflowType.CUSTOM.value:
        result.append("\nWorkflow Nodes:")
        for node in info.workflow_nodes:
            result.append(f"  - {node.name} (Type: {node.type.value}) (Subtype: {node.subtype}):")
            if node.settings:
                result.append(f"    Settings: {json.dumps(node.settings, indent=8)}")

    result.append("\nDestinations:")
    for destination in info.destinations:
        result.append(f"  - {destination}")

    result.append("\nSchedule:")
    if info.schedule.crontab_entries:
        for crontab_entry in info.schedule.crontab_entries:
            result.append(f"  - {crontab_entry.cron_expression}")
    else:
        result.append("  - No crontab entry")

    return "\n".join(result)


@mcp.tool()
@add_custom_node_examples  # Note: This documentation is added due to lack of typing in
# WorkflowNode.settings. It can be safely deleted when typing is added.
async def create_workflow(ctx: Context, workflow_config: CreateWorkflowTypedDict) -> str:
    """Create a new workflow.

    Args:
        workflow_config: A Typed Dictionary containing required fields (destination_id - should be a
        valid UUID, name, source_id - should be a valid UUID, workflow_type) and non-required fields
        (schedule, and workflow_nodes). Note workflow_nodes is only enabled when workflow_type
        is `custom` and is a list of WorkflowNodeTypedDict: partition, prompter,chunk, embed
        Below is an example of a partition workflow node:
            {
                "name": "vlm-partition",
                "type": "partition",
                "sub_type": "vlm",
                "settings": {
                            "provider": "your favorite provider",
                            "model": "your favorite model"
                            }
            }


    Returns:
        String containing the created workflow information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        workflow = CreateWorkflow(**workflow_config)
        response = await client.workflows.create_workflow_async(
            request=CreateWorkflowRequest(create_workflow=workflow),
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
            request=RunWorkflowRequest(workflow_id=workflow_id),
        )
        return f"Workflow execution initiated: {response.raw_response}"
    except Exception as e:
        return f"Error running workflow: {str(e)}"


@mcp.tool()
# WorkflowNode.settings. It can be safely deleted when typing is added.
async def update_workflow(
    ctx: Context,
    workflow_id: str,
    workflow_config: CreateWorkflowTypedDict,
) -> str:
    """Update an existing workflow.

    Args:
        workflow_id: ID of the workflow to update
        workflow_config: A Typed Dictionary containing required fields (destination_id,
        name, source_id, workflow_type) and non-required fields (schedule, and workflow_nodes)

    Returns:
        String containing the updated workflow information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        workflow = UpdateWorkflow(**workflow_config)
        response = await client.workflows.update_workflow_async(
            request=UpdateWorkflowRequest(workflow_id=workflow_id, update_workflow=workflow),
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
            request=DeleteWorkflowRequest(workflow_id=workflow_id),
        )
        return f"Workflow deleted successfully: {response.raw_response}"
    except Exception as e:
        return f"Error deleting workflow: {str(e)}"


@mcp.tool()
async def list_jobs(
    ctx: Context,
    workflow_id: Optional[str] = None,
    status: Optional[JobStatus | str] = None,
) -> str:
    """
    List jobs via the Unstructured API.

    Args:
        workflow_id: Optional workflow ID to filter by
        status: Optional job status to filter by

    Returns:
        String containing the list of jobs
    """
    client = ctx.request_context.lifespan_context.client

    request = ListJobsRequest(workflow_id=workflow_id, status=status)

    if status:
        try:
            status = JobStatus(status) if isinstance(status, str) else status
            request.status = status
        except KeyError:
            return f"Invalid job status: {status}"

    response = await client.jobs.list_jobs_async(request=request)

    # Sort jobs by name
    sorted_jobs = sorted(
        response.response_list_jobs,
        key=lambda job: job.created_at,
    )

    if not sorted_jobs:
        return "No Jobs found"

    # Format response
    result = ["Available Jobs by created time:"]
    for job in sorted_jobs:
        result.append(f"- JOB ID: {job.id}")

    return "\n".join(result)


@mcp.tool()
async def get_job_info(ctx: Context, job_id: str) -> str:
    """Get detailed information about a specific job.

    Args:
        job_id: ID of the job to get information for

    Returns:
        String containing the job information
    """
    client = ctx.request_context.lifespan_context.client

    response = await client.jobs.get_job_async(
        request=GetJobRequest(job_id=job_id),
    )

    info = response.job_information

    result = ["Job Information:"]
    result.append(f"Created at: {info.created_at}")
    result.append(f"ID: {info.id}")
    result.append(f"Status: {info.status}")
    result.append(f"Workflow name: {info.workflow_name}")
    result.append(f"Workflow id: {info.workflow_id}")
    result.append(f"Runtime: {info.runtime}")
    result.append(f"Raw result: {json.dumps(json.loads(info.json()), indent=2)}")

    return "\n".join(result)


@mcp.tool()
async def cancel_job(ctx: Context, job_id: str) -> str:
    """Delete a specific job.

    Args:
        job_id: ID of the job to cancel

    Returns:
        String containing the response from the job cancellation
    """
    client = ctx.request_context.lifespan_context.client

    try:
        response = await client.jobs.cancel_job_async(
            request=CancelJobRequest(job_id=job_id),
        )
        return f"Job canceled successfully: {response.raw_response}"
    except Exception as e:
        return f"Error canceling job: {str(e)}"


@mcp.tool()
async def list_workflows_with_finished_jobs(
    ctx: Context,
    source_type: Optional[SourceConnectorType | str] = None,
    destination_type: Optional[DestinationConnectorType | str] = None,
) -> str:
    """
    List workflows with finished jobs via the Unstructured API.
    Args:
        source_type: Optional source connector type to filter by
        destination_type: Optional destination connector type to filter by
    Returns:
        String containing the list of workflows with finished jobs and source and destination
        details
    """
    if source_type:
        try:
            source_type = (
                SourceConnectorType(source_type) if isinstance(source_type, str) else source_type
            )
        except KeyError:
            return f"Invalid source type: {source_type}"
    if destination_type:
        try:
            destination_type = (
                DestinationConnectorType(destination_type)
                if isinstance(destination_type, str)
                else destination_type
            )
        except KeyError:
            return f"Invalid destination type: {destination_type}"

    client = ctx.request_context.lifespan_context.client
    try:
        workflows_details = await gather_workflows_details(client=client)
    except Exception as e:
        return f"Error retrieving workflows: {str(e)}"

    filtered_workflows_details = []

    for workflow_details in workflows_details:
        updated_workflow_details = deepcopy(workflow_details)

        if source_type:
            updated_workflow_details.sources = [
                source for source in workflow_details.sources if source.type == source_type
            ]

        if destination_type:
            updated_workflow_details.destinations = [
                destination
                for destination in workflow_details.destinations
                if destination.type == destination_type
            ]

        updated_workflow_details.jobs = [
            job for job in workflow_details.jobs if job.status == JobStatus.COMPLETED
        ]

        if (
            updated_workflow_details.sources
            and updated_workflow_details.destinations
            and updated_workflow_details.jobs
        ):
            filtered_workflows_details.append(updated_workflow_details)

    if not filtered_workflows_details:
        return "No workflows found with finished jobs"

    result = ["Workflows:"]
    for workflow_details in filtered_workflows_details:
        result.append(f"- Name: {workflow_details.workflow.name}")
        result.append(f"  ID: {workflow_details.workflow.id}")
        result.append("  Sources:")
        for source in workflow_details.sources:
            result.append(f"    - {source.name} (ID: {source.id})")
            for key, value in source.config:
                result.append(f"      {key}: {value}")

        result.append("  Destinations:")
        for destination in workflow_details.destinations:
            result.append(f"    - {destination.name} (ID: {destination.id})")
            for key, value in destination.config:
                result.append(f"      {key}: {value}")

    return "\n".join(result)


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


class WorkflowDetails(BaseModel):
    workflow: WorkflowInformation
    jobs: list[JobInformation]
    sources: list[SourceConnectorInformation]
    destinations: list[DestinationConnectorInformation]


async def gather_workflows_details(client: UnstructuredClient) -> list[WorkflowDetails]:
    workflows, jobs, sources, destinations = await asyncio.gather(
        client.workflows.list_workflows_async(request=ListWorkflowsRequest()),
        client.jobs.list_jobs_async(request=ListJobsRequest()),
        client.sources.list_sources_async(request=ListSourcesRequest()),
        client.destinations.list_destinations_async(request=ListDestinationsRequest()),
    )
    workflows: list[WorkflowInformation] = workflows.response_list_workflows
    jobs: list[JobInformation] = jobs.response_list_jobs
    sources: list[SourceConnectorInformation] = sources.response_list_sources
    destinations: list[DestinationConnectorInformation] = destinations.response_list_destinations

    workflow_id_to_jobs = {
        workflow_id: list(grouped_jobs)
        for workflow_id, grouped_jobs in groupby(jobs, lambda x: x.workflow_id)
    }
    source_id_to_source_info = {source.id: source for source in sources}
    destination_id_to_destination_info = {
        destination.id: destination for destination in destinations
    }

    sorted_workflows = sorted(workflows, key=lambda x: x.updated_at, reverse=True)

    workflows_details = []

    for workflow in sorted_workflows:
        workflow_details = WorkflowDetails(
            workflow=workflow,
            jobs=list(workflow_id_to_jobs.get(workflow.id, [])),
            sources=[
                source_id_to_source_info[source_id]
                for source_id in workflow.sources
                if source_id in source_id_to_source_info
            ],
            destinations=[
                destination_id_to_destination_info[destination_id]
                for destination_id in workflow.destinations
                if destination_id in destination_id_to_destination_info
            ],
        )
        workflows_details.append(workflow_details)

    return workflows_details


def main():
    load_environment_variables()
    if len(sys.argv) < 2:
        # server is directly being invoked from client
        mcp.run(transport="stdio")
    else:
        # server is running as HTTP SSE server
        # reference: https://github.com/sidharthrajaram/mcp-sse
        mcp_server = mcp._mcp_server  # noqa: WPS437

        import argparse

        parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
        parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
        parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
        args = parser.parse_args()

        # Bind SSE request handling to MCP server
        starlette_app = create_starlette_app(mcp_server, debug=True)

        uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
