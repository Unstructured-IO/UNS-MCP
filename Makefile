.PHONY: local-client
local-client:
	uv run python3 minimal_client/client.py uns_mcp/server.py

.PHONE: dev
dev:
	mcp dev uns_mcp/server.py
