from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as MCPTypes
import mcp.server.stdio
import asyncio

server = Server("SimpleMCPServer")

@server.list_tools()
async def handle_list_tools() -> list[MCPTypes.Tool]:
    """
    List available tools for simple text operations.
    """

    return [
        MCPTypes.Tool(
            name="reverse-text",
            description="Reverse the input text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to reverse",
                    },
                },
                "required": ["text"],
            },
        ),
        MCPTypes.Tool(
            name="uppercase",
            description="Modify input text to upper case.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to uppercase",
                    },
                },
                "required": ["text"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[MCPTypes.TextContent]:
    """
    Handle tool execution requests
    """
    
    if not arguments:
        raise ValueError("Missing arguments")

    text = arguments.get("text")
    if not text:
        return [MCPTypes.TextContent(type="text", text="Error: Missing text parameter")]

    if name == "reverse-text":
        result = text[::-1]
    elif name == "uppercase":
        result = text.upper()
    else:
        raise ValueError(f"Unknown tool {name}")

    return [MCPTypes.TextContent(type="text", text=result)]

async def main():
    print("Launcing an MCP server...")

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="SimpleMCPServer",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())