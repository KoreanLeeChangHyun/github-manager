# CLAUDE.md

FastMCP server for GitHub management. Python 3.10+, PyGithub, GitPython, FastMCP, pytest.

## Commands

```bash
# Install
uv pip install -e ".[dev]"

# Run server
uv run github-manager-mcp                          # STDIO mode
MCP_TRANSPORT=sse uv run github-manager-mcp        # SSE mode (port 8001)

# Test
uv run pytest                                       # All tests
uv run pytest tests/test_<module>.py               # Specific module

# Code quality
uv run black src/ && uv run ruff check src/ && uv run mypy src/
```

## Code Style Rules

IMPORTANT: Enforce strictly:
- Line length: 100 max
- Type hints required (mypy --disallow-untyped-defs)
- Use `str | None` not `Optional[str]`
- Import: `Github` from PyGithub, `Repo` from git
- Catch `GithubException` for API errors
- Pydantic models for config

## Environment Setup

REQUIRED: `GITHUB_TOKEN`, `GITHUB_USERNAME`
Optional: `GITHUB_ORG`, `WORKSPACE_DIR`, `BACKUP_DIR`, `RATE_LIMIT_THRESHOLD`

See [.claude/docs/environment.md](.claude/docs/environment.md) for detailed setup.

## Project Structure

```
src/github_manager/
├── server.py           # Main server, tool registration
├── config.py           # Environment config (Pydantic)
├── repository/         # 8 tools: CRUD, search, topics
├── automation/         # 13 tools: issues, PRs, workflows
├── workspace/          # 10 tools: git operations
└── backup/             # 4 tools: mirror + metadata
```

## Development Workflow

IMPORTANT: Follow this sequence for ALL code changes:

1. **Code**: Make changes to source files
2. **Test**: Run `uv run pytest` - Must pass before proceeding
3. **Quality**: Run `uv run black src/ && uv run ruff check src/ && uv run mypy src/`
4. **Document**: Update relevant docs in `.claude/docs/` if architecture/config changed
5. **Commit**: Create commit with clear message
6. **Push**: Push to remote repository

NEVER skip steps. NEVER commit without passing tests.

## Git Workflow

IMPORTANT: Commit message rules:
- Write in Korean (한국어로 작성)
- NEVER add Co-Authored-By or emoji
- Format: `<type>: <description>`
- Types: feat, fix, docs, refactor, test, chore

```bash
# After code changes and tests pass
git add .
git commit -m "docs: 문서 업데이트"
git push origin <branch-name>
```

## Documentation

For detailed information, see:
- [Architecture](.claude/docs/architecture.md) - Components, tool organization, data flow
- [Environment](.claude/docs/environment.md) - Configuration, MCP setup, security
