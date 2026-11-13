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

On Ubuntu/WSL with a corporate CA already trusted by the operating system,
HTTPX may still reject HTTPS because its default `certifi` bundle does not
include that CA. Set `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt` in
the project `.env` to use the Ubuntu CA bundle while keeping TLS verification
enabled. `mcp_entry.py` loads the project `.env` when OpenCode or Claude
starts the MCP server; restart the MCP client after changing the setting.
Do not disable certificate verification with `verify=False`.


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
from toolkits.intellian_oneweb.tools.health import health

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
in `src/toolkits/intellian_oneweb/tools/__init__.py`. A failed request is reported and does not stop
the remaining operations; the process exits nonzero if any request fails.

## Default operational assistant (OpenCode and Claude Code)

This repository is intended to be **used** as a satellite diagnostics assistant,
not edited by the assistant during routine operations.

- `AGENTS.md` defines the shared operational role, tool-selection rules,
  evidence standards, read-only limits, and diagnostic response format.
- Claude Code and OpenCode use the project `AGENTS.md` directly (use a client version that supports it).
- OpenCode reads `AGENTS.md` as project instructions. Its project
  `opencode.json` denies file editing and shell execution by the agent;
  the configured local MCP process can still launch.
- Both clients connect to the same project-local `nxwv-toolkit` MCP server.
  There is no separate agent to select: open either client in the repository root.

To use the assistant, configure `.env` from `.env.example` for the OneWeb
service (if needed), then launch `opencode` or `claude`. You can ask questions
such as "Check the firmware upgrade status for IMEI 350357139990004" or
"Investigate blockage on the Intellian antenna at https://device.example".
The latter URL is illustrative; direct Intellian queries require an accessible
device URL and any necessary credentials available to the MCP process.

Restart the client and its MCP subprocess after editing the source or `.env`;
a running stdio server does not hot-reload changes. The agent cannot infer
live status from historical reports or failed queries.

**Security:** these are client-level instructions and OpenCode permissions,
not a sandbox for arbitrary MCP tools. Claude Code's project instructions
guide operational behavior but do not by themselves enforce a hard tool
permission boundary. Keep the server read-only and restrict credentials
to the access required for diagnostics.

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

Example prompt: "Check antenna health at https://example.com".
The example URL is only for testing GET /, not a real Intellian device. A new registered
HttpTool becomes available to both clients on the next MCP server restart.

## Intellian endpoint tools

Each Intellian endpoint has its own Python file under
`src/toolkits/intellian_oneweb/tools/`; one HTTP GET endpoint equals one tool.
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


## OneWeb API (centralized service)

The `oneweb_api_*` MCP tools connect to the OneWeb service, not to individual
antennas. Copy `.env.example` to `.env` and configure the three service base
URLs plus Basic credentials. `mcp_entry.py` loads the local `.env` automatically;
environment variables already set by the process take precedence.

The toolkit exposes six GET operations (inventory list/detail; upgrade, reboot
and mute status; available installer bundles) and **one read-only POST**
(`oneweb_api_performance_report`). The performance report RAML specifies
`POST /performanceReport` for report retrieval and returns the report in a 201
response. No terminal-management POST, PUT, PATCH or DELETE is exposed.

OneWeb MCP tools take domain arguments such as `imei`, `fields`, `limit`
and `offset`; they do **not** accept URL or credentials as tool arguments.
The performance report accepts a structured `payload` matching one of the
RAML report configurations (including `reportingTimeframe` and
`performanceJob`). Each metric has its own required schema; the toolkit
passes that payload through without inventing values.

The three source RAML ZIP archives are kept locally in `.local/raml/` and
ignored by Git. No vendor specifications or sample data are committed.
The example service URLs in `.env.example` are placeholders, not verified
production endpoints.

## OpsCenter API (Poller)

Two read-only MCP tools (one module per endpoint under
`src/toolkits/opscenter_api/tools/`) fetch the original JSON payload, without field
selection or schema conversion:

- `opscenter_api_get_antenna_data(antenna_id)` — `GET /api/v1/antennas/data/{antenna_id}`
- `opscenter_api_get_antenna_info(antenna_id)` — `GET /api/v1/antennas/info/{antenna_id}`

Set the Poller host in `OPSCENTER_BASE_URL` in your local `.env` file.
The server does not ship with a default host. Antenna IDs are not OneWeb IMEIs.
Authentication is a manually managed
application session cookie, **not** an Okta token. The MCP never asks
the AI client for the cookie and never returns it in tool results.

To save the **entire Cookie request header value** copied from an authenticated
browser request, enter it interactively in WSL:

```bash
install -d -m 700 .local/auth
umask 077
read -rsp "OpsCenter Cookie header: " COOKIE; echo
printf '%s' "$COOKIE" > .local/auth/opscenter.cookie
unset COOKIE
chmod 600 .local/auth/opscenter.cookie
```

The MCP reads this file on each request, so updating the cookie does not
require restarting the server. By default the file lives at
`.local/auth/opscenter.cookie` relative to the repository root (gitignored).
Set `OPSCENTER_COOKIE_FILE` to use another private file. The tool reports authentication errors when the cookie expires;
it does not automatically sign in or renew the session. Keep the file out
of source control, logs, prompts, and shared directories.

TLS verification remains enabled. WSL must trust the corporate root CA;
do not use `curl -k` or `verify=False` as a permanent workaround.
