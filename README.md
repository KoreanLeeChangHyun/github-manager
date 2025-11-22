# GitHub Manager MCP Server

Comprehensive GitHub management MCP server built with FastMCP. Manage repositories, automate workflows, organize workspaces, and backup your GitHub data - all through the Model Context Protocol.

## Features

### Repository Management
- List, search, and get detailed repository information
- Create, update, and delete repositories
- Manage repository topics and settings
- Get repository statistics

### Automation
- **Issues**: List, create, and close issues
- **Pull Requests**: List, create, and merge PRs
- **Releases**: List and create releases
- **Labels**: List and create labels
- **Workflows**: Monitor GitHub Actions workflow runs

### Workspace Management
- Clone repositories to local workspace
- Pull latest changes across all repos
- Check git status and manage branches
- Sync all workspace repositories
- Create and switch branches

### Backup & Restore
- Backup individual repositories with metadata
- Batch backup all user repositories
- Backup includes: code, issues, PRs, releases
- List and restore from backups

## Installation

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- GitHub personal access token

### Quick Install

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/KoreanLeeChangHyun/github-manager.git
cd github-manager

# Run installation script
chmod +x install.sh
./install.sh

# Edit .env file with your GitHub token
nano .env
```

### Manual Installation

```bash
# Create virtual environment and install
uv pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env and add your GitHub token
```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_username
GITHUB_ORG=optional_org_name
WORKSPACE_DIR=/home/user/workspace
BACKUP_DIR=/home/user/backups/github
RATE_LIMIT_THRESHOLD=100
```

### MCP Client Configuration

For Claude Code or other MCP clients, add to your MCP settings:

```json
{
  "mcpServers": {
    "github-manager": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/github-manager",
        "run",
        "github-manager-mcp"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_USERNAME": "your_username"
      }
    }
  }
}
```

See `config/mcp-config.example.json` for a complete example.

## Usage

### Running the Server

#### STDIO Mode (for Claude Code)

```bash
# Default mode - STDIO transport
uv run github-manager-mcp
```

#### SSE Mode (for network access / other LLMs)

```bash
# Start SSE server on port 8001
./start_sse.sh

# Or with custom port
./start_sse.sh --port 3000

# Or using environment variables
MCP_TRANSPORT=sse MCP_PORT=8001 uv run github-manager-mcp

# Or using command line arguments
uv run github-manager-mcp --transport sse --port 8001
```

Server will be available at: `http://localhost:8001/sse`

**For other LLMs (ChatGPT, Gemini, etc.)**: See [docs/connecting-llms.md](docs/connecting-llms.md) for connection guide.

### Available Tools

#### Repository Management

- `list_repositories` - List repositories for a user
- `get_repository_info` - Get detailed repository information
- `create_repository` - Create a new repository
- `update_repository` - Update repository settings
- `delete_repository` - Delete a repository (with confirmation)
- `search_repositories` - Search GitHub repositories
- `get_repository_topics` - Get repository topics
- `set_repository_topics` - Set repository topics

#### Issues

- `list_issues` - List issues in a repository
- `create_issue` - Create a new issue
- `close_issue` - Close an issue with optional comment

#### Pull Requests

- `list_pull_requests` - List pull requests
- `create_pull_request` - Create a new pull request
- `merge_pull_request` - Merge a pull request

#### Releases

- `list_releases` - List repository releases
- `create_release` - Create a new release

#### Labels

- `list_labels` - List repository labels
- `create_label` - Create a new label

#### Workflows

- `list_workflow_runs` - List GitHub Actions workflow runs

#### Workspace

- `list_workspace_repos` - List repositories in workspace
- `clone_repository` - Clone a repository to workspace
- `pull_repository` - Pull latest changes
- `get_repository_status` - Get git status
- `sync_all_repositories` - Pull all workspace repos
- `delete_workspace_repo` - Delete from workspace
- `create_branch` - Create a new branch
- `switch_branch` - Switch to a branch

#### Backup

- `backup_repository` - Backup a repository with metadata
- `backup_all_repositories` - Batch backup all repositories
- `list_backups` - List available backups
- `restore_repository` - Restore from backup

### Resources

- `config://github` - View current configuration
- `status://rate-limit` - Check GitHub API rate limits

## Examples

### Using with Claude Code

```
You: List my GitHub repositories

Claude: [uses list_repositories tool]

You: Clone my-project to workspace

Claude: [uses clone_repository tool]

You: Create an issue titled "Bug fix needed"

Claude: [uses create_issue tool]

You: Backup all my repositories

Claude: [uses backup_all_repositories tool]
```

## Development

### Project Structure

```
github-manager/
├── src/
│   └── github_manager/
│       ├── __init__.py
│       ├── server.py          # FastMCP server
│       ├── config.py          # Configuration management
│       ├── repository/        # Repository management
│       ├── automation/        # Issues, PRs, releases
│       ├── workspace/         # Local workspace management
│       └── backup/            # Backup & restore
├── tests/
├── config/
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

## GitHub Token Scopes

Your GitHub personal access token needs these scopes:

- `repo` - Full control of repositories
- `workflow` - Update GitHub Actions workflows
- `read:org` - Read organization data (if using organizations)

Create a token at: https://github.com/settings/tokens

## Security

- Never commit your `.env` file or expose your GitHub token
- Use environment variables for sensitive data
- Tokens are never logged or exposed in tool outputs
- Use SSH keys for git operations when possible

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- Issues: https://github.com/KoreanLeeChangHyun/github-manager/issues
- Discussions: https://github.com/KoreanLeeChangHyun/github-manager/discussions

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API
- Powered by [Model Context Protocol](https://modelcontextprotocol.io/)
