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

| Tool | Description |
|------|-------------|
| `list_sources` | Lists available sources from the Unstructured API. |
| `get_source_info` | Get detailed information about a specific source connector. |
| `create_[connector]_source` | Create a source connector. Currently, we have s3/google drive/azure connectors (more to come!) |
| `update_[connector]_source` | Update an existing source connector by params. |
| `delete_[connector]_source` | Delete a source connector by source id. |
| `list_destinations` | Lists available destinations from the Unstructured API. |
| `get_destination_info` | Get detailed info about a specific destination connector. Currently, we have s3/weaviate/astra/neo4j/mongo DB (more to come!) |
| `create_[connector]_destination` | Create a destination connector by params. |
| `update_[connector]_destination` | Update an existing destination connector by destination id. |
| `delete_[connector]_destination` | Delete a destination connector by destination id. |
| `list_workflows` | Lists workflows from the Unstructured API. |
| `get_workflow_info` | Get detailed information about a specific workflow. |
| `create_workflow` | Create a new workflow with source, destination id, etc. |
| `run_workflow` | Run a specific workflow with workflow id |
| `update_workflow` | Update an existing workflow by params. |
| `delete_workflow` | Delete a specific workflow by id. |
| `list_jobs` | Lists jobs for a specific workflow from the Unstructured API. |
| `get_job_info` | Get detailed information about a specific job by job id. |
| `cancel_job` |Delete a specific job by id. |

Below is a list of connectors the `UNS-MCP` server currently supports, please see the full list of source connectors that Unstructured platform supports [here](https://docs.unstructured.io/api-reference/workflow/sources/overview) and destination list [here](https://docs.unstructured.io/api-reference/workflow/destinations/overview). We are planning on adding more!

| Source | Destination |
|------|-------------|
| S3 | S3 |
| Azure | Weaviate |
| Google Drive | Pinecone |
| OneDrive | AstraDB |
| Salesforce | MongoDB |
| Sharepoint | Neo4j|
| | Databricks Volumes|
|  | Databricks Volumes Delta Table |


To use the tool that creates/updates/deletes a connector, the credentials for that specific connector must be defined in your .env file. Below is the list of `credentials` for the connectors we support:

| Credential Name | Description |
|------|-------------|
| `ANTHROPIC_API_KEY` | required to run the `minimal_client` to interact with our server. |
| `AWS_KEY`, `AWS_SECRET`| required to create S3 connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/api-reference/workflow/sources/s3) and [here](https://docs.unstructured.io/api-reference/workflow/destinations/s3) |
| `WEAVIATE_CLOUD_API_KEY` | required to create Weaviate vector db connector, see how in [documentation](https://docs.unstructured.io/api-reference/workflow/destinations/weaviate) |
| `FIRECRAWL_API_KEY` | required to use Firecrawl tools in `external/firecrawl.py`, sign up on [Firecrawl](https://www.firecrawl.dev/) and get an API key. |
| `ASTRA_DB_APPLICATION_TOKEN`, `ASTRA_DB_API_ENDPOINT` | required to create Astradb connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/astradb)|
| `AZURE_CONNECTION_STRING`| required option 1 to create Azure connector via ``uns-mcp`` server, see how in [documentation](https://docs.unstructured.io/ui/sources/azure-blob-storage) |
| `AZURE_ACCOUNT_NAME`+`AZURE_ACCOUNT_KEY`| required option 2 to create Azure connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/sources/azure-blob-storage)|
| `AZURE_ACCOUNT_NAME`+`AZURE_SAS_TOKEN` | required option 3 to create Azure connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/sources/azure-blob-storage) |
| `NEO4J_PASSWORD` | required to create Neo4j connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/neo4j) |
| `MONGO_DB_CONNECTION_STRING` | required to create Mongodb connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/mongodb) |
| `GOOGLEDRIVE_SERVICE_ACCOUNT_KEY` | a string value. The original server account key (follow [documentation](https://docs.unstructured.io/ui/sources/google-drive)) is in json file, run `cat /path/to/google_service_account_key.json | base64` in terminal to get the string value  |
| `DATABRICKS_CLIENT_ID`,`DATABRICKS_CLIENT_SECRET` | required to create Databricks volume/delta table connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/databricks-volumes) and [here](https://docs.unstructured.io/ui/destinations/databricks-delta-table) |
| `ONEDRIVE_CLIENT_ID`, `ONEDRIVE_CLIENT_CRED`,`ONEDRIVE_TENANT_ID`| required to create One Drive connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/onedrive) |
| `PINECONE_API_KEY` | required to create Pinecone vector DB connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/destinations/pinecone) |
| `SALESFORCE_CONSUMER_KEY`,`SALESFORCE_PRIVATE_KEY` | required to create salesforce source connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ingestion/source-connectors/salesforce)|
| `SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_CRED`,`SHAREPOINT_TENANT_ID`| required to create One Drive connector via `uns-mcp` server, see how in [documentation](https://docs.unstructured.io/ui/sources/sharepoint) |
| `LOG_LEVEL` | Used to set logging level for our `minimal_client`, e.g. set to ERROR to get everything  |
| `CONFIRM_TOOL_USE` | set to true so that `minimal_client` can confirm execution before each tool call |
| `DEBUG_API_REQUESTS` | set to true so that `uns_mcp/server.py` can output request parameters for better debugging |


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

## VS Code Integration

For one-click installation, click one of the install buttons below:

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=uns-mcp&config=%7B%22command%22%3A%22uv%22%2C%22args%22%3A%5B%22run%22%2C%22server.py%22%5D%2C%22env%22%3A%7B%22UNSTRUCTURED_API_KEY%22%3A%22%24%7Binput%3AapiKey%7D%22%7D%7D&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22apiKey%22%2C%22description%22%3A%22Unstructured+API+Key%22%2C%22password%22%3Atrue%7D%5D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=uns-mcp&config=%7B%22command%22%3A%22uv%22%2C%22args%22%3A%5B%22run%22%2C%22server.py%22%5D%2C%22env%22%3A%7B%22UNSTRUCTURED_API_KEY%22%3A%22%24%7Binput%3AapiKey%7D%22%7D%7D&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22apiKey%22%2C%22description%22%3A%22Unstructured+API+Key%22%2C%22password%22%3Atrue%7D%5D&quality=insiders)

### Manual Installation

For manual installation, first make sure you've installed all dependencies as described in the Setup section above.

Add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "apiKey",
        "description": "Unstructured API Key",
        "password": true
      }
    ],
    "servers": {
      "uns-mcp": {
        "command": "uv",
        "args": ["run", "server.py"],
        "env": {
          "UNSTRUCTURED_API_KEY": "${input:apiKey}"
        }
      }
    }
  }
}
```

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "apiKey",
      "description": "Unstructured API Key",
      "password": true
    }
  ],
  "servers": {
    "uns-mcp": {
      "command": "uv",
      "args": ["run", "server.py"],
      "env": {
        "UNSTRUCTURED_API_KEY": "${input:apiKey}"
      }
    }
  }
}
```

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
                "ABSOLUTE/PATH/TO/YOUR-UNS-MCP-REPO/uns_mcp",
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

If you need to log request call parameters to `UnstructuredClient`, set the environment variable `DEBUG_API_REQUESTS=false`.
The logs are stored in a file with the format `unstructured-client-{date}.log`, which can be examined to debug request call parameters to `UnstructuredClient` functions.

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

## Running locally minimal client, accessing local the MCP server over HTTP + SSE

The main difference here is it becomes easier to set breakpoints on the server side during development -- the client and server are decoupled.

```
# in one terminal, run the server:
uv run python uns_mcp/server.py --host 127.0.0.1 --port 8080

or
make sse-server

# in another terminal, run the client:
uv run python minimal_client/client.py "http://127.0.0.1:8080/sse"

or
make sse-client
```

Hint: `ctrl+c` out of the client first, then the server. Otherwise the server appears to hang.

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

## CHANGELOG.md

Any new developed features/fixes/enhancements will be added to CHANGELOG.md. 0.x.x-dev pre-release format is preferred before we bump to a stable version.
