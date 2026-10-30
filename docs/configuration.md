# Configuration

> **First draft.**

## Settings file

Optional JSON at the path in `THEIA_MCP_SETTINGS` (`~` is expanded). Every key is optional; these are the defaults:

```json
{
  "endpoints": [],
  "local_sdk_endpoint": {
    "address": "127.0.0.1",
    "port": 17420,
    "port_step": 2000,
    "port_attempts": 5,
    "token_env": "THEIA_RPC_TOKEN"
  },
  "default_token": "theia_mcp_default_token",
  "knowledgebase": { "default_max_length": 5000 }
}
```

| Key | Meaning |
|---|---|
| `endpoints` | Named endpoints: `{"name", "url", "token_env", "certificate"}`. `connect` accepts the name or the URL. The URL must be `https://`. |
| `local_sdk_endpoint` | Where `connect` with no endpoint looks for the local SDK, which env var holds its token, and optionally its `certificate` |
| `certificate` | In an endpoint entry or `local_sdk_endpoint`: the path of that SDK's RPC certificate, or a copy of it (`~` is expanded) |
| `default_token` | The token used when no other is found. The default value is public: development only. |
| `knowledgebase.default_max_length` | Characters per `read_knowledgebase` call when none is given |

Tokens are read from the environment when the settings are loaded.

## Token order

1. The `token` passed to `connect`.
2. The environment variable named by the endpoint's `token_env`.
3. `default_token`.

A URL that matches no configured endpoint uses `connect`'s `token`, else `default_token`.

## Certificate order

1. The `certificate` passed to `connect`.
2. The endpoint's `certificate` setting.
3. `sdk_rpc_server_cert.pem` in `THEIA_RPC_TLS_DIR`, else in `~/.theia/rpc_tls`: the folder where an SDK on this machine, run by the same OS user, generates its certificate on first start.

The server connects only to an endpoint that proves it holds that certificate's private key. With no certificate found, or a server presenting another one, it refuses before sending anything, the token included. For an SDK on another machine, give the server a copy of that SDK's `sdk_rpc_server_cert.pem`.

## Environment variables

| Variable | Meaning |
|---|---|
| `THEIA_MCP_SETTINGS` | Path to the settings file |
| `THEIA_RPC_TOKEN` | The local SDK's token (the default `token_env`) |
| `THEIA_MCP_HTTP_SECRET` | Required with `--http`: the bearer secret MCP clients send |
| `THEIA_RPC_TLS_DIR` | Folder of the local SDK's RPC certificate when it is not `~/.theia/rpc_tls` (the SDK reads the same variable) |

## HTTP transport

`--http` serves Streamable HTTP at `/mcp`:

- Bind address and port: `--host` (default `127.0.0.1`) and `--port` (default `8765`). These are flags, not settings.
- Authentication: clients send `Authorization: Bearer <THEIA_MCP_HTTP_SECRET>`.
- DNS-rebinding protection: accepted `Host` values are `127.0.0.1:*`, `localhost:*`, `[::1]:*` and the bound host. Accepted `Origin` values are the `--allowed-origin` flags; a request with no `Origin` (a non-browser client) is not rejected for it.

## The SDK side

What an endpoint offers is set where the SDK runs, in its RPC config: the address and ports it listens on, whether it accepts connections from other machines (`allow_external_connections`), how many clients it allows, and the tokens it accepts with each token's `methods`, `events` or `full_access`. The SDK's own documentation covers that file.
