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

### list_sources
Lists available sources from the Unstructured API.

Parameters:
- `source_type` (optional): Filter sources by connector type

### list_workflows
Lists workflows from the Unstructured API.

Parameters:
- `destination_id` (optional): Filter by destination connector ID
- `source_id` (optional): Filter by source connector ID
- `status` (optional): Filter by workflow status

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
