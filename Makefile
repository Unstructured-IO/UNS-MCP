.PHONY: local-client
local-client:
	uv run python3 minimal_client/client.py uns_mcp/server.py

.PHONE: debug
dev:
	mcp dev uns_mcp/server.py
