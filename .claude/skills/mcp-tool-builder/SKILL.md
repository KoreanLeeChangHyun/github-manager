# MCP Tool Builder

You are an expert at building MCP tools for the GitHub Manager project following established patterns and best practices.

## When to Use This Skill

Use this skill when:
- Adding new MCP tools to the project
- Creating new domain modules (repository, automation, workspace, backup)
- Implementing GitHub API integrations
- Need to follow the project's tool setup pattern

## Tool Development Pattern

### 1. Tool Function Structure

All tools must follow this pattern:

```python
@mcp.tool()
def tool_name(
    param1: str,
    param2: int | None = None
) -> str:
    """Clear, concise description.

    Args:
        param1: Description of param1
        param2: Description of param2 (optional)

    Returns:
        Success message or error details
    """
    try:
        client = get_client()

        # Implementation
        result = client.some_api_call(param1, param2)

        return f"Success: {result}"

    except GithubException as e:
        return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### 2. Module Structure

Each domain module must have:

```python
from typing import Callable
from github import Github, GithubException
from mcp.server.fastmcp import FastMCP


def setup_module_tools(mcp: FastMCP, get_client: Callable[[], Github]) -> str:
    """Setup module-specific tools.

    Args:
        mcp: FastMCP instance
        get_client: Callable that returns authenticated Github client

    Returns:
        Description of registered tools
    """

    @mcp.tool()
    def tool_1(...):
        """Tool 1 implementation"""
        pass

    @mcp.tool()
    def tool_2(...):
        """Tool 2 implementation"""
        pass

    return """
    Registered tools:
    - tool_1: Description
    - tool_2: Description
    """
```

### 3. Registration in server.py

Add to server.py:

```python
from github_manager.module_name.tools import setup_module_tools

# In main() function
setup_module_tools(mcp, get_github_client)
```

## Code Style Requirements

CRITICAL - Always enforce:
- Line length: 100 characters max
- Type hints required: `param: str | None` not `Optional[str]`
- Import `Github, GithubException` from `github`
- Catch `GithubException` for all GitHub API calls
- Use Pydantic models for complex configurations
- Docstrings: Google style with Args, Returns, Raises

## Error Handling Best Practices

```python
try:
    # GitHub API calls
    result = client.get_repo("owner/repo")

except GithubException as e:
    # Specific GitHub errors
    if e.status == 404:
        return "Repository not found"
    elif e.status == 403:
        return "Permission denied - check token scopes"
    return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"

except Exception as e:
    # Unexpected errors
    return f"Unexpected error: {str(e)}"
```

## PyGithub Common Patterns

### Repository Operations
```python
# Get repository
repo = client.get_repo("owner/name")

# Create repository
user = client.get_user()
repo = user.create_repo(name, description=desc, private=True)

# List repositories
repos = client.get_user().get_repos()
for repo in repos:
    print(repo.full_name)
```

### Issue/PR Operations
```python
# Create issue
issue = repo.create_issue(title="Title", body="Body", labels=["bug"])

# Get pull requests
pulls = repo.get_pulls(state="open")

# Create pull request
pr = repo.create_pull(title="Title", body="Body", head="feature", base="main")
```

### Workflow Operations
```python
# List workflows
workflows = repo.get_workflows()

# Trigger workflow
workflow = repo.get_workflow("ci.yml")
workflow.create_dispatch(ref="main", inputs={"key": "value"})

# Get workflow runs
runs = repo.get_workflow_runs()
```

## Testing Requirements

For each new tool, create a test:

```python
def test_tool_name():
    """Test tool_name functionality."""
    # Arrange
    expected = "expected result"

    # Act
    result = tool_name(param1="value")

    # Assert
    assert expected in result
```

## Documentation Updates

After adding tools, update:
1. `.claude/docs/architecture.md` - Add tool description to relevant module section
2. `CLAUDE.md` - Update tool count if adding new module
3. Module docstring - List all tools with brief descriptions

## Quick Checklist

Before committing new tools:
- [ ] Type hints on all parameters and return values
- [ ] Docstring with Args, Returns sections
- [ ] GithubException error handling
- [ ] Line length ≤ 100 characters
- [ ] Test written and passing
- [ ] Documentation updated
- [ ] Registered in server.py
- [ ] Follows `setup_*_tools()` pattern

## Example: Adding a New Tool

```python
# File: src/github_manager/repository/tools.py

@mcp.tool()
def archive_repository(repo_name: str, archive: bool = True) -> str:
    """Archive or unarchive a repository.

    Args:
        repo_name: Repository name in format 'owner/name'
        archive: True to archive, False to unarchive

    Returns:
        Success message or error details
    """
    try:
        client = get_client()
        repo = client.get_repo(repo_name)

        repo.edit(archived=archive)

        action = "archived" if archive else "unarchived"
        return f"Repository {repo_name} successfully {action}"

    except GithubException as e:
        return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"
```

## Common Pitfalls to Avoid

1. **Missing error handling**: Always catch GithubException
2. **Type hints**: Never use Optional[], always use `type | None`
3. **Line length**: Keep under 100 characters
4. **Client creation**: Always use `get_client()`, never create new client
5. **Return types**: Always return `str`, not dict or object
6. **Documentation**: Update architecture docs when adding tools
7. **Testing**: Write tests before considering tool complete

## Resources

- PyGithub docs: https://pygithub.readthedocs.io/
- Project architecture: .claude/docs/architecture.md
- Code style rules: CLAUDE.md
- Existing tools: src/github_manager/*/tools.py
