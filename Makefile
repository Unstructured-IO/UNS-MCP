.PHONY: local-client
local-client:
	uv run python minimal_client/client.py uns_mcp/server.py

.PHONY: debug
debug:
	mcp dev uns_mcp/server.py

.PHONY: test-firecrawl
test-firecrawl:
	uv run pytest tests/test_firecrawl.py

.PHONY: install-pre-commit
install-pre-commit:
	uv pip install ".[dev]"
