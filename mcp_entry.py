"""Launch the local MCP server from the project root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mcp_server.server import main

if __name__ == "__main__":
    main()
