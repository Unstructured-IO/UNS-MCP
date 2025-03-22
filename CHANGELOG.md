## 0.1.1-dev

### Enhancements

- apply typed model to `workflow_config` param in `create_workflow` func

- add better docstring into tools so that client LLM can provide better guidance to users

- enable logging capability for minimal_client and add memory history to minimal_client

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
