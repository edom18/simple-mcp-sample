import asyncio
from anthropic import Anthropic
from dotenv import load_dotenv
from single_client import MCPClient

load_dotenv()

class MultiMCPClient:
    def __init__(self):
        self.clients: dict[str, MCPClient] = {}
        self.anthropic = Anthropic()

    async def add_client(self, server_name: str, server_script_path: str):
        """
        Add a new MCP client connection.
        """
        client = MCPClient(server_name)
        await client.connect_to_server(server_script_path)
        self.clients[server_name] = client
    
    async def process_query(self, query: str) -> str:
        """
        Process query across all connected servers.
        """

        # Gather tools from all clients
        all_tools = []
        for client in self.clients.values():
            response = await client.session.list_tools()
            tools = [{
                "name": f"{client.server_name}-{tool.name}",
                "description": tool.description,
                "input_schema": tool.inputSchema,
            } for tool in response.tools]
            all_tools.extend(tools)

        messages = [
            {
                "role": "user",
                "content": query,
            }
        ]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=all_tools,
        )

        final_text = []
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                print(f"Tool call: {content.name} with args {content.input}")

                # Parse server name from tool name (format: "server-tool")
                tool_name = content.name
                server_name, tool_name = tool_name.split("-", 1)

                if server_name not in self.clients:
                    final_text.append(f"Error: Server '{server_name}' not found")
                    continue

                client = self.clients[server_name]
                tool_args = content.input
                
                # Execute tool call
                result = await client.session.call_tool(tool_name, tool_args)
                final_text.append(f"[{server_name}] Calling tool {tool_name} with args {tool_args}")
                final_text.append(result.content[0].text)
        
        return "\n".join(final_text)

    async def chat_loop(self):
        """
        Run intaractive caht loop.
        """
        print("\nMultiMCP client started!")
        print("\nType your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print(f"\n{response}")

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """
        Clean up all client connections.
        """
        for client in self.clients.values():
            await client.cleanup()

async def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python client.py <server1_name> <server1_script> [server2_name] [server2_script] ...")
        sys.exit(1)

    client = MultiMCPClient()
    try:
        # Add each server connection
        for i in range(1, len(sys.argv), 2):
            server_name = sys.argv[i]
            server_script = sys.argv[i + 1]
            await client.add_client(server_name, server_script)

        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())