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
mcp run uns_mcp/server.py
```

or:
```bash
uv run uns_mcp/server.py
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

#### create_[connector]_source
Create a source connector. We plan on adding all the source connectors that are available in Unstructured Platform (https://platform.unstructured.io). Please refer to our CHANGELOG.md for new source connectors we are rapidly adding.

Below is example for `create_s3_source`

Parameters:
- `name`: Unique name for the connector
- `remote_url`: S3 URI to the bucket or folder (e.g., s3://my-bucket/)
- `key` (optional): AWS access key ID (required if not using anonymous auth)
- `secret` (optional): AWS secret access key (required if not using anonymous auth)
- `token` (optional): AWS STS session token for temporary access
- `anonymous` (optional): Whether to use anonymous authentication (default: false)
- `endpoint_url` (optional): Custom URL if connecting to a non-AWS S3 bucket
- `recursive` (optional): Whether to access subfolders within the bucket (default: false)

#### update_[connector]_source
Update an existing source connector. Below is an example of `update_s3_source`:

Parameters:
- `source_id`: ID of the source connector to update
- `remote_url` (optional): Updated S3 URI to the bucket or folder
- `key` (optional): Updated AWS access key ID
- `secret` (optional): Updated AWS secret access key
- `token` (optional): Updated AWS STS session token
- `anonymous` (optional): Whether to use anonymous authentication
- `endpoint_url` (optional): Updated custom URL
- `recursive` (optional): Updated subfolder access setting

#### delete_[connector]_source
Delete a source connector. Below is an example of `delete_s3_source`:

Parameters:
- `source_id`: ID of the source connector to delete

### Firecrawl Source

[Firecrawl](https://www.firecrawl.dev/) is a web crawling API that provides two main capabilities in our MCP:

1. **HTML Content Retrieval**: Using `invoke_firecrawl_crawlhtml` to start crawl jobs and `check_crawlhtml_status` to monitor them
2. **LLM-Optimized Text Generation**: Using `invoke_firecrawl_llmtxt` to generate text and `check_llmtxt_status` to retrieve results

How Firecrawl works:

**Web Crawling Process:**
- Starts with a specified URL and analyzes it to identify links
- Uses the sitemap if available; otherwise follows links found on the website
- Recursively traverses each link to discover all subpages
- Gathers content from every visited page, handling JavaScript rendering and rate limits
- Jobs can be cancelled with `cancel_crawlhtml_job` if needed
- Use this if you require all the info extracted into raw HTML, Unstructured's workflow cleans it up really well  :smile:

**LLM Text Generation:**
- After crawling, extracts clean, meaningful text content from the crawled pages
- Generates optimized text formats specifically formatted for large language models
- Results are automatically uploaded to the specified S3 location
- Note: LLM text generation jobs cannot be cancelled once started. The `cancel_llmtxt_job` function is provided for consistency but is not currently supported by the Firecrawl API.

Note: A `FIRECRAWL_API_KEY` environment variable must be set to use these functions.

### Destinations

#### list_destinations
Lists available destinations from the Unstructured API.

Parameters:
- `destination_type` (optional): Filter destinations by connector type

#### get_destination_info
Get detailed information about a specific destination connector.

Parameters:
- `destination_id`: ID of the destination connector to get information for

#### create_[connector]_destination
Create a destination connector. We plan on adding all the destination connectors that are available in Unstructured Platform (https://platform.unstructured.io). Please refer to our CHANGELOG.md for new destination connectors we are rapidly adding.

Below is an example of `create_s3_destination`:

Parameters:
- `name`: Unique name for the connector
- `remote_url`: S3 URI to the bucket or folder (e.g., s3://my-bucket/)
- `key`: AWS access key ID
- `secret`: AWS secret access key
- `token` (optional): AWS STS session token for temporary access
- `endpoint_url` (optional): Custom URL if connecting to a non-AWS S3 bucket

#### update_[connector]_destination
Update an existing destination connector. Below is an example of `update_s3_destination`:

Parameters:
- `destination_id`: ID of the destination connector to update
- `remote_url` (optional): Updated S3 URI to the bucket or folder
- `key` (optional): Updated AWS access key ID
- `secret` (optional): Updated AWS secret access key
- `token` (optional): Updated AWS STS session token
- `endpoint_url` (optional): Updated custom URL

#### delete_[connector]_destination
Delete a destination connector. Below is an example of `delete_s3_destination`:

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
- `workflow_config`: Dictionary containing the workflow configuration (must include required fields as per CreateWorkflow model). It

#### run_workflow
Run a specific workflow.

Parameters:
- `workflow_id`: ID of the workflow to run

#### update_workflow
Update an existing workflow.

Parameters:
- `workflow_id`: ID of the workflow to update
- `workflow_config`:
    A dictionary containing the updated workflow configuration (must include required fields as per UpdateWorkflow model).
    More specifically, it's a `CreateWorkflowTypedDict` that one can refer its params [here](https://github.com/Unstructured-IO/unstructured-python-client/blob/main/src/unstructured_client/models/shared/createworkflow.py#L33).


#### delete_workflow
Delete a specific workflow.

Parameters:
- `workflow_id`: ID of the workflow to delete


### Jobs

#### list_jobs

Lists jobs for a specific workflow from the Unstructured API.

Parameters:
- `workflow_id` (optional): Filter by workflow ID
- `status` (optional): Filter by job status

#### get_job_info
Get detailed information about a specific job.

Parameters:
- `job_id`: ID of the job to get information for

#### cancel_job

Delete a specific job.

Parameters:
- `job_id`: ID of the job to cancel

## Claude Desktop Integration

To install in Claude Desktop:

1. Go to `~/Library/Application Support/Claude/` and create a `claude_desktop_config.json`.
2. In that file add:
```bash
{
    "mcpServers":
    {
        "UNS_MCP":
        {
            "command": "ABSOLUTE/PATH/TO/.local/bin/uv",
            "args":
            [
                "--directory",
                "ABSOLUTE/PATH/TO/UNS-MCP",
                "run",
                "server.py"
            ],
            "env":
            [
            "UNSTRUCTURED_API_KEY":"<your key>"
            ],
            "disabled": false
        }
    }
}
```
3. Restart Claude Desktop.

4. Example Issues seen from Claude Desktop.
    - You will see `No destinations found` when you query for a list of destination connectors. Check your API key in `.env` or in your config json, it needs to be your personal key in `https://platform.unstructured.io/app/account/api-keys`.

## Debugging tools

Anthropic provides `MCP Inspector` tool to debug/test your MCP server. Run the following command to spin up a debugging UI. From there, you will be able to add environment variables (pointing to your local env) on the left pane. Include your personal API key there as env var. Go to `tools`, you can test out the capabilities you add to the MCP server.
```
mcp dev uns_mcp/server.py
```

## Running locally minimal client
```
uv run python minimal_client/client.py uns_mcp/server.py
```

or

```
make local-client
```

Env variables to configure behavior of the client:
- `LOG_LEVEL="ERROR"` # If you would like to hide outputs from the LLM and present clear messages for the user
- `CONFIRM_TOOL_USE='false'` If you would like to disable the tool use confirmation before running it (True by default). **BE MINDFUL** about that option, as LLM can decide to purge all data from your account or run some expensive workflows; use only for development purposes.

## Running locally minimal client, accessing local the MCP server over HTTP

The main difference here is it becomes easier to set breakpoints on the server side during development -- the client and server are decoupled.

```
# in one terminal, run the server:
python uns_mcp/server.py --host 127.0.0.1 --port 8080

# in another terminal, run the client:
python minimal_client/client.py "http://127.0.0.1:8080/sse"
```


## CHANGELOG.md

Any new developed features/fixes/enhancements will be added to CHANGELOG.md. 0.x.x-dev pre-release format is preferred before we bump to a stable version.
