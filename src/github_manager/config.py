"""Configuration management for GitHub Manager MCP Server."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class GitHubConfig(BaseModel):
    """GitHub configuration settings."""

    token: str = Field(..., description="GitHub personal access token")
    username: str = Field(..., description="GitHub username")
    org: Optional[str] = Field(None, description="GitHub organization name")
    rate_limit_threshold: int = Field(
        default=100, description="API rate limit warning threshold"
    )

    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """Load configuration from environment variables."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

        username = os.getenv("GITHUB_USERNAME")
        if not username:
            raise ValueError("GITHUB_USERNAME environment variable is required")

        return cls(
            token=token,
            username=username,
            org=os.getenv("GITHUB_ORG"),
            rate_limit_threshold=int(os.getenv("RATE_LIMIT_THRESHOLD", "100")),
        )


class WorkspaceConfig(BaseModel):
    """Workspace configuration settings."""

    workspace_dir: Path = Field(..., description="Directory for cloned repositories")
    backup_dir: Path = Field(..., description="Directory for backups")

    @classmethod
    def from_env(cls) -> "WorkspaceConfig":
        """Load configuration from environment variables."""
        workspace_dir = os.getenv("WORKSPACE_DIR", str(Path.home() / "workspace"))
        backup_dir = os.getenv("BACKUP_DIR", str(Path.home() / "backups" / "github"))

        return cls(
            workspace_dir=Path(workspace_dir),
            backup_dir=Path(backup_dir),
        )


class Config(BaseModel):
    """Main configuration object."""

    github: GitHubConfig
    workspace: WorkspaceConfig

    @classmethod
    def load(cls) -> "Config":
        """Load all configuration from environment."""
        return cls(
            github=GitHubConfig.from_env(),
            workspace=WorkspaceConfig.from_env(),
        )
