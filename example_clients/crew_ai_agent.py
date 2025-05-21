#!/usr/bin/env python3
# /// script
# dependencies = [
#   "crewai>=0.11.0",
#   "crewai-tools[mcp]>=0.0.5",
#   "pydantic>=2.11.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
Example script demonstrating how to use CrewAI with Unstructured MCP to configure sources.
This script creates a CrewAI agent that connects to the Unstructured MCP server
and configures data sources.

1. Configure UNSTRUCTURED_API_KEY, ANTHROPIC_API_KEY, AWS_KEY, AWS_SECRET keys in .env file
2. Start MCP server with:
```
make sse-server
```

3. Run example with:
```
uv run example_clients/crew_ai_agent.py
```
"""

import os
from typing import Optional

from crewai import LLM, Agent, Crew, Task
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.pretty import pprint

load_dotenv()


class SourceConfigurationResult(BaseModel):
    source_id: Optional[str] = Field(
        default=None,
        description="The ID of the configured data source",
    )
    source_type: Optional[str] = Field(
        default=None,
        description="The type of data source configured",
    )
    source_name: Optional[str] = Field(
        default=None,
        description="The name of the configured data source",
    )
    source_config: Optional[dict] = Field(
        default=None,
        description="The configuration details of the data source",
    )


def main():

    with MCPServerAdapter(
        {"url": os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8080/sse")},
    ) as tools:
        llm = LLM(model="anthropic/claude-3-opus-20240229", temperature=0.7, max_tokens=4096)

        agent = Agent(
            role="Source Configuration Specialist",
            goal="Configure and manage data sources for the MCP server",
            backstory="""You are an expert in data source configuration and management.
            You specialize in setting up and configuring various types of data sources
            including AWS S3, Google Drive, and other storage systems. You ensure
            proper configuration and validation of data sources.""",
            tools=tools,
            llm=llm,
            verbose=True,
        )

        task = Task(
            description="""Configure an S3 source with the following specifications:
            - Name: MCP-S3-Source
            - URI: s3://test/uri
            - Recursive: true
            Ensure the source is properly configured and return the configuration details.""",
            agent=agent,
            expected_output="""A result containing:
            - source_id: The ID of the configured source
            - source_config: The configuration details
            - source_name: The name of the configured source
            - source_type: The type of data source configured
            """,
            output_pydantic=SourceConfigurationResult,
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)

        result = crew.kickoff()
        pprint("Task Result:")
        pprint(result.tasks_output[0].pydantic)


if __name__ == "__main__":
    main()
