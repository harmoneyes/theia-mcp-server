# Knowledgebase bundles

> **First draft.** No separate bundles are published here yet; the server wheel ships `theia_knowledgebase_0.1.0.zip` inside it. This page sets out the bundle format and how releases will be laid out.

The knowledgebase is the Theia product and SDK information an agent reads through `get_knowledgebase_index` and `read_knowledgebase`. It is orientation for the agent. The authoritative description of any method or event is the endpoint's own discovery document (`rpc.discover`), which `describe_method` returns.

## Bundle format

- One zip per Theia SDK version: `theia_knowledgebase_<version>.zip`.
- Each zip holds an MkDocs source tree:
  - `manifest.json`: `{"product_version": "<version>", "revision_timestamp": "<ISO-8601 UTC>"}`
  - `mkdocs.yml`: the site title and the `nav` (page order and sections)
  - `docs/`: Markdown pages, each with YAML front matter giving `title` and `description`
- MkDocs itself is not run. The MCP server reads the tree directly.

## How the server picks a bundle

- When exactly one connection is open, the server uses the bundle whose `product_version` matches that SDK's version (the `x-theia-sdk-version` of its discovery document).
- Otherwise, or when no bundle matches, it uses the most recent bundle and says so in a version note on each read.

## Anchors

Pages are addressed by anchors:

| Anchor | Addresses |
|---|---|
| `setup/index.md` | a page |
| `setup/index.md#some-heading` | a heading (ids as Python-Markdown's table of contents makes them) |
| `setup/index.md#char=100,400` | a block of characters (RFC 5147) |

`get_knowledgebase_index("")` gives the top-level index; reads are paged with `start_index` and `max_length` (default 5000 characters).

## Current sections

| Section | Pages |
|---|---|
| Home | `index.md` |
| About Theia | `about/index.md`, `about/harmoneyes-and-theia.md`, `about/not-measured-by-theia.md` |
| Measured outputs | `outputs/index.md`, `outputs/cognitive-load.md`, `outputs/fatigue.md`, `outputs/attention.md`, `outputs/mental-readiness.md`, `outputs/transitions.md` |
| Setup | `setup/index.md`, `setup/installing-the-sdk.md`, `setup/activating-the-sdk.md`, `setup/first-session.md`, `setup/connecting-an-ai-agent.md`, `setup/session-reports.md`, `setup/sdk-alerts.md` |
| Advanced integration | `advanced-integration/index.md`, `advanced-integration/use-cases.md`, `advanced-integration/features.md`, `advanced-integration/integration-example.md` |
| API reference | `api-reference/index.md`, one page per group of public RPC methods (session lifecycle, data input, prediction results, ...), `api-reference/events.md`, `api-reference/types.md`, `api-reference/rpc-differences.md` |

`setup/connecting-an-ai-agent.md` must stay at that path: the server's instructions and its 401 guidance name it.

## Releasing a bundle

1. Edit the pages and the `nav` in `mkdocs.yml`.
2. Set `product_version` to the Theia SDK version the bundle describes, and a new `revision_timestamp`.
3. Zip the tree as `theia_knowledgebase_<version>.zip`.

The server currently loads only the bundles shipped inside its package. Serving bundles from this repository, so the knowledgebase can update without a new server release, is not built yet.
