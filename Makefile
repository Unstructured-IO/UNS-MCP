.PHONY: local-client
local-client:
	uv run python3 minimal_client/run.py uns_mcp/run.py

.PHONE: dev
dev:
	mcp dev uns_mcp/run.py
