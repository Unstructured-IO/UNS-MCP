import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from unstructured_client import UnstructuredClient
from unstructured_client.models.operations import (
    CreateWorkflowRequest,
    DeleteWorkflowRequest,
    GetDestinationRequest,
    GetSourceRequest,
    GetWorkflowRequest,
    ListDestinationsRequest,
    ListSourcesRequest,
    ListWorkflowsRequest,
    RunWorkflowRequest,
    UpdateWorkflowRequest,
)
from unstructured_client.models.shared import (
    CreateWorkflow,
    DestinationConnectorType,
    SourceConnectorType,
    UpdateWorkflow,
    WorkflowState,
)
from unstructured_client.models.shared.createworkflow import CreateWorkflowTypedDict

from connectors import register_connectors

custom_nodes_settings_documentation = """
Custom workflow DAG nodes
- If WorkflowType is set to custom, you must also specify the settings for the workflow’s
directed acyclic graph (DAG) nodes. These nodes’ settings are specified in the workflow_nodes array.
- A Source node is automatically created when you specify the source_id value outside of the
workflow_nodes array.
- A Destination node is automatically created when you specify the destination_id value outside
of the workflow_nodes array.
- You can specify Partitioner, Chunker, Enrichment, and Embedder nodes.
- The order of the nodes in the workflow_nodes array will be the same order that these nodes appear
in the DAG, with the first node in the array added directly after the Source node.
The Destination node follows the last node in the array.
- Be sure to specify nodes in the allowed order. The following DAG placements are all allowed:
    - Partitioner,
    - Partitioner -> Chunker,
    - Partitioner -> Chunker -> Embedder,
    - Partitioner -> Enrichment -> Chunker,
    - Partitioner -> Enrichment -> Chunker -> Embedder

Partitioner node
A Partitioner node has a type of partition and a subtype of auto, vlm, hires, or fast.
Examples:
- auto strategy:
{
    "name": "Partitioner",
    "type": "partition",
    "subtype": "vlm",
    "settings": {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "output_format": "text/html",
        "user_prompt": null,
        "format_html": true,
        "unique_element_ids": true,
        "is_dynamic": true,
        "allow_fast": true
    }
}

- vlm strategy:
    Allowed values for provider and model include:

    "provider": "anthropic" "model": "claude-3-5-sonnet-20241022"
    "provider": "openai" "model": "gpt-4o"


- hires strategy:
{
    "name": "Partitioner",
    "type": "partition",
    "subtype": "unstructured_api",
    "settings": {
        "strategy": "hi_res",
        "include_page_breaks": <true|false>,
        "pdf_infer_table_structure": <true|false>,
        "exclude_elements": [
            "<element-name>",
            "<element-name>"
        ],
        "xml_keep_tags": <true|false>,
        "encoding": "<encoding>",
        "ocr_languages": [
            "<language>",
            "<language>"
        ],
        "extract_image_block_types": [
            "image",
            "table"
        ],
        "infer_table_structure": <true|false>
    }
}
- fast strategy
{
    "name": "Partitioner",
    "type": "partition",
    "subtype": "unstructured_api",
    "settings": {
        "strategy": "fast",
        "include_page_breaks": <true|false>,
        "pdf_infer_table_structure": <true|false>,
        "exclude_elements": [
            "<element-name>",
            "<element-name>"
        ],
        "xml_keep_tags": <true|false>,
        "encoding": "<encoding>",
        "ocr_languages": [
            "<language-code>",
            "<language-code>"
        ],
        "extract_image_block_types": [
            "image",
            "table"
        ],
        "infer_table_structure": <true|false>
    }
}


Chunker node
A Chunker node has a type of chunk and subtype of chunk_by_character or chunk_by_title.

- chunk_by_character
{
    "name": "Chunker",
    "type": "chunk",
    "subtype": "chunk_by_character",
    "settings": {
        "include_orig_elements": <true|false>,
        "new_after_n_chars": <new-after-n-chars>,
        "max_characters": <max-characters>,
        "overlap": <overlap>,
        "overlap_all": <true|false>,
        "contextual_chunking_strategy": "v1"
    }
}

- chunk_by_title
{
    "name": "Chunker",
    "type": "chunk",
    "subtype": "chunk_by_title",
    "settings": {
        "multipage_sections": <true|false>,
        "combine_text_under_n_chars": <combine-text-under-n-chars>,
        "include_orig_elements": <true|false>,
        "new_after_n_chars": <new-after-n-chars>,
        "max_characters": <max-characters>,
        "overlap": <overlap>,
        "overlap_all": <true|false>,
        "contextual_chunking_strategy": "v1"
    }
}


Enrichment node
An Enrichment node has a type of prompter and subtype of:
- openai_image_description,
- anthropic_image_description,
- bedrock_image_description,
- vertexai_image_description,
- openai_table_description,
- anthropic_table_description,
- bedrock_table_description,
- vertexai_table_description,
- openai_table2html,
- openai_ner

Example:
{
    "name": "Enrichment",
    "type": "prompter",
    "subtype": "<subtype>",
    "settings": {}
}


Embedder node
An Embedder node has a type of embed

Allowed values for subtype and model_name include:

- "subtype": "azure_openai"
    - "model_name": "text-embedding-3-small"
    - "model_name": "text-embedding-3-large"
    - "model_name": "text-embedding-ada-002"
- "subtype": "bedrock"
    - "model_name": "amazon.titan-embed-text-v2:0"
    - "model_name": "amazon.titan-embed-text-v1"
    - "model_name": "amazon.titan-embed-image-v1"
    - "model_name": "cohere.embed-english-v3"
    - "model_name": "cohere.embed-multilingual-v3"
- "subtype": "togetherai":
    - "model_name": "togethercomputer/m2-bert-80M-2k-retrieval"
    - "model_name": "togethercomputer/m2-bert-80M-8k-retrieval"
    - "model_name": "togethercomputer/m2-bert-80M-32k-retrieval"

Example:
{
    "name": "Embedder",
    "type": "embed",
    "subtype": "<subtype>",
    "settings": {
        "model_name": "<model-name>"
    }
}
"""


def add_custom_node_examples(func):
    if func.__doc__ is None:
        func.__doc__ = ""
    func.__doc__ += "\n" + custom_nodes_settings_documentation
    return func


def load_environment_variables() -> None:
    """
    Load environment variables from .env file.
    Raises an error if critical environment variables are missing.
    """
    load_dotenv()
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
        source_type = source_type.upper()  # it needs uppercase to access
        try:
            request.source_type = SourceConnectorType[source_type]
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
async def list_workflows(
    ctx: Context,
    destination_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    List workflows from the Unstructured API.

    Args:
        destination_id: Optional destination connector ID to filter by, should be valid UUID
        source_id: Optional source connector ID to filter by, should be valid UUID
        status: Optional workflow status to filter by

    Returns:
        String containing the list of workflows
    """
    client = ctx.request_context.lifespan_context.client

    request = ListWorkflowsRequest(destination_id=destination_id, source_id=source_id)

    if status:
        try:
            request.status = WorkflowState[status]
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
        destination_type = destination_type.upper()
        try:
            request.destination_type = DestinationConnectorType[destination_type]
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
@add_custom_node_examples
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
@add_custom_node_examples
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


if __name__ == "__main__":
    load_environment_variables()
    mcp.run()
