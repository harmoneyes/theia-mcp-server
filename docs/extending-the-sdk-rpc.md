# Extending the SDK's RPC

> **First draft.** This describes the pattern and what the MCP server requires of it. No reference implementation exists yet.

An app that embeds the Theia SDK can put its own RPC endpoint in front of the SDK's. That endpoint speaks the same protocol, forwards SDK calls to the SDK, and adds its own methods and events to the discovery document. The Theia MCP server, pointed at the app's endpoint, lists, describes and calls the app's methods exactly as it does the SDK's. No change to the MCP server is needed, because everything it shows the agent comes from `rpc.discover`.

## What an app can do

- **Add methods:** app controls such as "start a level", "pause the task", "show a break screen".
- **Add events:** app events such as "level finished", streamed the same way SDK events are.
- **Override a method:** handle an SDK method name itself (validate, log, add side effects, then call the SDK or not), and describe the new behaviour in discovery.
- **Hide a method or event:** leave it out of discovery and refuse it.

## Architecture

```
 Theia MCP server
        │  HTTPS: the SDK RPC protocol
        ▼
 App's RPC endpoint
   ├─ open_rpc_session / end_rpc_session, tokens  ← the app's own
   ├─ rpc.discover   ← the SDK's document + the app's entries
   ├─ app methods and events  ← handled by the app
   └─ everything else  ← forwarded to the SDK
        │
        ▼
 Theia SDK
   in-process, through a control session (C++)
   or its own RPC server on loopback (any language)
```

### Reaching the SDK

The SDK has no API to add methods to its own RPC server, so the app's endpoint forwards to it:

| Route | Use when | Notes |
|---|---|---|
| **In-process control session** (`TheiaSDK::open_control_session`) | the app is C++ | The same methods, events, subscriptions and filters as the HTTP server, with no network or token. It has full access and no RPC session of its own, so the app enforces access itself. |
| **The SDK's RPC server** | any language (C, Python, Node, ...) | The app is an ordinary RPC client: it opens its own RPC session with the SDK, using a token the SDK's RPC config grants what the app needs. Keep the SDK's server on loopback. |

Either way, the SDK expects its methods to be called one at a time: the app must not call SDK methods from its own threads at the same time as RPC clients.

## The discovery document

The app's `rpc.discover` returns the SDK's document with the app's changes:

```
on rpc.discover from client:
    document = sdk.call("rpc.discover")              # the SDK's methods and events
    add app method entries to document.methods
    add app event entries to document["x-events"]
    replace the entries of overridden methods
    remove hidden methods and events
    keep only what this client's token may use
    keep document["x-theia-sdk-version"]             # the MCP server picks the knowledgebase from it
    return document
```

Describe every app entry as fully as the SDK does: the description is all the agent knows about the method. A method entry:

```json
{
  "name": "app_pause_task",
  "summary": "Pause the current task and show the pause screen.",
  "paramStructure": "by-name",
  "params": [
    {
      "name": "reason",
      "required": false,
      "schema": { "type": "string" },
      "description": "Shown to the user on the pause screen."
    }
  ],
  "result": {
    "name": "result",
    "schema": { "type": "boolean" },
    "description": "true if a task was running and is now paused."
  },
  "description": "Pauses the running task. The SDK session keeps running; call app_resume_task to continue.",
  "examples": [
    {
      "name": "Pause",
      "params": [{ "name": "reason", "value": "Break" }],
      "result": { "name": "result", "value": true }
    }
  ]
}
```

An event entry under `x-events` has a `summary`, a `description`, a payload schema with every property described, and examples.

Give app methods and events a prefix of their own (for example `app_`) so they never collide with an SDK name, now or in a later SDK version.

## Routing calls

```
on request from client:
    check the bearer token                           # 401 if rejected
    if method is open_rpc_session / end_rpc_session:
        handle it with the app's own session ids
    else if no RPC session:
        answer -32001
    else if method is rpc.discover:
        answer the merged document (above)
    else if the token may not use method:
        answer -32601 (or -32602 for an event)
    else if method is an app method or an override:
        handle it in the app
    else if method is subscribe / resume_subscription:
        route by event name or subscription (below)
    else:
        forward to the SDK; pass its result, error, stream or files back unchanged
```

## Events

- **SDK events:** forward `subscribe` to the SDK and relay its stream to the client message for message.
- **App events:** answer `subscribe` with a stream the app writes itself, in the SDK's message format: `subscription_acknowledged` first, then `subscription_event` messages with `sdk_event_id` counting up from 1, and a final response when the subscription ends.
- **Resuming:** the MCP server resumes a dropped stream with `resume_subscription` and the last event id it saw. Keep recent app events so the app can replay them, and send `subscription_missed_events` for any it no longer holds. Without it, a dropped app stream ends in a `reconnect_failed` event.
- **Keep-alive:** send `: keep-alive` on a quiet stream. The MCP server treats 45 s without any bytes as a dropped stream.

## Sessions and tokens

- The app's endpoint issues its own `Theia-Rpc-Session-Id`s and checks its own tokens. When it forwards over the SDK's RPC server, it holds its own session and token with the SDK, separate from its clients'.
- Decide per token which app methods and events, and which SDK ones, a client may use, and list only those in discovery. User state (outputs, transitions, session reports) describes a person's eye movement and physiological state; grant it deliberately.
- A 404 from the app's endpoint tells the MCP server the RPC session ended.

## Pointing the MCP server at the app

- Pass the app endpoint's URL to `connect`, or add it to the settings' `endpoints` with a name and `token_env`.
- A configured endpoint or URL is used as given, with no health check and no `/v1` added.
- `connect` with no endpoint searches only the SDK's default local ports, and needs `GET /health` to answer `{"status":"pass"}`.

## Current limitation: the certificate

The MCP server verifies every endpoint against one certificate, the SDK's compiled-in RPC certificate, and has no setting for another. So an app's endpoint must currently serve that same certificate and its private key. Both ship with the SDK and are for development and testing only.

## Checklist

- [ ] `POST /v1` over HTTPS, JSON-RPC 2.0, params by name
- [ ] Bearer token on every request; 401 with `WWW-Authenticate: Bearer` when rejected
- [ ] `open_rpc_session` returns `Theia-Rpc-Session-Id`; `end_rpc_session`; 404 for an ended session
- [ ] `rpc.discover` returns the merged document, filtered per token, with `x-theia-sdk-version`
- [ ] Every app method and event fully described, with examples
- [ ] App names prefixed so they never collide with SDK names
- [ ] SDK calls forwarded with results, errors, streams and files passed through unchanged
- [ ] App event streams in the SDK's message format, with `resume_subscription` and keep-alives
- [ ] `GET /health` if the endpoint should be found by the local port search
- [ ] Serves the certificate the MCP server trusts
