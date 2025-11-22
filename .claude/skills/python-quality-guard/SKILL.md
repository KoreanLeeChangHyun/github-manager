# Python Quality Guard

You are an expert at Python code quality, testing, and following this project's strict quality standards.

## When to Use This Skill

Use this skill when:
- Writing or reviewing tests
- Fixing code quality issues (Black, Ruff, Mypy)
- Ensuring CLAUDE.md rules compliance
- Improving test coverage
- Refactoring code while maintaining quality

## Project Quality Standards

### CRITICAL Rules from CLAUDE.md

```python
# ✅ CORRECT
def get_repo(name: str, private: bool | None = None) -> str:
    """Get repository information."""
    pass

# ❌ WRONG - Using Optional
from typing import Optional
def get_repo(name: str, private: Optional[bool] = None) -> str:
    pass
```

**Mandatory Standards:**
- Line length: 100 characters MAX
- Type hints: Always use `type | None`, never `Optional[type]`
- Import PyGithub: `from github import Github, GithubException`
- Import GitPython: `from git import Repo`
- Error handling: Always catch `GithubException` for GitHub API calls
- Config: Use Pydantic models
- Docstrings: Google style with Args, Returns, Raises

## Testing Patterns

### Test Structure (Arrange-Act-Assert)

```python
import pytest
from github import GithubException
from unittest.mock import Mock, patch


def test_create_repository_success():
    """Test successful repository creation."""
    # Arrange
    repo_name = "test-repo"
    description = "Test repository"
    expected = "Repository test-repo created successfully"

    # Act
    result = create_repository(name=repo_name, description=description)

    # Assert
    assert expected in result
    assert "created successfully" in result


def test_create_repository_already_exists():
    """Test repository creation when repo already exists."""
    # Arrange
    repo_name = "existing-repo"

    # Act
    with patch('github_manager.server.get_github_client') as mock_client:
        mock_user = Mock()
        mock_user.create_repo.side_effect = GithubException(
            422, {"message": "Repository already exists"}
        )
        mock_client.return_value.get_user.return_value = mock_user

        result = create_repository(name=repo_name)

    # Assert
    assert "already exists" in result.lower() or "error" in result.lower()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("repo_name,expected_valid", [
    ("valid-repo", True),
    ("valid_repo", True),
    ("ValidRepo", True),
    ("", False),
    ("invalid repo name", False),
    ("-invalid", False),
])
def test_validate_repo_name(repo_name: str, expected_valid: bool):
    """Test repository name validation."""
    result = validate_repo_name(repo_name)
    assert result == expected_valid
```

### Mocking GitHub API

```python
@patch('github_manager.server.get_github_client')
def test_list_repositories(mock_get_client):
    """Test listing repositories."""
    # Arrange
    mock_client = Mock()
    mock_repo1 = Mock()
    mock_repo1.full_name = "user/repo1"
    mock_repo1.private = False
    mock_repo2 = Mock()
    mock_repo2.full_name = "user/repo2"
    mock_repo2.private = True

    mock_client.get_user.return_value.get_repos.return_value = [
        mock_repo1, mock_repo2
    ]
    mock_get_client.return_value = mock_client

    # Act
    result = list_repositories()

    # Assert
    assert "user/repo1" in result
    assert "user/repo2" in result
```

### Fixture Usage

```python
@pytest.fixture
def mock_github_client():
    """Provide mock GitHub client."""
    with patch('github_manager.server.get_github_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


def test_with_fixture(mock_github_client):
    """Test using fixture."""
    mock_github_client.get_user.return_value.login = "testuser"
    result = get_current_user()
    assert "testuser" in result
```

## Code Quality Tools

### Black (Code Formatter)

```bash
# Format code
uv run black src/

# Check without modifying
uv run black --check src/

# Format specific file
uv run black src/github_manager/repository/tools.py
```

**Black will enforce:**
- 100 character line length (configured in pyproject.toml)
- Consistent string quotes
- Trailing commas
- Spacing around operators

### Ruff (Fast Linter)

```bash
# Check all issues
uv run ruff check src/

# Auto-fix safe issues
uv run ruff check --fix src/

# Check specific rules
uv run ruff check --select E,F src/
```

**Common Ruff Errors to Fix:**

```python
# E501: Line too long
# ❌ WRONG
def very_long_function_name_that_exceeds_the_maximum_allowed_line_length(parameter1, parameter2, parameter3):
    pass

# ✅ CORRECT
def very_long_function_name_that_exceeds_maximum(
    parameter1: str,
    parameter2: int,
    parameter3: bool
) -> None:
    pass


# F401: Unused import
# ❌ WRONG
from github import Github, GithubException
from typing import Optional  # Not used

# ✅ CORRECT
from github import Github, GithubException


# F841: Unused variable
# ❌ WRONG
def process_repo():
    unused_var = get_client()
    return "done"

# ✅ CORRECT
def process_repo():
    client = get_client()
    return f"Processed with {client.get_user().login}"
```

### Mypy (Type Checker)

```bash
# Type check all files
uv run mypy src/

# Check specific file
uv run mypy src/github_manager/repository/tools.py

# Show error codes
uv run mypy --show-error-codes src/
```

**Common Mypy Errors:**

```python
# error: Missing return statement
# ❌ WRONG
def get_repo_name(repo_id: int) -> str:
    if repo_id > 0:
        return "valid"
    # Missing return for else case

# ✅ CORRECT
def get_repo_name(repo_id: int) -> str:
    if repo_id > 0:
        return "valid"
    return "invalid"


# error: Incompatible return value type
# ❌ WRONG
def get_count() -> int:
    return "5"  # str, not int

# ✅ CORRECT
def get_count() -> int:
    return 5


# error: Need type annotation
# ❌ WRONG
def process_data(items):
    return [x * 2 for x in items]

# ✅ CORRECT
def process_data(items: list[int]) -> list[int]:
    return [x * 2 for x in items]


# error: Optional[] is deprecated
# ❌ WRONG
from typing import Optional
def get_value() -> Optional[str]:
    return None

# ✅ CORRECT
def get_value() -> str | None:
    return None
```

## Test Coverage

### Running with Coverage

```bash
# Run tests with coverage
uv run pytest --cov=src/github_manager --cov-report=term-missing

# Generate HTML report
uv run pytest --cov=src/github_manager --cov-report=html

# Fail if coverage below threshold
uv run pytest --cov=src/github_manager --cov-fail-under=80
```

### Coverage Report Interpretation

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/github_manager/__init__.py              2      0   100%
src/github_manager/server.py               45      5    89%   67-71
src/github_manager/config.py               20      2    90%   35, 42
src/github_manager/repository/tools.py    120     15    87%   89-95, 120-125
---------------------------------------------------------------------
TOTAL                                     187     22    88%
```

**What to focus on:**
- Lines in "Missing" column need test coverage
- Aim for 80%+ overall coverage
- Critical paths should have 100% coverage

### Improving Coverage

```python
# Before: 50% coverage
def process_repo(name: str) -> str:
    """Process repository."""
    try:
        client = get_client()
        repo = client.get_repo(name)
        return f"Processed {repo.full_name}"
    except GithubException as e:  # NOT TESTED
        return f"Error: {e}"       # NOT TESTED


# After: 100% coverage with tests
def test_process_repo_success():
    """Test successful processing."""
    result = process_repo("user/repo")
    assert "Processed" in result


def test_process_repo_not_found():
    """Test repo not found error."""
    with patch('github_manager.server.get_github_client') as mock:
        mock.return_value.get_repo.side_effect = GithubException(404, {})
        result = process_repo("invalid/repo")
        assert "Error" in result
```

## Pre-Commit Quality Checks

### Manual Quality Check Script

```bash
#!/bin/bash
# scripts/quality_check.sh

echo "Running quality checks..."

echo "1. Black formatting..."
uv run black src/ || exit 1

echo "2. Ruff linting..."
uv run ruff check src/ || exit 1

echo "3. Mypy type checking..."
uv run mypy src/ || exit 1

echo "4. Running tests..."
uv run pytest || exit 1

echo "✅ All quality checks passed!"
```

### Using as Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
./scripts/quality_check.sh
```

## Refactoring Guidelines

### When to Refactor

- Function > 50 lines → Split into smaller functions
- Duplicate code appears 3+ times → Extract to function
- Complex conditional logic → Extract to named functions
- Type hints missing → Add them
- No tests → Write tests first

### Safe Refactoring Steps

1. **Write tests first** (if they don't exist)
2. **Run tests** - Ensure they pass
3. **Refactor** - Make changes
4. **Run tests again** - Ensure still passing
5. **Run quality tools** - Black, Ruff, Mypy
6. **Commit** - Small, focused commits

### Example Refactoring

```python
# BEFORE: Long, complex function
def handle_repository(name: str, action: str, value: str | None = None) -> str:
    try:
        client = get_client()
        repo = client.get_repo(name)
        if action == "archive":
            repo.edit(archived=True)
            return "Archived"
        elif action == "unarchive":
            repo.edit(archived=False)
            return "Unarchived"
        elif action == "visibility":
            if value == "private":
                repo.edit(private=True)
                return "Made private"
            elif value == "public":
                repo.edit(private=False)
                return "Made public"
        elif action == "description":
            repo.edit(description=value)
            return "Description updated"
    except GithubException as e:
        return f"Error: {e}"


# AFTER: Refactored into focused functions
def archive_repository(repo_name: str, archive: bool = True) -> str:
    """Archive or unarchive repository."""
    try:
        client = get_client()
        repo = client.get_repo(repo_name)
        repo.edit(archived=archive)
        return f"Repository {'archived' if archive else 'unarchived'}"
    except GithubException as e:
        return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"


def set_repository_visibility(repo_name: str, private: bool) -> str:
    """Set repository visibility."""
    try:
        client = get_client()
        repo = client.get_repo(repo_name)
        repo.edit(private=private)
        visibility = "private" if private else "public"
        return f"Repository visibility set to {visibility}"
    except GithubException as e:
        return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"


def update_repository_description(repo_name: str, description: str) -> str:
    """Update repository description."""
    try:
        client = get_client()
        repo = client.get_repo(repo_name)
        repo.edit(description=description)
        return "Repository description updated"
    except GithubException as e:
        return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"
```

## Common Quality Issues and Fixes

### Issue 1: Long Lines

```python
# ❌ WRONG (120 characters)
def create_issue_with_labels(repo_name: str, title: str, body: str, labels: list[str]) -> str:
    return client.get_repo(repo_name).create_issue(title=title, body=body, labels=labels)

# ✅ CORRECT
def create_issue_with_labels(
    repo_name: str,
    title: str,
    body: str,
    labels: list[str]
) -> str:
    """Create issue with labels."""
    repo = client.get_repo(repo_name)
    issue = repo.create_issue(title=title, body=body, labels=labels)
    return f"Issue #{issue.number} created"
```

### Issue 2: Missing Type Hints

```python
# ❌ WRONG
def process_items(items, multiplier=2):
    return [x * multiplier for x in items]

# ✅ CORRECT
def process_items(items: list[int], multiplier: int = 2) -> list[int]:
    """Process items by multiplying each by multiplier."""
    return [x * multiplier for x in items]
```

### Issue 3: Poor Error Messages

```python
# ❌ WRONG
except GithubException as e:
    return "Error"

# ✅ CORRECT
except GithubException as e:
    if e.status == 404:
        return f"Repository {repo_name} not found"
    elif e.status == 403:
        return "Permission denied - check token scopes"
    return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"
```

## Quality Checklist

Before committing, verify:
- [ ] All functions have type hints
- [ ] All functions have docstrings (Google style)
- [ ] Line length ≤ 100 characters
- [ ] Using `type | None` not `Optional[type]`
- [ ] Black formatting applied: `uv run black src/`
- [ ] Ruff checks pass: `uv run ruff check src/`
- [ ] Mypy checks pass: `uv run mypy src/`
- [ ] All tests pass: `uv run pytest`
- [ ] Coverage ≥ 80%: `uv run pytest --cov=src/github_manager --cov-fail-under=80`
- [ ] No unused imports or variables
- [ ] Error handling for all GitHub API calls
- [ ] Documentation updated if needed

## Resources

- pytest docs: https://docs.pytest.org/
- Black: https://black.readthedocs.io/
- Ruff: https://docs.astral.sh/ruff/
- Mypy: https://mypy.readthedocs.io/
- Project standards: CLAUDE.md
- Test examples: tests/
