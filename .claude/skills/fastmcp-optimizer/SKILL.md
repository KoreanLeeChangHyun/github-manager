# FastMCP Optimizer

You are an expert at optimizing FastMCP servers for performance, reliability, and best practices.

## When to Use This Skill

Use this skill when:
- Optimizing MCP server performance
- Implementing MCP resources
- Handling rate limiting and quotas
- Improving error handling and logging
- Scaling MCP servers
- Adding monitoring and observability

## FastMCP Server Optimization

### Server Configuration

```python
from mcp.server.fastmcp import FastMCP

# Optimized server initialization
mcp = FastMCP(
    "GitHub Manager",
    version="1.0.0",
    dependencies=["PyGithub>=2.1.1", "GitPython>=3.1.40"]
)
```

### Resource Management

```python
from mcp.types import Resource, TextContent
from datetime import datetime


@mcp.resource("config://github")
def get_github_config() -> Resource:
    """Expose GitHub configuration as MCP resource.

    Returns configuration without exposing secrets.
    """
    config = Config.load()

    return Resource(
        uri="config://github",
        name="GitHub Configuration",
        description="Current GitHub Manager configuration",
        mimeType="application/json",
        text=TextContent(
            text=json.dumps({
                "username": config.github_username,
                "org": config.github_org,
                "workspace_dir": str(config.workspace_dir),
                "backup_dir": str(config.backup_dir),
                # NEVER expose GITHUB_TOKEN
            }, indent=2)
        )
    )


@mcp.resource("status://rate-limit")
def get_rate_limit_status() -> Resource:
    """Expose GitHub API rate limit status."""
    client = get_github_client()
    rate_limit = client.get_rate_limit()

    core = rate_limit.core
    remaining_percent = (core.remaining / core.limit) * 100

    status = {
        "limit": core.limit,
        "remaining": core.remaining,
        "used": core.limit - core.remaining,
        "reset_at": core.reset.isoformat(),
        "remaining_percent": round(remaining_percent, 2),
        "status": "healthy" if remaining_percent > 20 else "warning"
    }

    return Resource(
        uri="status://rate-limit",
        name="GitHub API Rate Limit",
        description="Current GitHub API rate limit status",
        mimeType="application/json",
        text=TextContent(text=json.dumps(status, indent=2))
    )
```

## Rate Limiting Strategy

### Implementing Rate Limit Checks

```python
from functools import wraps
from typing import Callable, Any


def check_rate_limit(threshold: int = 100) -> Callable:
    """Decorator to check rate limit before API calls.

    Args:
        threshold: Minimum remaining calls before warning

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> str:
            try:
                client = get_github_client()
                rate_limit = client.get_rate_limit()

                if rate_limit.core.remaining < threshold:
                    reset_time = rate_limit.core.reset
                    return (
                        f"Rate limit warning: Only {rate_limit.core.remaining} "
                        f"requests remaining. Resets at {reset_time}"
                    )

                return func(*args, **kwargs)

            except Exception as e:
                return f"Rate limit check failed: {str(e)}"

        return wrapper
    return decorator


# Usage
@mcp.tool()
@check_rate_limit(threshold=100)
def expensive_operation(repo_name: str) -> str:
    """Operation that makes many API calls."""
    # Implementation
    pass
```

### Automatic Retry with Backoff

```python
import time
from typing import TypeVar, Callable

T = TypeVar('T')


def retry_on_rate_limit(
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Callable:
    """Retry function on rate limit errors with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except GithubException as e:
                    if e.status == 403 and "rate limit" in str(e).lower():
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            time.sleep(delay)
                            continue
                    raise

            return func(*args, **kwargs)

        return wrapper
    return decorator


# Usage
@mcp.tool()
@retry_on_rate_limit(max_retries=3)
def resilient_operation(repo_name: str) -> str:
    """Operation with automatic retry on rate limits."""
    client = get_github_client()
    repo = client.get_repo(repo_name)
    return f"Repository: {repo.full_name}"
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from typing import Any
import time


class TimedCache:
    """Simple time-based cache for API responses."""

    def __init__(self, ttl: int = 300):
        """Initialize cache.

        Args:
            ttl: Time-to-live in seconds
        """
        self.ttl = ttl
        self.cache: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """Get cached value if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value with current timestamp."""
        self.cache[key] = (value, time.time())


# Global cache instance
repo_cache = TimedCache(ttl=300)  # 5 minutes


@mcp.tool()
def get_repository_cached(repo_name: str) -> str:
    """Get repository info with caching.

    Args:
        repo_name: Repository name in format 'owner/name'

    Returns:
        Repository information
    """
    # Check cache first
    cached = repo_cache.get(repo_name)
    if cached:
        return f"[CACHED] {cached}"

    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)

        result = (
            f"Repository: {repo.full_name}\n"
            f"Description: {repo.description}\n"
            f"Stars: {repo.stargazers_count}\n"
            f"Forks: {repo.forks_count}"
        )

        # Store in cache
        repo_cache.set(repo_name, result)

        return result

    except GithubException as e:
        return f"Error: {e.status} - {e.data.get('message', str(e))}"
```

### Batch Operations

```python
@mcp.tool()
def batch_update_labels(
    repo_name: str,
    issue_numbers: list[int],
    labels: list[str]
) -> str:
    """Update labels for multiple issues in one operation.

    More efficient than individual updates.

    Args:
        repo_name: Repository name
        issue_numbers: List of issue numbers
        labels: Labels to add

    Returns:
        Summary of updates
    """
    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)

        # Batch fetch issues
        issues = [repo.get_issue(num) for num in issue_numbers]

        # Batch update
        success_count = 0
        for issue in issues:
            try:
                issue.add_to_labels(*labels)
                success_count += 1
            except GithubException:
                continue

        return (
            f"Updated {success_count}/{len(issues)} issues "
            f"with labels: {', '.join(labels)}"
        )

    except GithubException as e:
        return f"Error: {e.status} - {e.data.get('message', str(e))}"
```

## Error Handling Best Practices

### Structured Error Responses

```python
from dataclasses import dataclass
import json


@dataclass
class ErrorResponse:
    """Structured error response."""
    error_type: str
    message: str
    details: dict[str, Any] | None = None
    suggestion: str | None = None

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "error": self.error_type,
            "message": self.message,
            "details": self.details or {},
            "suggestion": self.suggestion or ""
        }, indent=2)


def handle_github_error(e: GithubException, context: str = "") -> str:
    """Convert GithubException to structured error response.

    Args:
        e: GitHub exception
        context: Additional context about the operation

    Returns:
        Formatted error message
    """
    error_map = {
        401: ErrorResponse(
            error_type="authentication_failed",
            message="GitHub authentication failed",
            suggestion="Check GITHUB_TOKEN environment variable"
        ),
        403: ErrorResponse(
            error_type="permission_denied",
            message="Permission denied",
            suggestion="Verify token has required scopes (repo, workflow)"
        ),
        404: ErrorResponse(
            error_type="not_found",
            message=f"Resource not found: {context}",
            suggestion="Verify repository/resource name is correct"
        ),
        422: ErrorResponse(
            error_type="validation_error",
            message="Validation error",
            details=e.data
        ),
    }

    if e.status in error_map:
        return error_map[e.status].to_json()

    # Generic error
    return ErrorResponse(
        error_type="github_api_error",
        message=f"GitHub API error: {e.status}",
        details=e.data
    ).to_json()


# Usage
@mcp.tool()
def optimized_tool(repo_name: str) -> str:
    """Tool with structured error handling."""
    try:
        client = get_github_client()
        repo = client.get_repo(repo_name)
        return f"Success: {repo.full_name}"

    except GithubException as e:
        return handle_github_error(e, context=repo_name)
```

## Logging and Monitoring

### Structured Logging

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("github_manager")


def log_tool_execution(func: Callable) -> Callable:
    """Decorator to log tool execution.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        start_time = time.time()
        tool_name = func.__name__

        logger.info(f"Tool started: {tool_name}", extra={
            "tool": tool_name,
            "args": args,
            "kwargs": kwargs
        })

        try:
            result = func(*args, **kwargs)

            duration = time.time() - start_time
            logger.info(f"Tool completed: {tool_name}", extra={
                "tool": tool_name,
                "duration": duration,
                "success": True
            })

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Tool failed: {tool_name}", extra={
                "tool": tool_name,
                "duration": duration,
                "error": str(e),
                "success": False
            })
            raise

    return wrapper


# Usage
@mcp.tool()
@log_tool_execution
def monitored_tool(param: str) -> str:
    """Tool with automatic logging."""
    # Implementation
    pass
```

### Performance Metrics

```python
from collections import defaultdict
from typing import DefaultDict


class PerformanceMonitor:
    """Monitor tool performance metrics."""

    def __init__(self):
        self.call_counts: DefaultDict[str, int] = defaultdict(int)
        self.total_duration: DefaultDict[str, float] = defaultdict(float)
        self.error_counts: DefaultDict[str, int] = defaultdict(int)

    def record_call(
        self,
        tool_name: str,
        duration: float,
        success: bool
    ) -> None:
        """Record tool execution metrics."""
        self.call_counts[tool_name] += 1
        self.total_duration[tool_name] += duration
        if not success:
            self.error_counts[tool_name] += 1

    def get_stats(self, tool_name: str) -> dict[str, Any]:
        """Get statistics for a tool."""
        calls = self.call_counts[tool_name]
        if calls == 0:
            return {}

        return {
            "calls": calls,
            "errors": self.error_counts[tool_name],
            "error_rate": self.error_counts[tool_name] / calls,
            "avg_duration": self.total_duration[tool_name] / calls,
            "total_duration": self.total_duration[tool_name]
        }


# Global monitor instance
monitor = PerformanceMonitor()


@mcp.resource("metrics://tools")
def get_tool_metrics() -> Resource:
    """Expose tool performance metrics."""
    stats = {
        tool: monitor.get_stats(tool)
        for tool in monitor.call_counts.keys()
    }

    return Resource(
        uri="metrics://tools",
        name="Tool Performance Metrics",
        description="Performance metrics for all MCP tools",
        mimeType="application/json",
        text=TextContent(text=json.dumps(stats, indent=2))
    )
```

## Configuration Management

### Environment-Based Config

```python
from pydantic import BaseModel, Field
from pathlib import Path


class OptimizedConfig(BaseModel):
    """Optimized configuration with validation."""

    # GitHub
    github_token: str = Field(..., min_length=1)
    github_username: str = Field(..., min_length=1)
    github_org: str | None = None

    # Paths
    workspace_dir: Path = Path.home() / "workspace"
    backup_dir: Path = Path.home() / "backups"

    # Performance
    rate_limit_threshold: int = Field(default=100, ge=10)
    cache_ttl: int = Field(default=300, ge=0)
    max_retries: int = Field(default=3, ge=1, le=10)

    # Logging
    log_level: str = Field(default="INFO")
    log_file: Path | None = None

    class Config:
        env_prefix = "GITHUB_"

    @classmethod
    def load(cls) -> "OptimizedConfig":
        """Load configuration from environment."""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN", ""),
            github_username=os.getenv("GITHUB_USERNAME", ""),
            github_org=os.getenv("GITHUB_ORG"),
        )
```

## Server Lifecycle Management

### Graceful Shutdown

```python
import signal
import sys


def setup_signal_handlers():
    """Setup handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")

        # Cleanup operations
        logger.info("Flushing caches...")
        repo_cache.cache.clear()

        logger.info("Closing connections...")
        # Close any open connections

        logger.info("Shutdown complete")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Call during server initialization
setup_signal_handlers()
```

## Optimization Checklist

When optimizing MCP server:
- [ ] Implement rate limit checking for expensive operations
- [ ] Add caching for frequently accessed data
- [ ] Use batch operations where possible
- [ ] Implement structured error responses
- [ ] Add comprehensive logging
- [ ] Expose metrics as MCP resources
- [ ] Configure appropriate timeouts
- [ ] Implement graceful shutdown
- [ ] Monitor memory usage for caches
- [ ] Document performance characteristics

## Common Performance Issues

### Issue 1: Repeated API Calls

```python
# ❌ WRONG - Multiple API calls for same data
def get_repo_info(repo_name: str) -> str:
    repo1 = client.get_repo(repo_name)  # API call
    repo2 = client.get_repo(repo_name)  # Duplicate call
    return f"{repo1.name} - {repo2.stars}"

# ✅ CORRECT - Single API call with caching
def get_repo_info(repo_name: str) -> str:
    repo = client.get_repo(repo_name)  # Single call
    return f"{repo.name} - {repo.stargazers_count}"
```

### Issue 2: No Rate Limit Protection

```python
# ❌ WRONG - No rate limit check
@mcp.tool()
def bulk_operation(repos: list[str]) -> str:
    for repo in repos:  # Could exceed rate limit
        process_repo(repo)

# ✅ CORRECT - With rate limit check
@mcp.tool()
@check_rate_limit(threshold=len(repos) * 2)
def bulk_operation(repos: list[str]) -> str:
    for repo in repos:
        process_repo(repo)
```

## Resources

- FastMCP docs: https://github.com/jlowin/fastmcp
- MCP specification: https://modelcontextprotocol.io/
- Project server: src/github_manager/server.py
- Configuration: src/github_manager/config.py
