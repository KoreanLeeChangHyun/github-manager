# Architecture Documentation

## Core Components

### server.py
Location: [src/github_manager/server.py](../../src/github_manager/server.py)

**Responsibilities:**
- Main FastMCP server initialization
- Creates singleton `Github` client instance via `get_github_client()`
- Registers all tools from four domain modules
- Exposes two MCP resources:
  - `config://github` - Current configuration
  - `status://rate-limit` - GitHub API rate limit status

**Key Functions:**
- `get_github_client()` - Returns cached PyGithub client
- `main()` - Server entry point

### config.py
Location: [src/github_manager/config.py](../../src/github_manager/config.py)

**Responsibilities:**
- Pydantic-based configuration management
- Loads environment variables via python-dotenv
- Validates required configuration on startup

**Configuration Loading:**
1. `.env` file loaded by `python-dotenv` when `config.py` imports
2. `Config.load()` called in `server.py` on first `get_github_client()` call
3. Global `config` and `github_client` cached in `server.py`
4. Environment variables override defaults in Pydantic models

**Error Handling:**
- Raises `ValueError` from config.py:27, 31 if GITHUB_TOKEN or GITHUB_USERNAME missing

## Tool Organization

Tools are organized into four domain modules under `src/github_manager/`:

### 1. repository/tools.py (8 tools)
**Purpose:** Repository CRUD operations

**Features:**
- Create, delete, list repositories
- Search repositories
- Manage repository topics
- Get repository information

**Key APIs:**
- `client.get_repo()` - Get single repository
- `client.get_user().get_repos()` - List user repositories
- `repo.edit()` - Update repository settings

### 2. automation/tools.py (13 tools)
**Purpose:** GitHub automation workflows

**Features:**
- Issue management
- Pull request operations
- Release management
- Label operations
- Workflow runs

**Key APIs:**
- `repo.get_issues()` - List/filter issues
- `repo.get_pulls()` - List/filter PRs
- `repo.create_issue()` - Create new issue
- `repo.get_workflow_runs()` - List workflow runs

### 3. workspace/tools.py (10 tools)
**Purpose:** Local git operations

**Features:**
- Clone repositories to local workspace
- Git operations (commit, push, pull)
- Branch management
- Status checking

**Key Details:**
- Uses GitPython library
- Clones repos to `WORKSPACE_DIR`
- Path resolution: accepts relative paths (to workspace) or absolute paths
- Uses `Repo` class from `git` module

**Default Location:**
- `~/workspace` (configurable via WORKSPACE_DIR)
- Repository path: `WORKSPACE_DIR/<repo_name>/`

### 4. backup/tools.py (4 tools)
**Purpose:** Repository backup and restore

**Features:**
- Create mirror clones
- Export metadata (issues, PRs, releases) to JSON
- List backups
- Restore from backups

**Backup Structure:**
```
BACKUP_DIR/
├── <repo_name>/
│   └── <timestamp>/
│       ├── repository/     # Mirror clone (bare repo)
│       └── metadata/       # JSON files
│           ├── repository.json
│           ├── issues.json
│           ├── pull_requests.json
│           └── releases.json
```

## Tool Setup Pattern

All domain modules follow the same pattern:

```python
def setup_*_tools(mcp: FastMCP, get_client: Callable) -> str:
    """
    Args:
        mcp: FastMCP instance
        get_client: Callable that returns Github client

    Returns:
        Formatted string describing registered tools
    """

    @mcp.tool()
    def tool_name(...) -> str:
        client = get_client()
        # Tool implementation

    return "Tool descriptions..."
```

**Pattern Benefits:**
- Lazy client initialization
- Consistent error handling
- Clear tool organization
- Easy testing

## GitHub API Interaction

### Client Management
- Single PyGithub client shared across all tools
- Client created once and cached in `server.py`
- Authenticated with GITHUB_TOKEN

### Error Handling
- Catch `GithubException` from PyGithub
- Return formatted error messages to MCP clients
- Include relevant error details (status code, message)

### Rate Limiting
- Check via `client.get_rate_limit()` resource
- Exposed as MCP resource: `status://rate-limit`
- Configurable threshold: `RATE_LIMIT_THRESHOLD`

## Workspace Management

### Path Resolution
- Accepts relative paths (resolved to WORKSPACE_DIR)
- Accepts absolute paths (used as-is)
- Validates `.git` directory exists for repo operations

### Repository Status
- Uses GitPython's `repo.is_dirty()` - Check for uncommitted changes
- Uses `repo.active_branch` - Get current branch
- Uses `repo.untracked_files` - List untracked files

### Clone Operations
- Default clone location: `WORKSPACE_DIR/<repo_name>/`
- Supports both HTTPS and SSH URLs
- Creates parent directories if needed

## Data Flow

### Typical Request Flow
1. MCP client sends tool request
2. FastMCP routes to registered tool function
3. Tool calls `get_client()` to get Github instance
4. Tool makes PyGithub API calls
5. Results formatted and returned to MCP client

### Configuration Flow
1. Server starts
2. First tool call triggers `get_github_client()`
3. `Config.load()` reads `.env` file
4. PyGithub client created with token
5. Client and config cached globally

### Error Flow
1. PyGithub raises `GithubException`
2. Tool catches exception
3. Error formatted as string with details
4. Returned to MCP client for display
