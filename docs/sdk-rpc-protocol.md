# The SDK RPC protocol

> **First draft.**

This is the protocol the Theia SDK's RPC server speaks, and the one the MCP server expects from any endpoint. An app that wraps the SDK implements the same protocol on its own endpoint ([Extending the SDK's RPC](extending-the-sdk-rpc.md)).

## HTTP

| Item | Contract |
|---|---|
| Endpoint | `POST https://<address>:<port>/v1` |
| Health check | `GET https://<address>:<port>/health`, no token: 200, `application/health+json`, `{"status":"pass"}` |
| TLS | TLS 1.2 or later. Plain HTTP is not served. |
| Other methods on `/v1` | 405, `Allow: POST` |
| Request headers | `Authorization: Bearer <token>` on every request; `Content-Type: application/json`; `Theia-Rpc-Session-Id: <uuid>` on every request after `open_rpc_session` |
| Single response | 200, `application/json` |
| Notification (no `id`) | 202, no body |
| Stream | 200, `text/event-stream`; each message `data: <compact JSON>`; a `: keep-alive` comment after 15 s without a write |
| Files | 200, `multipart/mixed`; one part per file, `Content-Type: application/octet-stream`, named by `Content-Disposition: attachment; filename="<file_name>"` |
| 401 | missing or rejected token, with `WWW-Authenticate: Bearer` |
| 404 | unknown, ended or displaced RPC session, or a session used with a token other than the one that opened it |
| 503 | the server is stopping |
| Otherwise | a JSON-RPC result or error inside a 200 |

Requests are JSON-RPC 2.0 objects with params by name. Batches are not accepted.

## Control methods

| Method | Params | Result |
|---|---|---|
| `open_rpc_session` | `client_name`, `client_version` | `{}`, and the `Theia-Rpc-Session-Id` header |
| `end_rpc_session` | none | `{}` |
| `rpc.discover` | none | the OpenRPC document, with only what the token may use |
| `subscribe` | `event_name`; optional `filter`, `webhook` (`{"url", "headers"}`) | a stream |
| `unsubscribe` | `subscription_id` | `true` if it existed and is now ended |
| `resume_subscription` | `subscription_id`, `last_sdk_event_id` | a stream |

Every other method needs an open RPC session first.

## Error codes

| Code | Meaning |
|---|---|
| -32700 | parse error |
| -32600 | invalid request |
| -32601 | method not found, including a method the token may not call |
| -32602 | invalid params, including an unknown event or one the token may not subscribe to, or an invalid filter or webhook |
| -32603 | internal error: the method threw; `message` is its text |
| -32001 | an RPC session is required |
| -32002 | subscription id already active |
| -32003 | subscription not found |
| -32004 | too many open subscription streams |

## Stream messages

```
acknowledgement (always first):
  {"jsonrpc":"2.0","method":"subscription_acknowledged",
   "params":{"subscription_id":<id>,"event_name":"<name>"}}
missed events (resume only, right after the acknowledgement):
  {"jsonrpc":"2.0","method":"subscription_missed_events",
   "params":{"subscription_id":<id>,"oldest_retained_sdk_event_id":<int or null>}}
event:
  {"jsonrpc":"2.0","method":"subscription_event",
   "params":{"subscription_id":<id>,"sdk_event_id":<int>,"event_name":"<name>","payload":{...}}}
final response (unsubscribe, end_rpc_session, displacement, shutdown):
  {"jsonrpc":"2.0","id":<id of the request that opened this stream>,
   "result":{"result_type":"complete","subscription_id":<id>}}
```

- `subscription_id` is the `id` of the `subscribe` request, as sent.
- `sdk_event_id` starts at 1 per subscription and counts up by 1.
- A dropped subscription stays resumable for 10 minutes.

## The discovery document

`rpc.discover` returns an [OpenRPC](https://spec.open-rpc.org/) 1.4 document:

- `methods`: one entry per method, each with `name`, `summary`, `description`, `params` (by name, with schemas and descriptions), `result` (schema and description) and `examples`.
- `x-events`: an object keyed by event name; each entry has a `summary`, `description`, payload schema and examples.
- `components/schemas`: shared types, referenced with `$ref`.
- `x-theia-sdk-version`: the SDK version, which the MCP server uses to pick the knowledgebase.

Descriptions are the only explanation an agent gets of what a method does and what its output means, so every method, param, result and event property is described, with examples.
