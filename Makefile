.PHONY: debug
debug:
	mcp dev uns_mcp/server.py

.PHONY: sse-client
sse-client:
	uv run python minimal_client/client.py "http://127.0.0.1:8080/sse"


.PHONY: sse-client-terminal
sse-client-terminal:
	uv run python minimal_client/client.py "http://127.0.0.1:8080/sse" "@wonderwhy-er/desktop-commander"

.PHONY: sse-server
sse-server:
	uv run python uns_mcp/server.py --host 127.0.0.1 --port 8080

.PHONY: test-firecrawl
test-firecrawl:
	uv run pytest tests/test_firecrawl.py

.PHONY: install-pre-commit
install-pre-commit:
	uv pip install ".[dev]"
