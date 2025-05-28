# Simple MCP feature sample

This project includes some implementations of MCP feature.

The server script shows you how to implement simple MCP server. This server works with Claude Desktop.

# Installation for Claude Desktop

Add below parameter for Claude Desktop setting file.

```json
"mcpServers": {
    "simple-mcp-sample": {
        "command": "python",
        "args": [
            "/path/to/simple-mcp-sample/server/server.py"
        ]
    }
}
```

> [!NOTE]
> If you can't launch this server with command not found error, please set a python command as absolute path.