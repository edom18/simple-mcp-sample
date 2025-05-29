import os
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self, server_name: str):
        """
        Initialize session and client objects.
        """
        self.server_name = server_name
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.tools: list[dict] = []

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """

        print("Connecting to the MCP server...")

        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or a .js file.")
        
        command = "python" if is_python else "node"
        print(f"Command is {command}")

        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        print(f"Connected to the server '{self.server_name}'!")
        print("Waiting for server to initialize...")

        await self.session.initialize()

        print("Server initialized!")

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to the server with tools: ", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """
        Process a query using Claude and available tools
        """
        messages = [
            {
                "role": "user",
                "content": query,
            },
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, "text") and content.text:
                    messages.append({
                        "role": "assistant",
                        "content": content.text,
                    })

                messages.append({
                    "role": "user",
                    "content": result.content,
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """
        Run an interactive chat loop
        """
        print("\nMCP client started!")
        print("\nType your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nChat Error: {str(e)}")

    async def cleanup(self):
        """
        Clean up resources
        """
        await self.exit_stack.aclose()

async def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python single-client.py <server_name> <server_script_path>")
        sys.exit(1)

    try:
        server_name = sys.argv[1]
        server_script_path = sys.argv[2]

        client = MCPClient(server_name)
        await client.connect_to_server(server_script_path)
        await client.chat_loop()

    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
