# Unstructured API MCP Server Makefile

.PHONY: local-client
local-client:
	uv run python3 minimal_client/run.py uns_mcp/run.py

.PHONY: dev
dev:
	mcp dev server.py

.PHONY: test-firecrawl
test-firecrawl:
	uv run pytest tests/test_firecrawl.py
