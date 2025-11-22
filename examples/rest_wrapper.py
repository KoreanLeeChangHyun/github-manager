"""REST API wrapper for GitHub Manager MCP Server.

This wrapper allows non-MCP clients (ChatGPT, Gemini, etc.) to access
the MCP server through a standard REST API.

Usage:
    1. Start MCP server in SSE mode:
       MCP_TRANSPORT=sse uv run github-manager-mcp

    2. Start this REST wrapper:
       python examples/rest_wrapper.py

    3. Access via HTTP:
       curl http://localhost:9000/api/repositories?limit=5
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import json
from typing import Any, Optional
import uvicorn

app = FastAPI(
    title="GitHub Manager REST API",
    description="REST API wrapper for GitHub Manager MCP Server",
    version="0.1.0"
)

# MCP server URL
MCP_SERVER_URL = "http://localhost:8000/sse"


class ToolCallRequest(BaseModel):
    """Generic tool call request."""
    tool_name: str
    arguments: dict[str, Any] = {}


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call MCP server tool via SSE endpoint.

    Note: This is a simplified implementation.
    For production, use proper MCP client library.
    """
    # For this example, we'll make HTTP POST to a hypothetical endpoint
    # In reality, you'd need to implement full MCP protocol over SSE

    # Placeholder - actual implementation would use MCP client
    raise NotImplementedError(
        "Full MCP client implementation required. "
        "See docs/connecting-llms.md for complete implementation."
    )


# Repository endpoints
@app.get("/api/repositories")
async def list_repositories(
    username: Optional[str] = None,
    sort: str = "updated",
    direction: str = "desc",
    limit: int = 30
):
    """List GitHub repositories."""
    return {
        "tool": "list_repositories",
        "arguments": {
            "username": username,
            "sort": sort,
            "direction": direction,
            "limit": limit
        },
        "note": "Connect this to MCP server using proper MCP client library"
    }


@app.get("/api/repositories/{owner}/{repo}")
async def get_repository(owner: str, repo: str):
    """Get repository information."""
    return {
        "tool": "get_repository_info",
        "arguments": {"repo_name": f"{owner}/{repo}"},
        "note": "Connect this to MCP server using proper MCP client library"
    }


@app.post("/api/repositories")
async def create_repository(
    name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = True
):
    """Create a new repository."""
    return {
        "tool": "create_repository",
        "arguments": {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        },
        "note": "Connect this to MCP server using proper MCP client library"
    }


# Issues endpoints
@app.get("/api/repositories/{owner}/{repo}/issues")
async def list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    limit: int = 20
):
    """List repository issues."""
    return {
        "tool": "list_issues",
        "arguments": {
            "repo_name": f"{owner}/{repo}",
            "state": state,
            "limit": limit
        },
        "note": "Connect this to MCP server using proper MCP client library"
    }


@app.post("/api/repositories/{owner}/{repo}/issues")
async def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str = ""
):
    """Create a new issue."""
    return {
        "tool": "create_issue",
        "arguments": {
            "repo_name": f"{owner}/{repo}",
            "title": title,
            "body": body
        },
        "note": "Connect this to MCP server using proper MCP client library"
    }


# Generic tool call endpoint
@app.post("/api/tools/call")
async def call_tool(request: ToolCallRequest):
    """Call any MCP tool by name."""
    try:
        result = await call_mcp_tool(request.tool_name, request.arguments)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "mcp_server": MCP_SERVER_URL}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GitHub Manager REST API",
        "version": "0.1.0",
        "mcp_server": MCP_SERVER_URL,
        "docs": "/docs",
        "note": "This is a template. Implement MCP client for full functionality."
    }


if __name__ == "__main__":
    print("=" * 70)
    print("GitHub Manager REST API Wrapper")
    print("=" * 70)
    print()
    print("This is a TEMPLATE implementation.")
    print("For full functionality, implement proper MCP client connection.")
    print()
    print("See: docs/connecting-llms.md")
    print()
    print("API Documentation: http://localhost:9000/docs")
    print("=" * 70)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
