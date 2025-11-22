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


@mcp.resource("docs://tools")
def get_tools_documentation() -> str:
    """Get list of all available tools with descriptions."""
    tools = mcp._tool_manager._tools

    categories = {
        'Repository Management (8 tools)': [
            'list_repositories', 'get_repository_info', 'create_repository',
            'update_repository', 'delete_repository', 'search_repositories',
            'get_repository_topics', 'set_repository_topics'
        ],
        'Issues (3 tools)': [
            'list_issues', 'create_issue', 'close_issue'
        ],
        'Pull Requests (3 tools)': [
            'list_pull_requests', 'create_pull_request', 'merge_pull_request'
        ],
        'Releases (2 tools)': [
            'list_releases', 'create_release'
        ],
        'Labels (2 tools)': [
            'list_labels', 'create_label'
        ],
        'Workflows (1 tool)': [
            'list_workflow_runs'
        ],
        'Workspace (8 tools)': [
            'list_workspace_repos', 'clone_repository', 'pull_repository',
            'get_repository_status', 'sync_all_repositories', 'delete_workspace_repo',
            'create_branch', 'switch_branch'
        ],
        'Backup (4 tools)': [
            'backup_repository', 'backup_all_repositories',
            'list_backups', 'restore_repository'
        ],
    }

    result = ["GitHub Manager MCP Server - Tools Documentation", "=" * 70, ""]

    for category, tool_names in categories.items():
        result.append(f"\n{category}")
        result.append("-" * 70)
        for tool_name in tool_names:
            if tool_name in tools:
                func = tools[tool_name]
                doc = func.__doc__ or "No description available"
                first_line = doc.strip().split('\n')[0]
                result.append(f"  • {tool_name}")
                result.append(f"    {first_line}")

    result.append(f"\nTotal: 31 tools across 8 categories")
    result.append("\nResources:")
    result.append("  • config://github - View current configuration")
    result.append("  • status://rate-limit - Check GitHub API rate limits")
    result.append("  • docs://tools - This documentation")

    return "\n".join(result)


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
