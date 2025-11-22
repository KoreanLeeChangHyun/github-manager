"""FastMCP server for GitHub management."""

import logging
import os
import sys
from typing import Any

from fastmcp import FastMCP
from github import Github, GithubException

from .config import Config
from .repository.tools import setup_repository_tools
from .automation.tools import setup_automation_tools
from .workspace.tools import setup_workspace_tools
from .backup.tools import setup_backup_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("GitHub Manager")

# Global configuration and GitHub client
config: Config | None = None
github_client: Github | None = None


def get_github_client() -> Github:
    """Get or create GitHub client."""
    global config, github_client

    if github_client is None:
        if config is None:
            config = Config.load()
        github_client = Github(config.github.token)

    return github_client


# Setup all tool categories
setup_repository_tools(mcp, get_github_client)
setup_automation_tools(mcp, get_github_client)
setup_workspace_tools(mcp, get_github_client)
setup_backup_tools(mcp, get_github_client)


@mcp.resource("config://github")
def get_github_config() -> str:
    """Get current GitHub configuration (token redacted)."""
    if config is None:
        cfg = Config.load()
    else:
        cfg = config

    return f"""GitHub Configuration:
- Username: {cfg.github.username}
- Organization: {cfg.github.org or 'N/A'}
- Rate Limit Threshold: {cfg.github.rate_limit_threshold}
- Workspace Directory: {cfg.workspace.workspace_dir}
- Backup Directory: {cfg.workspace.backup_dir}
"""


@mcp.resource("status://rate-limit")
def get_rate_limit() -> str:
    """Get current GitHub API rate limit status."""
    client = get_github_client()
    rate_limit = client.get_rate_limit()

    core = rate_limit.core
    search = rate_limit.search

    return f"""GitHub API Rate Limit Status:
Core API:
- Limit: {core.limit}
- Remaining: {core.remaining}
- Reset: {core.reset}

Search API:
- Limit: {search.limit}
- Remaining: {search.remaining}
- Reset: {search.reset}
"""


def main() -> None:
    """Run the MCP server.

    Transport mode can be controlled via:
    - Environment variable: MCP_TRANSPORT=sse or MCP_TRANSPORT=stdio (default)
    - Command line: --transport sse or --transport stdio

    For SSE mode, port can be set via:
    - Environment variable: MCP_PORT=8001 (default)
    - Command line: --port 8001
    """
    # Parse command line arguments
    transport = "stdio"  # default
    port = 8001  # default
    host = "0.0.0.0"  # default

    # Check environment variables
    if os.getenv("MCP_TRANSPORT"):
        transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if os.getenv("MCP_PORT"):
        port = int(os.getenv("MCP_PORT", "8001"))

    if os.getenv("MCP_HOST"):
        host = os.getenv("MCP_HOST", "0.0.0.0")

    # Check command line arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--transport" and i + 1 < len(sys.argv):
            transport = sys.argv[i + 1].lower()
        elif arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
        elif arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]

    logger.info(f"Starting GitHub Manager MCP Server (transport={transport})...")

    if transport == "sse":
        logger.info(f"SSE server will be available at http://{host}:{port}")
        logger.info("Connect using MCP client or HTTP requests")
        mcp.run(transport="sse", port=port, host=host)
    else:
        logger.info("STDIO server ready for MCP client connection")
        mcp.run()


if __name__ == "__main__":
    main()
