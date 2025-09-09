.PHONY: debug
debug:
	mcp dev uns_mcp/server.py

.PHONY: sse-client
sse-client:
	uv run python minimal_client/client.py "http://127.0.0.1:8080/sse"

.PHONY: sse-client-terminal
sse-client-terminal:
	uv run python minimal_client/client.py "http://127.0.0.1:8080/sse" "@wonderwhy-er/desktop-commander@^0.2.11"

.PHONY: sse-server
sse-server:
	uv run python uns_mcp/server.py --host 127.0.0.1 --port 8080

.PHONY: test-firecrawl
test-firecrawl:
	uv run pytest tests/test_firecrawl.py

.PHONY: install-pre-commit
install-pre-commit:
	uv pip install ".[dev]"

.PHONY: uv-lock-update
uv-lock-update:
	@rm -f uv.lock
	@env -u UV_INDEX_URL -u PIP_EXTRA_INDEX_URL uv lock --index-url https://pypi.org/simple/ --no-cache
