# Environment Configuration

## Required Variables

### GITHUB_TOKEN
**Required:** Yes
**Purpose:** Authenticate with GitHub API

**Setup:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Generate new token with the following permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
3. Copy token to `.env` file

**Example:**
```bash
GITHUB_TOKEN=github_pat_11ABCDEFG...
```

**Error if missing:**
- Server will raise `ValueError` from config.py:27
- Error message: "GITHUB_TOKEN environment variable is required"

### GITHUB_USERNAME
**Required:** Yes
**Purpose:** Default user for repository operations

**Example:**
```bash
GITHUB_USERNAME=your-github-username
```

**Error if missing:**
- Server will raise `ValueError` from config.py:31
- Error message: "GITHUB_USERNAME environment variable is required"

## Optional Variables

### GITHUB_ORG
**Required:** No
**Default:** None
**Purpose:** Organization name for org-level operations

**Example:**
```bash
GITHUB_ORG=my-organization
```

**Usage:**
- Used by tools that operate on organization repositories
- If not set, operations default to user repositories

### WORKSPACE_DIR
**Required:** No
**Default:** `~/workspace`
**Purpose:** Base directory for cloned repositories

**Example:**
```bash
WORKSPACE_DIR=/home/user/projects
```

**Usage:**
- All repository clones stored in this directory
- Repository path: `WORKSPACE_DIR/<repo_name>/`
- Must be writable by the user running the server

### BACKUP_DIR
**Required:** No
**Default:** `~/backups`
**Purpose:** Base directory for repository backups

**Example:**
```bash
BACKUP_DIR=/home/user/github-backups
```

**Usage:**
- Backups stored as: `BACKUP_DIR/<repo_name>/<timestamp>/`
- Each backup includes mirror clone + JSON metadata
- Must be writable by the user running the server

### RATE_LIMIT_THRESHOLD
**Required:** No
**Default:** 100
**Purpose:** Warn when remaining API calls drop below threshold

**Example:**
```bash
RATE_LIMIT_THRESHOLD=50
```

**Usage:**
- Check via `status://rate-limit` MCP resource
- GitHub API limits:
  - 5,000 requests/hour for authenticated requests
  - 60 requests/hour for unauthenticated requests

## Configuration File Setup

### .env File (Recommended)

Create `.env` file in project root:

```bash
# Required
GITHUB_TOKEN=github_pat_11ABCDEFG...
GITHUB_USERNAME=your-username

# Optional
GITHUB_ORG=my-organization
WORKSPACE_DIR=/home/user/workspace
BACKUP_DIR=/home/user/backups
RATE_LIMIT_THRESHOLD=100
```

**Important:**
- Never commit `.env` to version control
- Add `.env` to `.gitignore`
- Use `.env.example` for team documentation

### Environment Variables

Alternatively, export variables in shell:

```bash
export GITHUB_TOKEN="github_pat_11ABCDEFG..."
export GITHUB_USERNAME="your-username"
```

**Precedence:**
- Environment variables override `.env` file values
- Pydantic models use environment variables first, then `.env` values

## MCP Server Configuration

### STDIO Mode (Claude Desktop)

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "github-manager": {
      "command": "uv",
      "args": ["--directory", "/path/to/github-manager-mcp", "run", "github-manager-mcp"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_USERNAME": "your-username"
      }
    }
  }
}
```

**Notes:**
- `${GITHUB_TOKEN}` references environment variable
- Can also hardcode values (not recommended for security)
- Path must be absolute

### SSE Mode (Network Access)

Run server with SSE transport:

```bash
# Use .env file
MCP_TRANSPORT=sse uv run github-manager-mcp

# Custom port
MCP_TRANSPORT=sse MCP_PORT=3000 uv run github-manager-mcp

# Or use start script
./start_sse.sh --port 8001
```

**Environment Variables for SSE:**
- `MCP_TRANSPORT=sse` - Enable SSE mode
- `MCP_PORT=8001` - Port number (default: 8001)

**Server URL:**
- Default: http://localhost:8001/sse
- Custom port: http://localhost:{PORT}/sse

## Configuration Validation

### Startup Checks

Server validates configuration on startup:

1. Loads `.env` file via `python-dotenv`
2. `Config.load()` validates required variables
3. Raises `ValueError` if GITHUB_TOKEN or GITHUB_USERNAME missing
4. Creates default directories if WORKSPACE_DIR or BACKUP_DIR not exist

### Runtime Checks

During operation:
- GitHub token validity checked on first API call
- Rate limits checked via `client.get_rate_limit()`
- Directory permissions validated on clone/backup operations

### Common Errors

**"GITHUB_TOKEN environment variable is required"**
- Add GITHUB_TOKEN to `.env` or environment variables
- Verify token is not expired
- Check token has required permissions

**"GITHUB_USERNAME environment variable is required"**
- Add GITHUB_USERNAME to `.env` or environment variables
- Must match GitHub account name exactly (case-sensitive)

**"Permission denied" errors**
- Check WORKSPACE_DIR and BACKUP_DIR are writable
- Verify user has permissions for specified directories

## Security Best Practices

1. **Never commit tokens**
   - Add `.env` to `.gitignore`
   - Use environment variables in CI/CD
   - Rotate tokens regularly

2. **Use fine-grained tokens**
   - Grant minimum required permissions
   - Set expiration dates
   - Limit repository access if possible

3. **Protect .env file**
   ```bash
   chmod 600 .env  # Read/write for owner only
   ```

4. **Use separate tokens**
   - Development token for local work
   - Production token for deployed servers
   - Different tokens per team member
