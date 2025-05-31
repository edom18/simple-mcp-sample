from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as MCPTypes
import mcp.server.stdio
import asyncio
import os

server = Server("DataMCPServer")

@server.list_tools()
async def handle_list_tools() -> list[MCPTypes.Tool]:
    """
    List available tools for explainging data.
    """

    return [
        MCPTypes.Tool(
            name="profile-data",
            description="Provide the user profile.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[MCPTypes.TextContent]:
    """
    Handle tool execution requests.
    """

    result = "No data."

    if name == "profile-data":
        data_path = os.path.join(os.path.dirname(__file__), "data", "data.md")
        with open(data_path, "rb") as f:
            result = f.read()
    
    return [MCPTypes.TextContent(type="text", text=result)]

async def main():
    print("Launcing an MCP server...")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="DataMCPServer",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
