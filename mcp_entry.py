"""Launch the local MCP server from the project root."""

import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from mcp_server.server import main  # noqa: E402

if __name__ == "__main__":
    main()
