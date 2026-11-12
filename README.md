# nxwv-toolkit

Independent declarative tools built on shared, system-agnostic primitives.

## HTTP primitive

The first primitive is an async HTTP/HTTPS client. Authentication defaults to none;
Basic and Bearer authentication are supported. It returns the native HTTPX response
and raises HTTPX exceptions for HTTP and transport errors.

```python
from core import BasicAuth, BearerAuth, HttpClient

client = HttpClient("https://example.test")
response = await client.request("GET", "/status")
data = response.json()

# Optional authentication:
basic = HttpClient("http://example.test", auth=BasicAuth("user", "password"))
bearer = HttpClient("https://example.test", auth=BearerAuth("token"))
```

Supply credentials at runtime (for example, from environment variables), never in
source files. TLS verification is enabled by default.

The client currently creates an HTTPX connection context per request. Connection
pooling is not implemented yet.

## Development

Requires Python 3.12 and uv.

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

## Declarative HTTP tools

A toolkit declares an operation without binding it to a specific host:

```python
from core import HttpTool

health = HttpTool(
    name="health",
    description="Get antenna health status",
    method="GET",
    path="/",
)
```

Execute the same declaration with any configured HTTP client:

```python
from core import HttpClient
from toolkits.intellian_oneweb.health import health

client = HttpClient("https://192.0.2.10")
data = await health.run(client)
print(data)
```

The Intellian health tool requests GET /, as specified for this device.

## Run a TOML pipeline

`inventory.example.toml` lists URLs and tools. Every tool runs against every URL,
in the order listed:

```toml
[targets]
urls = ["https://example.com"]

[pipeline]
tools = ["intellian_oneweb.health"]
```

```bash
uv run python main.py inventory.example.toml
```

An optional shared `[auth]` section supports `type = "basic"` with
`username` and `password_env`, or `type = "bearer"` with `token_env`.
Secrets are read from environment variables. Tools must be explicitly registered
in `src/toolkits/__init__.py`. A failed request is reported and does not stop
the remaining operations; the process exits nonzero if any request fails.

## Project-local MCP for OpenCode and Claude Code

Both clients discover the MCP server configuration directly from this repository:
`opencode.json` for OpenCode and `.mcp.json` for Claude Code. No global MCP
registration, absolute machine-specific paths, or listening ports are required.

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/), then:

```bash
git clone https://github.com/oscarfp-dev/nxwv-toolkit.git
cd nxwv-toolkit
uv sync --locked
opencode  # or: claude
```

Start the client **from the repository root**. Both configurations run
`uv run --project . python mcp_entry.py` as a local stdio MCP server.
OpenCode loads project-local `opencode.json`; Claude Code loads project-local
`.mcp.json` and may prompt for approval of the project's MCP server.

Check discovery using `opencode mcp list` or `claude mcp list`.
Tools still require network connectivity to the requested device URLs.
Never commit secrets: pass authentication using environment variables.

The registered MCP tools are `intellian_oneweb_health` and the nine Intellian endpoint tools listed below. Each accepts `url`, plus optional
`auth_type` (`none`, `basic`, `bearer`), `username` (for Basic),
and `secret_env` (name of an environment variable containing the password
or token). Set that environment variable in the MCP server process environment
before starting the client. Avoid supplying passwords or tokens directly as
tool arguments.

Example prompt: "Use intellian_oneweb_health with url https://example.com".
The example URL is only for testing GET /, not a real Intellian device. A new registered
HttpTool becomes available to both clients on the next MCP server restart.

## Intellian endpoint tools

Each Intellian endpoint has its own Python file under
`src/toolkits/intellian_oneweb/`; one HTTP GET endpoint equals one tool.
Each declaration selects native JSON paths without renaming them. The generic
extractor lives in `src/core/json.py`, and `HttpTool.run()` returns the
extracted data directly (or the full JSON/text body for tools without fields).
The TOML and MCP adapters do not perform extraction. For example,
`nmea_data.latitude` preserves the nested `nmea_data` object in the result.
Missing keys are omitted, not replaced with invented values. `health` remains an unmodified GET / probe.

| Tool suffix | GET endpoint |
| --- | --- |
| antenna_info | /api/antenna/antennainfo |
| modem_info | /api/modem/modeminfo |
| product | /aim/api/lui/data/status/product |
| blockage_info | /api/antenna/blockageinfo |
| gnss_stats | /api/gnss/gnssstats |
| antenna_status | /aim/api/lui/data/status/antenna |
| lte_signal_info | /api/modem/lte_signal_info |
| modem_status | /api/modem/modemstatus |
| cuc_info | /api/cuc/info |

The TOML pipeline uses names like `intellian_oneweb.gnss_stats`; MCP
exposes `intellian_oneweb_gnss_stats`. Set the full URL including scheme and
port in `[targets].urls` (for example `https://192.0.2.10:8443`).
No port is hardcoded in the tools.

The original JavaScript configuration does not establish whether every
endpoint returns exactly the documented JSON shape. Validate mappings against
real Intellian responses before treating extracted values as verified.
