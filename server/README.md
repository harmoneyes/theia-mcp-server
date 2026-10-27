# The MCP server package

> **First draft.** The package is not in this folder yet. This page describes the current server so the folder's purpose and usage are set.

## Package

| | |
|---|---|
| Package | `theia_native_mcp` |
| Command | `theia-native-mcp` (also `python -m theia_native_mcp`) |
| Python | 3.10 or later |
| Main dependencies | the MCP Python SDK (`mcp>=2.2.0,<3`), `httpx2`, `PyYAML` |
| Ships with it | the knowledgebase bundles, the agent-facing text (server instructions, tool descriptions), and the SDK RPC certificate it trusts |

## Install

Install into its own virtual environment. The package is copied into the environment, so it does not depend on its source folder afterwards; re-run the install to pick up a new version.

Linux and macOS:

```bash
python3 -m venv ~/.venvs/theia_native_mcp
~/.venvs/theia_native_mcp/bin/pip install <path to the server package>
```

Windows:

```powershell
py -m venv $env:USERPROFILE\.venvs\theia_native_mcp
& $env:USERPROFILE\.venvs\theia_native_mcp\Scripts\pip.exe install <path to the server package>
```

## Run

| Mode | Command | Notes |
|---|---|---|
| stdio (default) | `theia-native-mcp` | The MCP client starts the server as a child process. No HTTP authentication. |
| Streamable HTTP | `THEIA_MCP_HTTP_SECRET=<secret> theia-native-mcp --http --host 127.0.0.1 --port 8765 --allowed-origin <origin>` | Serves `/mcp`. Exits with status 2 when the secret is not set. |

Command-line flags:

| Flag | Meaning | Default |
|---|---|---|
| `--http` | Serve Streamable HTTP instead of stdio | stdio |
| `--host` | HTTP bind address | `127.0.0.1` |
| `--port` | HTTP port | `8765` |
| `--allowed-origin` | An `Origin` header value HTTP accepts; repeatable | none |

## Register with an MCP client

Claude Code:

```bash
claude mcp add --scope user theia -- "$HOME/.venvs/theia_native_mcp/bin/theia-native-mcp"
```

Pass a settings file or a token by adding `-e THEIA_MCP_SETTINGS=<path>` or `-e THEIA_RPC_TOKEN=<token>` before `--`.

Settings, tokens and endpoints: [../docs/configuration.md](../docs/configuration.md).
