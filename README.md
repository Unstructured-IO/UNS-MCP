# Unstructured API MCP Server

An MCP server implementation for interacting with the Unstructured API. This server provides tools to list sources and workflows.

## Setup

1. Install dependencies:
- `uv add "mcp[cli]"`
- `uv pip install --upgrade unstructured-client python-dotenv`

or use `uv sync`.

2. Set your Unstructured API key as an environment variable.
   - Create a `.env` file in the root directory, and add a line with your key: `UNSTRUCTURED_API_KEY="YOUR_KEY"`

To test in local, any working key that pointing to prod env would work. However, to be able to return valid results from client's side (e.g, Claude for Desktop), your personal key that is fetched from `https://platform.unstructured.io/app/account/api-keys` is needed.

## Running the Server
Using the MCP CLI:
```bash
mcp run server.py
```

or:
```bash
uv run server.py
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

#### create_s3_source
Create an S3 source connector.

Parameters:
- `name`: Unique name for the connector
- `remote_url`: S3 URI to the bucket or folder (e.g., s3://my-bucket/)
- `key` (optional): AWS access key ID (required if not using anonymous auth)
- `secret` (optional): AWS secret access key (required if not using anonymous auth)
- `token` (optional): AWS STS session token for temporary access
- `anonymous` (optional): Whether to use anonymous authentication (default: false)
- `endpoint_url` (optional): Custom URL if connecting to a non-AWS S3 bucket
- `recursive` (optional): Whether to access subfolders within the bucket (default: false)

#### update_s3_source
Update an existing S3 source connector.

Parameters:
- `source_id`: ID of the source connector to update
- `remote_url` (optional): Updated S3 URI to the bucket or folder
- `key` (optional): Updated AWS access key ID
- `secret` (optional): Updated AWS secret access key
- `token` (optional): Updated AWS STS session token
- `anonymous` (optional): Whether to use anonymous authentication
- `endpoint_url` (optional): Updated custom URL
- `recursive` (optional): Updated subfolder access setting

#### delete_s3_source
Delete an S3 source connector.

Parameters:
- `source_id`: ID of the source connector to delete

#### invoke_firecrawl
Start an asynchronous web crawl job using Firecrawl.

Parameters:
- `url`: URL to crawl
- `api_key`: Firecrawl API key
- `s3_uri`: S3 URI where results will be uploaded (e.g., s3://my-bucket/folder/)
- `limit` (optional): Maximum number of pages to crawl (default: 100)

#### check_crawl_status
Check the status of an existing Firecrawl crawl job.

Parameters:
- `crawl_id`: ID of the crawl job to check
- `api_key`: Firecrawl API key

#### wait_for_crawl_completion
Poll a Firecrawl crawl job until completion and upload results to S3. 

Parameters:
- `crawl_id`: ID of the crawl job to monitor
- `s3_uri`: S3 URI where results will be uploaded. The crawl job ID will be appended directly to this URI
- `poll_interval` (optional): How often to check job status in seconds (default: 30)
- `timeout` (optional): Maximum time to wait in seconds (default: 3600)
- `api_key`: Firecrawl API key

Returns:
- A dictionary with crawl statistics and S3 upload information including:
  - Number of successfully uploaded files
  - Number of failed uploads
  - Total bytes uploaded
  - Original crawl job statistics

### Destinations

#### list_destinations
Lists available destinations from the Unstructured API.

Parameters:
- `destination_type` (optional): Filter destinations by connector type

#### get_destination_info
Get detailed information about a specific destination connector.

Parameters:
- `destination_id`: ID of the destination connector to get information for

#### create_s3_destination
Create an S3 destination connector.

Parameters:
- `name`: Unique name for the connector
- `remote_url`: S3 URI to the bucket or folder (e.g., s3://my-bucket/)
- `key`: AWS access key ID
- `secret`: AWS secret access key
- `token` (optional): AWS STS session token for temporary access
- `endpoint_url` (optional): Custom URL if connecting to a non-AWS S3 bucket

#### update_s3_destination
Update an existing S3 destination connector.

Parameters:
- `destination_id`: ID of the destination connector to update
- `remote_url` (optional): Updated S3 URI to the bucket or folder
- `key` (optional): Updated AWS access key ID
- `secret` (optional): Updated AWS secret access key
- `token` (optional): Updated AWS STS session token
- `endpoint_url` (optional): Updated custom URL

#### delete_s3_destination
Delete an S3 destination connector.

Parameters:
- `destination_id`: ID of the destination connector to delete

#### create_astradb_destination
Create an AstraDB destination connector.

Parameters:
- `name`: Unique name for the connector
- `token`: The AstraDB application token
- `api_endpoint`: The AstraDB API endpoint
- `collection_name`: The name of the collection to use
- `keyspace`: The AstraDB keyspace
- `batch_size` (optional): The batch size for inserting documents (default: 20)

#### update_astradb_destination
Update an existing AstraDB destination connector.

Parameters:
- `destination_id`: ID of the destination connector to update
- `token` (optional): Updated AstraDB application token
- `api_endpoint` (optional): Updated AstraDB API endpoint
- `collection_name` (optional): Updated collection name
- `keyspace` (optional): Updated AstraDB keyspace
- `batch_size` (optional): Updated batch size for inserting documents

#### delete_astradb_destination
Delete an AstraDB destination connector.

Parameters:
- `destination_id`: ID of the destination connector to delete

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

## Claude Desktop Integration

To install in Claude Desktop:

1. Go to `~/Library/Application Support/Claude/` and create a `claude_desktop_config.json`.
2. In that file add:
```bash
{
    "mcpServers": {
        "UNS_MCP": {
            "command": "ABSOLUTE/PATH/TO/.local/bin/uv",
            "args": [
                "--directory",
                "ABSOLUTE/PATH/TO/UNS-MCP",
                "run",
                "server.py"
            ],
            "disabled": false
        }
    }
}
```
3. Restart Claude Desktop.

4. Example Issues seen from Claude Desktop.
    - You will see `No destinations found` when you query for a list of destionation connectors. Check your API key in `.env`, it needs to be your personal key in `https://platform.unstructured.io/app/account/api-keys`.

## Debugging tools

Anthropic provides `MCP Inspector` tool to debug/test your MCP server. Run the following command to spin up a debugging UI. From there, you will be able to add environment variables (pointing to your local env) on the left pane. Include your personal API key there as env var. Go to `tools`, you can test out the capabilities you add to the MCP server.
```
mcp dev server.py
```

## Running locally minimal client
```
uv run python minimal_client/run.py server.py
```
