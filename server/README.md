# The MCP server package

> **First draft.**

## Package

| | |
|---|---|
| Wheel | [`theia_native_mcp-0.1.0-py3-none-any.whl`](theia_native_mcp-0.1.0-py3-none-any.whl) (pure Python, any platform) |
| Package | `theia_native_mcp` |
| Command | `theia-native-mcp` (also `python -m theia_native_mcp`) |
| Python | 3.10 or later |
| Main dependencies | the MCP Python SDK (`mcp>=2.2.0,<3`), `httpx2`, `PyYAML` |
| Ships with it | the knowledgebase bundles, the agent-facing text (server instructions, tool descriptions), and the SDK RPC certificate it trusts |

## Install

Install into its own virtual environment. The package is copied into the environment, so it does not depend on its source folder afterwards; re-run the install to pick up a new version.

From this folder, Linux and macOS:

```bash
python3 -m venv ~/.venvs/theia_native_mcp
~/.venvs/theia_native_mcp/bin/pip install theia_native_mcp-0.1.0-py3-none-any.whl
```

Windows:

```powershell
py -m venv $env:USERPROFILE\.venvs\theia_native_mcp
& $env:USERPROFILE\.venvs\theia_native_mcp\Scripts\pip.exe install theia_native_mcp-0.1.0-py3-none-any.whl
```

Or run it without an environment of your own, with [uv](https://docs.astral.sh/uv/)'s `uvx`:

```bash
uvx --from theia_native_mcp-0.1.0-py3-none-any.whl theia-native-mcp
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
