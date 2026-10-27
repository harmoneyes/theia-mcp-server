# How the MCP server works

> **First draft.**

The server sits between an AI agent and one or more Theia SDK RPC endpoints. It speaks MCP to the agent and the SDK's JSON-RPC protocol to each endpoint. It holds no knowledge of individual SDK methods: method and event lists, params and schemas come only from each endpoint's discovery document.

## Connecting

`connect(endpoint?, token?)`:

1. **Picks the endpoint.**
   - A name or URL from the settings' `endpoints`, or any `https://` URL, is used as given.
   - With no endpoint, it tries the local SDK: `https://127.0.0.1:<port>/v1` for ports 17420, 19420, 21420, 23420 and 25420 (`port`, then `port + port_step`, up to `port_attempts` candidates). Each candidate must first answer `GET /health` with `{"status":"pass"}` within 3 s, or it is skipped and no token is sent to it.
   - Only `https://` is accepted.
2. **Verifies the server.** TLS is checked against the one certificate the server trusts, the SDK's compiled-in certificate. The host name is not checked, so the certificate identifies an SDK wherever it runs.
3. **Picks the token:** `connect`'s `token`, else the environment variable the endpoint's `token_env` names (`THEIA_RPC_TOKEN` for the local SDK), else `default_token`. It is sent as `Authorization: Bearer <token>`.
4. **Opens an RPC session** with `open_rpc_session`. The reply's `Theia-Rpc-Session-Id` header is sent on every later request.
5. **Reads the surface** with `rpc.discover`, and assigns the connection an id (`conn-1`, `conn-2`, ...).

The result lists the endpoint's methods and events and its SDK version. `disconnect` sends `end_rpc_session`, ends the connection's subscriptions and discards its buffered events.

Connection states: `open`, `rpc_session ended` (the endpoint answered 404), `connection lost` (a transport failure). A later successful reply sets `open` again. The server never opens a new session on its own.

## Discovering methods and events

- `list_methods` lists every entry of the discovery document's `methods` and every key of its `x-events`, each with its `summary` (or the first line of its `description`).
- `describe_method` returns one entry as the document gives it, with its local `$ref`s resolved: description, params, result schema, examples, or an event's payload schema. An unknown name returns similar names.
- The discovery document lists only what the connection's token may use.

Because nothing is hard-coded, a new SDK method or event, or one an app adds, appears on the next `connect` with no change to the MCP server.

## Calling methods

`call_method(rpc_connection_id, method, params)` sends any method with params by name, and returns one of:

| Result | When |
|---|---|
| `result` | a JSON-RPC result |
| `error` (`code`, `message`, `data`) | a JSON-RPC error |
| `subscription_id` | the reply is an event stream (see below) |
| `files_downloaded` (`file_name`, `path`, `size_bytes`) | the reply is files (`multipart/mixed`); each is saved under the system temp folder, in `theia_native_mcp/downloads/<rpc_connection_id>/` |
| `http_status_reply` | an HTTP status other than 200, e.g. 401 (token rejected, with setup guidance) or 404 (RPC session ended) |
| `connection_failed` | the endpoint could not be reached |

A file name that is absolute or contains `..`, `\` or `:` is refused and nothing is written.

## Events

- **Subscribing** is an ordinary method call: `subscribe` with an `event_name`, and optionally a `filter` (evaluated by the SDK) and a `webhook`. Its reply is an SSE stream, and `call_method` returns the stream's `subscription_id`.
- **Buffering:** every event on the connection's streams goes into a per-connection buffer of up to 10,000 events, oldest dropped first. Each buffered event carries `sequence_number`, `rpc_connection_id`, `subscription_id`, `kind`, `event_name`, `payload` and `received_at`.
- **Reading:** `get_events` reads from a position; `wait_for_event` waits up to a timeout (seconds) for the next event on given subscriptions or event names. Both take an optional buffer filter: field selectors such as `event_name=fatigue_transition_ace`. This filter only selects among events the server already holds; it is not the SDK's subscription filter.
- **Dropped streams** (closed, failed, or 45 s without any bytes) are resumed with `resume_subscription`, up to 3 attempts after 1, 2 and 4 s. Events the endpoint no longer holds are reported as a `missed_events` event; if every attempt fails, a `reconnect_failed` event is buffered. Both always match a `wait_for_event` on that subscription.
- **Ending:** `unsubscribe`, also an ordinary method call.

## The knowledgebase

`get_knowledgebase_index` and `read_knowledgebase` serve the bundled knowledgebase, matched to the connected SDK's version. See [../knowledgebase/README.md](../knowledgebase/README.md).

## What the agent is told

The server's MCP instructions tell the agent, among other things:

- the endpoint may be an SDK or an app that embeds it and adds or overrides methods, so it must run `describe_method` before using any method or event;
- user state (outputs and transitions) and session reports are not reachable with a default token, and a missing method or event usually means the token lacks access, not that the SDK lacks it;
- to change an RPC config only after the user agrees.

## Access control

Access is enforced by the endpoint, not by the MCP server:

- A default SDK token reaches the connection methods and the status methods (whether a session or tracker is running, model info and versions, batch info). No events.
- The SDK host grants more per token in its RPC config: listed `methods` and `events`, or `full_access`.
- A method the token may not use answers -32601 (method not found); an event it may not use answers -32602.
- An RPC session works only with the token that opened it.
