# Unstructured API MCP Server

An MCP server implementation for interacting with the Unstructured API. This server provides tools to list sources and workflows.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Unstructured API key as an environment variable:
```bash
export UNSTRUCTURED_API_KEY="your-api-key-here"
```

## Running the Server

```bash
python server.py
```

Or using the MCP CLI:
```bash
mcp run server.py
```

## Available Tools

### Sources

#### list_sources
Lists available sources from the Unstructured API.

Parameters:
- `source_type` (optional): Filter sources by connector type

#### get_source_info
Get detailed information about a specific source connector.

Parameters:
- `source_id`: ID of the source connector to get information for

### Destinations

#### list_destinations
Lists available destinations from the Unstructured API.

Parameters:
- `destination_type` (optional): Filter destinations by connector type

#### get_destination_info
Get detailed information about a specific destination connector.

Parameters:
- `destination_id`: ID of the destination connector to get information for

### Workflows

#### list_workflows
Lists workflows from the Unstructured API.

Parameters:
- `destination_id` (optional): Filter by destination connector ID
- `source_id` (optional): Filter by source connector ID
- `status` (optional): Filter by workflow status

#### get_workflow_info
Get detailed information about a specific workflow.

Parameters:
- `workflow_id`: ID of the workflow to get information for

#### create_workflow
Create a new workflow.

Parameters:
- `workflow_config`: Dictionary containing the workflow configuration (must include required fields as per CreateWorkflow model)

#### run_workflow
Run a specific workflow.

Parameters:
- `workflow_id`: ID of the workflow to run

#### update_workflow
Update an existing workflow.

Parameters:
- `workflow_id`: ID of the workflow to update
- `workflow_config`: Dictionary containing the updated workflow configuration (must include required fields as per UpdateWorkflow model)

#### delete_workflow
Delete a specific workflow.

Parameters:
- `workflow_id`: ID of the workflow to delete

## Development

For development and testing, use the MCP Inspector:
```bash
mcp dev server.py
```

## Claude Desktop Integration

To install in Claude Desktop:
```bash
mcp install server.py --name "Unstructured API"
```
