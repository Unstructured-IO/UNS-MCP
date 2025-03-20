
.PHONY: local-client
local-client:
	uv run python3 minimal_client/run.py server.py
