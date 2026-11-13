"""Register toolkit-specific MCP adapters, without domain logic here."""

from mcp.server.fastmcp import FastMCP

from toolkits.intellian_oneweb.mcp import register as register_intellian
from toolkits.oneweb_api.mcp import register as register_oneweb
from toolkits.opscenter_api.mcp import register as register_opscenter

mcp = FastMCP("nxwv-toolkit")
register_intellian(mcp)
register_oneweb(mcp)
register_opscenter(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
