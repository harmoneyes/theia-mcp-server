# Theia MCP server

> **First draft.** The server package and knowledgebase bundles are not in this repository yet; the documentation describes the current server.

The Theia MCP server lets an AI agent work with running Theia SDK instances. It connects to an SDK's RPC control surface (JSON-RPC 2.0 over HTTPS, events over SSE) and gives the agent tools to:

- connect to one or more SDK endpoints;
- discover the methods and events each endpoint offers, with their full schemas;
- call any method;
- subscribe to events such as cognitive load, fatigue, attention and mental readiness, and wait for them;
- read the Theia knowledgebase.

The server knows nothing about individual SDK methods. Everything it shows the agent comes from the endpoint's own discovery document, so an app that wraps the SDK can add, replace or remove methods, and the agent sees and uses them the same way. See [Extending the SDK's RPC](docs/extending-the-sdk-rpc.md).

## What this repository holds

| Folder | Contents |
|---|---|
| [`server/`](server/) | The MCP server package: install, run, configure |
| [`knowledgebase/`](knowledgebase/) | Knowledgebase bundles, one per Theia SDK version, and how they are released |
| [`docs/`](docs/) | Developer documentation: how the server works, the RPC protocol, extending the SDK's RPC |

## How it fits together

```
 AI agent (MCP client)
        │  MCP: stdio, or Streamable HTTP at /mcp
        ▼
 Theia MCP server ──── knowledgebase bundles
        │  HTTPS: JSON-RPC 2.0 on POST, replies as JSON, SSE streams or files
        ▼
 Theia SDK RPC endpoint
   either the SDK's own RPC server,
   or an app's endpoint that wraps it and adds its own methods
```

## Quick start

1. **Requirements:** Python 3.10 or later, and a running app with the Theia SDK's RPC server enabled.
2. **Install** the server into its own virtual environment:
   ```bash
   python3 -m venv ~/.venvs/theia_native_mcp
   ~/.venvs/theia_native_mcp/bin/pip install <path to the server package>
   ```
   This is a regular install: re-run it to pick up a new version.
3. **Register** it with your MCP client. For Claude Code:
   ```bash
   claude mcp add --scope user theia -- "$HOME/.venvs/theia_native_mcp/bin/theia-native-mcp"
   ```
   Add `-e THEIA_RPC_TOKEN=<token>` or `-e THEIA_MCP_SETTINGS=<path>` before `--` to pass a token or a settings file.
4. **Connect:** ask the agent to connect. With no endpoint given, the server looks for an SDK on this machine on ports 17420, 19420, 21420, 23420 and 25420.

Details: [server/README.md](server/README.md) and [docs/configuration.md](docs/configuration.md).

## The tools

| Tool | What it does |
|---|---|
| `connect` | Connects to an SDK endpoint (or finds the local one), opens an RPC session and reads its methods and events |
| `disconnect` | Ends the connection's RPC session and subscriptions |
| `list_connections` | Lists open connections and their state |
| `list_methods` | Lists a connection's methods and events with one-line summaries |
| `describe_method` | Gives a method's or event's full description and schemas |
| `call_method` | Calls a method with params by name |
| `get_events` | Reads buffered events from subscriptions |
| `wait_for_event` | Waits for the next matching event |
| `get_knowledgebase_index` | Lists knowledgebase pages and headings |
| `read_knowledgebase` | Reads a knowledgebase page, heading or text block |

How each works: [docs/how-the-mcp-server-works.md](docs/how-the-mcp-server-works.md).

## Access and security

- **What a token reaches is set by the SDK host.** By default a token reaches only the connection and status methods. User state (outputs, transitions, the methods that return them) and session reports must be granted per token in the SDK's RPC config, because they describe a person's eye movement and physiological state.
- **The default token `theia_mcp_default_token` is public.** Any local process that knows it can control an SDK that accepts it. Use it for development only.
- **The SDK's RPC certificate is for development and testing.** The server trusts only the certificate compiled into the SDK. Its private key ships in every SDK build, so anyone who extracts it can impersonate an SDK's RPC server.
- **HTTP mode requires a secret.** `--http` serves the MCP at `/mcp` and needs `THEIA_MCP_HTTP_SECRET`; clients send it as a bearer token.

## Documentation

- [How the MCP server works](docs/how-the-mcp-server-works.md)
- [Configuration](docs/configuration.md)
- [The SDK RPC protocol](docs/sdk-rpc-protocol.md)
- [Extending the SDK's RPC](docs/extending-the-sdk-rpc.md)
- [Knowledgebase bundles](knowledgebase/README.md)
