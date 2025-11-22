"""Workspace management tools for MCP server."""

import os
import shutil
from pathlib import Path
from typing import Callable, Any

from git import Repo, GitCommandError
from github import Github, GithubException

from ..config import Config


def setup_workspace_tools(mcp: Any, get_client: Callable[[], Github]) -> None:
    """Setup workspace management tools."""

    def get_workspace_dir() -> Path:
        """Get workspace directory from config."""
        config = Config.load()
        workspace_dir = config.workspace.workspace_dir
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir

    @mcp.tool()
    def list_workspace_repos() -> str:
        """List all repositories in the workspace.

        Returns:
            List of repositories with their status
        """
        workspace_dir = get_workspace_dir()

        repos = []
        for item in workspace_dir.iterdir():
            if item.is_dir() and (item / ".git").exists():
                try:
                    repo = Repo(str(item))
                    branch = repo.active_branch.name
                    is_dirty = repo.is_dirty()
                    status = "🔴 Modified" if is_dirty else "✅ Clean"

                    remotes = [r.name for r in repo.remotes]
                    remote_str = f"Remotes: {', '.join(remotes)}" if remotes else "No remotes"

                    repos.append(
                        f"📁 {item.name}\n"
                        f"   Branch: {branch} | {status}\n"
                        f"   Path: {item}\n"
                        f"   {remote_str}\n"
                    )
                except Exception as e:
                    repos.append(f"📁 {item.name}\n   Error: {str(e)}\n")

        if repos:
            return f"Workspace: {workspace_dir}\n\n" + "\n".join(repos)
        else:
            return f"No repositories found in workspace: {workspace_dir}"

    @mcp.tool()
    def clone_repository(
        repo_name: str,
        use_ssh: bool = True,
        destination: str | None = None,
    ) -> str:
        """Clone a repository to the workspace.

        Args:
            repo_name: Repository name in format 'owner/repo'
            use_ssh: Use SSH URL (default) or HTTPS
            destination: Optional custom destination path

        Returns:
            Success message with path
        """
        client = get_client()
        workspace_dir = get_workspace_dir()

        try:
            repo = client.get_repo(repo_name)

            if destination:
                dest_path = Path(destination)
            else:
                dest_path = workspace_dir / repo.name

            if dest_path.exists():
                return f"Error: Directory {dest_path} already exists"

            clone_url = repo.ssh_url if use_ssh else repo.clone_url

            Repo.clone_from(clone_url, str(dest_path))

            return f"""Repository cloned successfully!
Repository: {repo.full_name}
Path: {dest_path}
URL: {clone_url}
"""

        except (GithubException, GitCommandError) as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def pull_repository(repo_path: str) -> str:
        """Pull latest changes from remote.

        Args:
            repo_path: Path to repository (relative to workspace or absolute)

        Returns:
            Pull result
        """
        workspace_dir = get_workspace_dir()

        try:
            # Try as relative path first
            path = Path(repo_path)
            if not path.is_absolute():
                path = workspace_dir / repo_path

            if not path.exists():
                return f"Error: Repository not found at {path}"

            repo = Repo(str(path))

            if not repo.remotes:
                return f"Error: No remotes configured for {path}"

            origin = repo.remotes.origin
            pull_info = origin.pull()

            result = []
            for info in pull_info:
                result.append(f"- {info.ref}: {info.flags}")

            return f"""Pulled latest changes for {path.name}:
Branch: {repo.active_branch.name}
""" + "\n".join(result)

        except GitCommandError as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_repository_status(repo_path: str) -> str:
        """Get git status for a repository.

        Args:
            repo_path: Path to repository (relative to workspace or absolute)

        Returns:
            Git status information
        """
        workspace_dir = get_workspace_dir()

        try:
            path = Path(repo_path)
            if not path.is_absolute():
                path = workspace_dir / repo_path

            if not path.exists():
                return f"Error: Repository not found at {path}"

            repo = Repo(str(path))

            # Get branch info
            branch = repo.active_branch.name
            is_dirty = repo.is_dirty()

            # Get changed files
            changed = [item.a_path for item in repo.index.diff(None)]
            staged = [item.a_path for item in repo.index.diff("HEAD")]
            untracked = repo.untracked_files

            status_parts = [
                f"Repository: {path.name}",
                f"Branch: {branch}",
                f"Status: {'🔴 Modified' if is_dirty else '✅ Clean'}",
                "",
            ]

            if staged:
                status_parts.append("Staged files:")
                status_parts.extend(f"  + {f}" for f in staged)
                status_parts.append("")

            if changed:
                status_parts.append("Modified files:")
                status_parts.extend(f"  M {f}" for f in changed)
                status_parts.append("")

            if untracked:
                status_parts.append("Untracked files:")
                status_parts.extend(f"  ? {f}" for f in untracked)

            return "\n".join(status_parts)

        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def sync_all_repositories() -> str:
        """Pull latest changes for all repositories in workspace.

        Returns:
            Summary of sync operations
        """
        workspace_dir = get_workspace_dir()

        results = []
        success_count = 0
        error_count = 0

        for item in workspace_dir.iterdir():
            if item.is_dir() and (item / ".git").exists():
                try:
                    repo = Repo(str(item))

                    if not repo.remotes:
                        results.append(f"⚠️  {item.name}: No remotes")
                        continue

                    if repo.is_dirty():
                        results.append(f"⚠️  {item.name}: Has uncommitted changes, skipping")
                        continue

                    origin = repo.remotes.origin
                    origin.pull()

                    results.append(f"✅ {item.name}: Updated")
                    success_count += 1

                except Exception as e:
                    results.append(f"❌ {item.name}: {str(e)}")
                    error_count += 1

        summary = f"Synced {success_count} repositories ({error_count} errors)\n\n"
        return summary + "\n".join(results)

    @mcp.tool()
    def delete_workspace_repo(repo_name: str, confirm: bool = False) -> str:
        """Delete a repository from workspace.

        Args:
            repo_name: Repository directory name
            confirm: Must be True to actually delete

        Returns:
            Success or confirmation message
        """
        if not confirm:
            return f"⚠️  WARNING: This will permanently delete {repo_name} from workspace!\nSet confirm=True to proceed."

        workspace_dir = get_workspace_dir()
        repo_path = workspace_dir / repo_name

        if not repo_path.exists():
            return f"Error: Repository {repo_name} not found in workspace"

        if not (repo_path / ".git").exists():
            return f"Error: {repo_name} is not a git repository"

        try:
            shutil.rmtree(repo_path)
            return f"Repository {repo_name} deleted from workspace"

        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def create_branch(repo_path: str, branch_name: str, checkout: bool = True) -> str:
        """Create a new branch in a repository.

        Args:
            repo_path: Path to repository (relative to workspace or absolute)
            branch_name: Name for the new branch
            checkout: Checkout the new branch after creation

        Returns:
            Success message
        """
        workspace_dir = get_workspace_dir()

        try:
            path = Path(repo_path)
            if not path.is_absolute():
                path = workspace_dir / repo_path

            if not path.exists():
                return f"Error: Repository not found at {path}"

            repo = Repo(str(path))
            new_branch = repo.create_head(branch_name)

            if checkout:
                new_branch.checkout()
                return f"Created and checked out branch '{branch_name}' in {path.name}"
            else:
                return f"Created branch '{branch_name}' in {path.name}"

        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def switch_branch(repo_path: str, branch_name: str) -> str:
        """Switch to a different branch.

        Args:
            repo_path: Path to repository (relative to workspace or absolute)
            branch_name: Branch name to switch to

        Returns:
            Success message
        """
        workspace_dir = get_workspace_dir()

        try:
            path = Path(repo_path)
            if not path.is_absolute():
                path = workspace_dir / repo_path

            if not path.exists():
                return f"Error: Repository not found at {path}"

            repo = Repo(str(path))

            if repo.is_dirty():
                return f"Error: Repository has uncommitted changes. Commit or stash them first."

            repo.git.checkout(branch_name)

            return f"Switched to branch '{branch_name}' in {path.name}"

        except Exception as e:
            return f"Error: {str(e)}"
