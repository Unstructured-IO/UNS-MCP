## 0.1.3

### Enhancements

- Duplicated description of the custom workflow was removed from the tools, freeing up tokens from the LLM.
- **Delete Connector Tools Unification**: All delete tools require just the ID of the connector, so they were combined into one tool for sources and one for destinations.
- **Tools unification** - Source and destination connectors are now unified into a generic `create/update_source/destination_connector` tools.

### Fixes

## 0.1.2

### Enhancements

- Ability to run the minimal client and server separately (relies on the HTTP SSE interface)

- Neo4j Username is now ENV variable instead of being tool argument

- Added notebook with example workflow having Azure source and Neo4j destination

- **Destination connector adding**: MongoDB, Databricks Volumes, Databricks Volumes Delta Table, Pinecone

- **Source connector adding**: OneDrive, Salesforce, Sharepoint

- List all the tools in a table.

- Capability to only log request parameters to UnstructuredClient's AsyncHttpClient, no error response is logged by this mechanism.

- Adds terminal access to the minimal client using DesktopCommanderMCP

- UNS-MCP server can be installed as standalone package, thus the usage of it is simplified for non-dev users

### Fixes

- avoid client startup error if env not defined
- force server using env var from .env instead of fetching them from system first


## 0.1.1

### Enhancements

- apply typed model to `workflow_config` param in `create_workflow` func

- add better docstring into tools so that client LLM can provide better guidance to users

- enable logging capability for minimal_client and add memory history to minimal_client

- add docstrings to guide LLM how to configure Nodes when creating custom DAG workflow

- add notebooks to demonstrate end-to-end capabilities of creating connectors, combining them info workflow and executing the workflow

### Features

- Integrated firecrawl's /crawl and /llmstxt endpoint to generate and push HTML and llms.txt files to S3.

- ** Source connector adding**: azure, google drive

- ** Destination connector adding**: weaviate, astradb, neo4j

- ** Add `list_jobs`, `get_job_info`, `cancel_job` tools

### Fixes

- fix bugs for source connector config access

- refactor code to have common utility funcs


## 0.1.0

### Enhancements

### Features

- **Launch the initial version of `UNS-MCP`** that includes 14 tools and a minimal_client to interact with the server

### Fixes
