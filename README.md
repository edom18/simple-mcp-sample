# Simple MCP Feature Sample

This project includes several example implementations of MCP features.

The server script demonstrates how to set up a basic MCP server that integrates with Claude Desktop.

These server scripts also work with the simple MCP clients I developed.

# How to Verify Functionality

There are two shell scripts for launching demos: one for a single client and one for multiple clients.


## Launch the single client demo

Run `single-client-launch-demo.sh`.

```shell
$ ./single-client-launch-demo.sh
```

and then the console shows like below.

```console
Connecting to the MCP server...
Command is python
Connected to the server 'simple_server'!
Waiting for server to initialize...
Server initialized!

Connected to the server with tools:  ['reverse-text', 'uppercase']

MCP client started!

Type your queries or 'quit' to exit.

Query:
```

Please type something that you want to ask AI or `quit` to exit.

When you send a request containing `reverse text` or `upper text`, the AI will use the simple MCP server’s text-processing features.


## Launch the multi client demo

Run `multi-client-launch-demo.sh`.

```shell
$ ./multi-client-launch-demo.sh
```

and then the console shows like below.

```console
Connecting to the MCP server...
Command is python
Connected to the server 'simple_server'!
Waiting for server to initialize...
Server initialized!

Connected to the server with tools:  ['reverse-text', 'uppercase']
Connecting to the MCP server...
Command is python
Connected to the server 'profile_data_server'!
Waiting for server to initialize...
Server initialized!

Connected to the server with tools:  ['profile-data']

MultiMCP client started!

Type your queries or 'quit' to exit.

Query:
```

Please type something that you want to ask AI or `quit` to exit.

If you include `Who am I?` in your query, the AI will use the data MCP server feature to answer your question.


# Installation for Claude Desktop

Add the following settings to your Claude Desktop configuration file:

```json:for simple server
"mcpServers": {
    "simple-mcp-sample": {
        "command": "python",
        "args": [
            "/path/to/simple-mcp-sample/server/simple_server.py"
        ]
    }
}
```

```json:for data server
"mcpServers": {
    "simple-mcp-sample": {
        "command": "python",
        "args": [
            "/path/to/simple-mcp-sample/server/data_server.py"
        ]
    }
}
```

> [!NOTE]
> If you receive a `command not found` error when launching the server, specify the full path to your Python executable.