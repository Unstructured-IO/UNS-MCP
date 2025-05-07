# Unstructured API MCP Server

An MCP server implementation for interacting with the Unstructured API. This server provides tools to list sources and workflows.

## Available Tools

| Tool                                | Description                                                                                                      |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `list_sources`                      | Lists available sources from the Unstructured API.                                                               |
| `get_source_info`                   | Get detailed information about a specific source connector.                                                      |
| `create_source_connector`           | Create a source connector.)                                                                                      |
| `update_source_connector`           | Update an existing source connector by params.                                                                   |
| `delete_source_connector`           | Delete a source connector by source id.                                                                          |
| `list_destinations`                 | Lists available destinations from the Unstructured API.                                                          |
| `get_destination_info`              | Get detailed info about a specific destination connector                                                         |
| `create_destination_connector`      | Create a destination connector by params.                                                                        |
| `update_destination_connector`      | Update an existing destination connector by destination id.                                                      |
| `delete_destination_connector`      | Delete a destination connector by destination id.                                                                |
| `list_workflows`                    | Lists workflows from the Unstructured API.                                                                       |
| `get_workflow_info`                 | Get detailed information about a specific workflow.                                                              |
| `create_workflow`                   | Create a new workflow with source, destination id, etc.                                                          |
| `run_workflow`                      | Run a specific workflow with workflow id                                                                         |
| `update_workflow`                   | Update an existing workflow by params.                                                                           |
| `delete_workflow`                   | Delete a specific workflow by id.                                                                                |
| `list_jobs`                         | Lists jobs for a specific workflow from the Unstructured API.                                                    |
| `get_job_info`                      | Get detailed information about a specific job by job id.                                                         |
| `cancel_job`                        | Delete a specific job by id.                                                                                     |
| `list_workflows_with_finished_jobs` | Lists all workflows that have any completed job, together with information about source and destination details. |

Below is a list of connectors the `UNS-MCP` server currently supports, please see the full list of source connectors that Unstructured platform supports [here](https://docs.unstructured.io/api-reference/workflow/sources/overview) and destination list [here](https://docs.unstructured.io/api-reference/workflow/destinations/overview). We are planning on adding more!

| Source       | Destination                    |
|--------------|--------------------------------|
| S3           | S3                             |
| Azure        | Weaviate                       |
| Google Drive | Pinecone                       |
| OneDrive     | AstraDB                        |
| Salesforce   | MongoDB                        |
| Sharepoint   | Neo4j                          |
|              | Databricks Volumes             |
|              | Databricks Volumes Delta Table |


To use the tool that creates/updates/deletes a connector, the credentials for that specific connector must be defined in your .env file. Below is the list of `credentials` for the connectors we support:

| Credential Name                                                         | Description                                                                                                                                                                                                                                                     |
|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ANTHROPIC_API_KEY`                                                     | required to run the `minimal_client` to interact with our server.                                                                                                                                                                                               |
| `AWS_KEY`, `AWS_SECRET`                                                 | required to create S3 connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/api-reference/workflow/sources/s3) and [here](https://docs.unstructured.io/api-reference/workflow/destinations/s3)                                |
| `WEAVIATE_CLOUD_API_KEY`                                                | required to create Weaviate vector db connector, see how in [documentation](https://docs.unstructured.io/api-reference/workflow/destinations/weaviate)                                                                                                          |
| `FIRECRAWL_API_KEY`                                                     | required to use Firecrawl tools in `external/firecrawl.py`, sign up on [Firecrawl](https://www.firecrawl.dev/) and get an API key.                                                                                                                              |
| `ASTRA_DB_APPLICATION_TOKEN`, `ASTRA_DB_API_ENDPOINT`                   | required to create Astradb connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/astradb)                                                                                                                     |
| `AZURE_CONNECTION_STRING`                                               | required option 1 to create Azure connector via ``uns-mcp`` server, see how in [documentation](https://docs.unstructured.io/ui/sources/azure-blob-storage)                                                                                                      |
| `AZURE_ACCOUNT_NAME`+`AZURE_ACCOUNT_KEY`                                | required option 2 to create Azure connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/sources/azure-blob-storage)                                                                                                        |
| `AZURE_ACCOUNT_NAME`+`AZURE_SAS_TOKEN`                                  | required option 3 to create Azure connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/sources/azure-blob-storage)                                                                                                        |
| `NEO4J_PASSWORD`                                                        | required to create Neo4j connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/neo4j)                                                                                                                         |
| `MONGO_DB_CONNECTION_STRING`                                            | required to create Mongodb connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/mongodb)                                                                                                                     |
| `GOOGLEDRIVE_SERVICE_ACCOUNT_KEY`                                       | a string value. The original server account key (follow [documentation](https://docs.unstructured.io/ui/sources/google-drive)) is in json file, run `base64 < /path/to/google_service_account_key.json` in terminal to get the string value                     |
| `DATABRICKS_CLIENT_ID`,`DATABRICKS_CLIENT_SECRET`                       | required to create Databricks volume/delta table connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/databricks-volumes) and [here](https://docs.unstructured.io/ui/destinations/databricks-delta-table)    |
| `ONEDRIVE_CLIENT_ID`, `ONEDRIVE_CLIENT_CRED`,`ONEDRIVE_TENANT_ID`       | required to create One Drive connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/onedrive)                                                                                                                  |
| `PINECONE_API_KEY`                                                      | required to create Pinecone vector DB connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/pinecone)                                                                                                         |
| `SALESFORCE_CONSUMER_KEY`,`SALESFORCE_PRIVATE_KEY`                      | required to create salesforce source connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ingestion/source-connectors/salesforce)                                                                                            |
| `SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_CRED`,`SHAREPOINT_TENANT_ID` | required to create One Drive connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/sources/sharepoint)                                                                                                                     |
| `LOG_LEVEL`                                                             | Used to set logging level for our `minimal_client`, e.g. set to ERROR to get everything                                                                                                                                                                         |
| `CONFIRM_TOOL_USE`                                                      | set to true so that `minimal_client` can confirm execution before each tool call                                                                                                                                                                                |
| `DEBUG_API_REQUESTS`                                                    | set to true so that `uns_mcp/server.py` can output request parameters for better debugging                                                                                                                                                                      |


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

## Installation & Configuration

This guide provides step-by-step instructions to set up and configure the UNS_MCP server using Python 3.12 and the `uv` tool.

## Prerequisites
- Python 3.12+
- `uv` for environment management
- An API key from Unstructured. You can sign up and obtain your API key [here](https://platform.unstructured.io/app/account/api-keys).

### Using `uv` (Recommended)

No additional installation is required when using `uvx` as it handles execution. However, if you prefer to install the package directly:
```bash
uv pip install uns_mcp
```

#### Configure Claude Desktop
For integration with Claude Desktop, add the following content to your `claude_desktop_config.json`:

**Note:** The file is located in the `~/Library/Application Support/Claude/` directory.

**Using `uvx` Command:**
```json
{
   "mcpServers": {
      "UNS_MCP": {
         "command": "uvx",
         "args": ["uns_mcp"],
         "env": {
           "UNSTRUCTURED_API_KEY": "<your-key>"
         }
      }
   }
}
```

**Alternatively, Using Python Package:**
```json
{
   "mcpServers": {
      "UNS_MCP": {
         "command": "python",
         "args": ["-m", "uns_mcp"],
         "env": {
           "UNSTRUCTURED_API_KEY": "<your-key>"
         }
      }
   }
}
```

### Using Source Code
1. Clone the repository.

2. Install dependencies:
    ```bash
    uv sync
    ```

3. Set your Unstructured API key as an environment variable. Create a .env file in the root directory with the following content:
    ````bash
    UNSTRUCTURED_API_KEY="YOUR_KEY"
    ````
    Refer to `.env.template` for the configurable environment variables.

You can now run the server using one of the following methods:

<details>
<summary>
Using Editable Package Installation
</summary>
Install as an editable package:

```bash
uvx pip install -e .
```

Update your Claude Desktop config:
```json
{
  "mcpServers": {
    "UNS_MCP": {
      "command": "uvx",
      "args": ["uns_mcp"]
    }
  }
}
```
**Note**: Remember to point to the uvx executable in environment where you installed the package

</details>

<details>
<summary>
Using SSE Server Protocol
</summary>

**Note: Not supported by Claude Desktop.**

For SSE protocol, you can debug more easily by decoupling the client and server:

1. Start the server in one terminal:
    ```bash
    uv run python uns_mcp/server.py --host 127.0.0.1 --port 8080
    # or
    make sse-server
    ```

2. Test the server using a local client in another terminal:
   ```bash
   uv run python minimal_client/client.py "http://127.0.0.1:8080/sse"
   # or
   make sse-client
   ```
**Note:** To stop the services, use `Ctrl+C` on the client first, then the server.
</details>

<details>
<summary>
Using Stdio Server Protocol
</summary>

Configure Claude Desktop to use stdio:
```json
{
  "mcpServers": {
    "UNS_MCP": {
      "command": "ABSOLUTE/PATH/TO/.local/bin/uv",
      "args": [
        "--directory",
        "ABSOLUTE/PATH/TO/YOUR-UNS-MCP-REPO/uns_mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```
Alternatively, run the local client:
```bash
uv run python minimal_client/client.py uns_mcp/server.py
```
</details>

## Additional Local Client Configuration
Configure the minimal client using environmental variables:
- `LOG_LEVEL="ERROR"`: Set to suppress debug outputs from the LLM, displaying clear messages for users.
- `CONFIRM_TOOL_USE='false'`: Disable tool use confirmation before execution. **Use with caution**, especially during development, as LLM may execute expensive workflows or delete data.


#### Debugging tools

Anthropic provides `MCP Inspector` tool to debug/test your MCP server. Run the following command to spin up a debugging UI. From there, you will be able to add environment variables (pointing to your local env) on the left pane. Include your personal API key there as env var. Go to `tools`, you can test out the capabilities you add to the MCP server.
```
mcp dev uns_mcp/server.py
```

If you need to log request call parameters to `UnstructuredClient`, set the environment variable `DEBUG_API_REQUESTS=false`.
The logs are stored in a file with the format `unstructured-client-{date}.log`, which can be examined to debug request call parameters to `UnstructuredClient` functions.


## Add terminal access to minimal client
We are going to use [@wonderwhy-er/desktop-commander](https://github.com/wonderwhy-er/DesktopCommanderMCP) to add terminal access to the minimal client. It is built on the MCP Filesystem Server. Be careful, as the client (also LLM) now **has access to private files.**

Execute the following command to install the package:
```bash
npx @wonderwhy-er/desktop-commander setup
```

Then start client with extra parameter:

```bash
uv run python minimal_client/client.py "http://127.0.0.1:8080/sse" "@wonderwhy-er/desktop-commander"
# or
make sse-client-terminal
```

## Using subset of tools
If your client supports using only subset of tools here are the list of things you should be aware:
- `update_workflow` tool has to be loaded in the context together with `create_workflow` tool, because it contains detailed description on how to create and configure custom node.

## Known issues
- `update_workflow` - needs to have in context the configuration of the workflow it is updating either by providing it by the user or by calling `get_workflow_info` tool, as this tool doesn't work as `patch` applier, it fully replaces the workflow config.

## CHANGELOG.md

Any new developed features/fixes/enhancements will be added to CHANGELOG.md. 0.x.x-dev pre-release format is preferred before we bump to a stable version.

# Troubleshooting
- If you encounter issues with `Error: spawn <command> ENOENT` it means `<command>` is not installed or visible in your PATH:
  - Make sure to install it and add it to your PATH.
  - or provide absolute path to the command in the `command` field of your config. So for example replace `python` with `/opt/miniconda3/bin/python`
