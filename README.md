# Theia MCP server

> **First draft.** The server wheel is in [`server/`](server/); the knowledgebase it ships with is inside it. Separate knowledgebase bundles are not published here yet.

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

## Give this to your AI agent

Paste this into a coding agent that can run commands on your machine, such as Claude Code, Cursor or Codex. A chat-only client (Claude Desktop, for one) cannot follow it: register the server by hand instead, as in [Quick start](#quick-start). The install link works once this repository is public with GitHub Pages serving its `main` branch, which serves the package index in [`simple/`](simple/). It names no version: a release changes nothing here.

```text
Install the Theia MCP server and register it with this agent's MCP client.

The Theia MCP server connects you to a running Theia SDK through the SDK's built-in RPC server. That RPC server is enabled in the SDK's configuration and runs only while an app has a live SDK instance, so it may not be reachable yet; setup does not need it. To get the Theia SDK, contact HarmonEyes (https://www.harmoneyes.com) for a license. The Theia MCP server itself needs no key: never ask for one.

1. Check that uv is installed (it provides uvx) by running: uvx --version
   If it is missing, install it (https://docs.astral.sh/uv/getting-started/installation/):
     Linux / macOS: curl -LsSf https://astral.sh/uv/install.sh | sh
     Windows (PowerShell): powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

2. Register a stdio MCP server named theia, at user scope where supported:
     command: uvx
     args: --index https://harmoneyes.github.io/theia-mcp-server/simple/ theia-native-mcp
   In Claude Code, that is:
     claude mcp add --scope user theia -- uvx --index https://harmoneyes.github.io/theia-mcp-server/simple/ theia-native-mcp
   If uvx is not on your PATH, use its full path.

3. Reload or restart so the server loads, then confirm its tools are listed.

4. Only if the user asked to connect to an SDK: check whether one is reachable with the health check of the SDK's RPC server, then follow the Theia MCP server's setup guidance (its instructions and the knowledgebase page setup/connecting-an-ai-agent.md).
```

The HarmonEyes dashboard offers the same prompt under Integrations ▸ Developer access, with that one license sentence pointing at the reader's API keys instead. Keep the two in step.

## Quick start

1. **Requirements:** Python 3.10 or later, and a running app with the Theia SDK's RPC server enabled.
2. **Install** the server into its own virtual environment, from the wheel in [`server/`](server/):
   ```bash
   python3 -m venv ~/.venvs/theia_native_mcp
   ~/.venvs/theia_native_mcp/bin/pip install server/theia_native_mcp-0.1.1-py3-none-any.whl
   ```
   This is a regular install: re-run it to pick up a new version. Or skip the environment and run it with `uvx`, as in [Give this to your AI agent](#give-this-to-your-ai-agent).
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

## License

Proprietary: © 2026 HarmonEyes, all rights reserved. Install and run it only to use the Theia SDK under a license agreement with HarmonEyes. See [LICENSE](LICENSE).
