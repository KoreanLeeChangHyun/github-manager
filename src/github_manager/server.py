"""FastMCP server for GitHub management."""

import logging
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
    """Run the MCP server."""
    logger.info("Starting GitHub Manager MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
