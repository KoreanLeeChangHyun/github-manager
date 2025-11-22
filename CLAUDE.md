# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitHub Manager is a FastMCP server that provides comprehensive GitHub management capabilities through the Model Context Protocol. It exposes 35+ tools for repository management, automation, workspace operations, and backup/restore functionality.

## Development Commands

### Installation and Setup
```bash
# Install dependencies with uv
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run installation script
./install.sh
```

### Running the Server
```bash
# Run MCP server
uv run github-manager-mcp

# Direct Python execution
python -m github_manager.server
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/github_manager --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_repository.py

# Run specific test
uv run pytest tests/test_repository.py::test_list_repositories
```

### Code Quality
```bash
# Format code (line length: 100)
uv run black src/

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

## Architecture

### Core Components

**server.py (src/github_manager/server.py)**
- Main FastMCP server initialization
- Creates singleton `Github` client instance via `get_github_client()`
- Registers all tools from four domain modules
- Exposes two MCP resources: `config://github` and `status://rate-limit`

**config.py (src/github_manager/config.py)**
- Pydantic-based configuration management
- `Config.load()` reads from environment variables (via python-dotenv)
- Required: `GITHUB_TOKEN`, `GITHUB_USERNAME`
- Optional: `GITHUB_ORG`, `WORKSPACE_DIR`, `BACKUP_DIR`, `RATE_LIMIT_THRESHOLD`

### Tool Organization

Tools are organized into four domain modules under `src/github_manager/`:

1. **repository/tools.py** (8 tools)
   - Repository CRUD operations
   - Search and topic management
   - Uses PyGithub's `client.get_repo()`, `client.get_user().get_repos()`

2. **automation/tools.py** (13 tools)
   - Issues, PRs, releases, labels, workflows
   - Uses PyGithub's repository methods like `repo.get_issues()`, `repo.get_pulls()`
   - Workflow runs via `repo.get_workflow_runs()`

3. **workspace/tools.py** (10 tools)
   - Local git operations using GitPython
   - Clones repos to `WORKSPACE_DIR`
   - Path resolution: accepts relative paths (to workspace) or absolute paths
   - Uses `Repo` class from `git` module

4. **backup/tools.py** (4 tools)
   - Creates mirror clones + JSON metadata (issues, PRs, releases)
   - Backup structure: `BACKUP_DIR/<repo_name>/<timestamp>/`
   - Metadata stored as JSON files for programmatic access

### Tool Setup Pattern

Each domain module exports a `setup_*_tools(mcp, get_client)` function that:
- Takes FastMCP instance and a `get_client` callable
- Decorates functions with `@mcp.tool()` to register them
- Returns formatted strings for display in MCP clients

### Configuration Flow

1. `.env` file loaded by `python-dotenv` when `config.py` imports
2. `Config.load()` called in `server.py` on first `get_github_client()` call
3. Global `config` and `github_client` cached in `server.py`
4. Environment variables override defaults in Pydantic models

### GitHub API Interaction

- All GitHub API calls use PyGithub (imported as `Github`)
- Single authenticated client shared across all tools
- Error handling: catches `GithubException` and returns formatted error messages
- Rate limiting checked via `client.get_rate_limit()` resource

### Workspace Management

- Default workspace: `~/workspace`
- Repositories stored as: `WORKSPACE_DIR/<repo_name>/`
- Operations check for `.git` directory to identify repos
- Status tracking uses GitPython's `repo.is_dirty()`, `repo.active_branch`

### Backup Structure

```
BACKUP_DIR/
├── <repo_name>/
│   └── <timestamp>/
│       ├── repository/     # Mirror clone
│       └── metadata/       # JSON files
│           ├── repository.json
│           ├── issues.json
│           ├── pull_requests.json
│           └── releases.json
```

## Environment Configuration

Required for MCP server operation:
- `GITHUB_TOKEN`: Fine-grained token with `repo` (read/write), `workflow` scopes
- `GITHUB_USERNAME`: For default user operations

The server will fail on startup if these are missing (raises `ValueError` from config.py:27, 31).

## Code Style

- Line length: 100 characters (enforced by Black and Ruff)
- Type hints required: `mypy --disallow-untyped-defs`
- Python 3.10+ compatible
- Use `str | None` instead of `Optional[str]` (modern union syntax)

## MCP Integration

To use as MCP server in Claude Code (STDIO mode):
```json
{
  "mcpServers": {
    "github-manager": {
      "command": "uv",
      "args": ["--directory", "/path/to/repo", "run", "github-manager-mcp"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_USERNAME": "username"
      }
    }
  }
}
```

To run in SSE mode (network access):
```bash
# Default port 8001
MCP_TRANSPORT=sse uv run github-manager-mcp

# Custom port
MCP_TRANSPORT=sse MCP_PORT=3000 uv run github-manager-mcp

# Or use the start script
./start_sse.sh --port 8001
```

Server will be available at: http://localhost:8001/sse
