# Source: https://modelcontextprotocol.io/quickstart/client#best-practices

import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Optional

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from rich import print

configure_logging("DEBUG")

logger = get_logger(__name__)
loggers_to_mute = [
    "anthropic",
    "httpcore",
    "requests",
    "urllib3",
    "httpx",
    "botocore",
    "PIL",
]
for logger_name in loggers_to_mute:
    logging.getLogger(logger_name).setLevel(logging.WARNING)
load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.history = []
        self.available_tools = []

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write),
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Connected to server with tools: {[tool.name for tool in tools]}")

        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        self.available_tools = available_tools

    async def process_query(self, query: str) -> None:
        """Process a query using Claude and available tools"""
        self.history.append({"role": "user", "content": query})

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=self.history,
            tools=self.available_tools,
        )
        logger.debug(f"Model response: {response}")
        content_to_process = response.content

        max_loops = 5
        loop_number = 0

        while content_to_process:

            loop_number += 1
            if loop_number > max_loops:
                break

            content_item = content_to_process.pop(0)
            self.history.append({"role": "assistant", "content": [content_item]})

            if content_item.type == "text":
                print(f"\n[bold red]ASSISTANT[/bold red]\n{content_item.text}")
            elif content_item.type == "tool_use":

                tool_name = content_item.name
                tool_args = content_item.input

                print(f"\n[bold cyan]TOOL CALL[/bold cyan]\n{tool_name} with args {tool_args}\n")

                result = await self.session.call_tool(tool_name, tool_args)
                logger.debug(f"TOOL result: {result}")

                for result_item in result.content:
                    print(f"\n[bold cyan]TOOL OUTPUT[/bold cyan]:\n{result_item.text}\n")

                self.history.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content_item.id,
                                "content": result.content,
                            },
                        ],
                    },
                )

                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=self.history,
                    tools=self.available_tools,
                )
                logger.debug(f"ASSISTANT response: {response}")

                content_to_process.extend(response.content)

        return

    async def chat_loop(self):
        """Run an interactive chat loop"""
        logger.info("MCP Client Started!")
        logger.info("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                await self.process_query(query)
            except Exception as e:
                logger.error(f"Error: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
