"""Backup tools for MCP server."""

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Any

from git import Repo
from github import Github, GithubException

from ..config import Config


def setup_backup_tools(mcp: Any, get_client: Callable[[], Github]) -> None:
    """Setup backup tools."""

    def get_backup_dir() -> Path:
        """Get backup directory from config."""
        config = Config.load()
        backup_dir = config.workspace.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    @mcp.tool()
    def backup_repository(
        repo_name: str,
        include_metadata: bool = True,
    ) -> str:
        """Backup a repository (clone + metadata).

        Args:
            repo_name: Repository name in format 'owner/repo'
            include_metadata: Backup issues, PRs, releases metadata

        Returns:
            Success message with backup path
        """
        client = get_client()
        backup_dir = get_backup_dir()

        try:
            repo = client.get_repo(repo_name)

            # Create backup directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            repo_backup_dir = backup_dir / repo.name / timestamp
            repo_backup_dir.mkdir(parents=True, exist_ok=True)

            # Clone repository
            clone_path = repo_backup_dir / "repository"
            Repo.clone_from(repo.clone_url, str(clone_path), mirror=True)

            result_parts = [
                f"Repository backup completed!",
                f"Repository: {repo.full_name}",
                f"Backup path: {repo_backup_dir}",
                f"",
                f"✅ Repository cloned (mirror)",
            ]

            # Backup metadata
            if include_metadata:
                metadata_dir = repo_backup_dir / "metadata"
                metadata_dir.mkdir(exist_ok=True)

                # Backup repository info
                repo_info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "ssh_url": repo.ssh_url,
                    "created_at": str(repo.created_at),
                    "updated_at": str(repo.updated_at),
                    "pushed_at": str(repo.pushed_at),
                    "size": repo.size,
                    "language": repo.language,
                    "default_branch": repo.default_branch,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "watchers": repo.watchers_count,
                    "open_issues": repo.open_issues_count,
                    "topics": repo.get_topics(),
                    "private": repo.private,
                    "archived": repo.archived,
                }

                with open(metadata_dir / "repository.json", "w") as f:
                    json.dump(repo_info, f, indent=2)

                result_parts.append("✅ Repository info backed up")

                # Backup issues
                issues_data = []
                for issue in repo.get_issues(state="all"):
                    if issue.pull_request:
                        continue

                    issues_data.append({
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body,
                        "state": issue.state,
                        "created_at": str(issue.created_at),
                        "updated_at": str(issue.updated_at),
                        "closed_at": str(issue.closed_at) if issue.closed_at else None,
                        "labels": [l.name for l in issue.labels],
                        "assignees": [a.login for a in issue.assignees],
                        "user": issue.user.login,
                        "comments": issue.comments,
                    })

                with open(metadata_dir / "issues.json", "w") as f:
                    json.dump(issues_data, f, indent=2)

                result_parts.append(f"✅ {len(issues_data)} issues backed up")

                # Backup pull requests
                prs_data = []
                for pr in repo.get_pulls(state="all"):
                    prs_data.append({
                        "number": pr.number,
                        "title": pr.title,
                        "body": pr.body,
                        "state": pr.state,
                        "created_at": str(pr.created_at),
                        "updated_at": str(pr.updated_at),
                        "closed_at": str(pr.closed_at) if pr.closed_at else None,
                        "merged_at": str(pr.merged_at) if pr.merged_at else None,
                        "head": pr.head.ref,
                        "base": pr.base.ref,
                        "user": pr.user.login,
                        "merged": pr.merged,
                        "mergeable": pr.mergeable,
                        "comments": pr.comments,
                        "commits": pr.commits,
                    })

                with open(metadata_dir / "pull_requests.json", "w") as f:
                    json.dump(prs_data, f, indent=2)

                result_parts.append(f"✅ {len(prs_data)} pull requests backed up")

                # Backup releases
                releases_data = []
                for release in repo.get_releases():
                    releases_data.append({
                        "tag_name": release.tag_name,
                        "name": release.title,
                        "body": release.body,
                        "draft": release.draft,
                        "prerelease": release.prerelease,
                        "created_at": str(release.created_at),
                        "published_at": str(release.published_at) if release.published_at else None,
                        "author": release.author.login if release.author else None,
                        "assets": [{
                            "name": a.name,
                            "size": a.size,
                            "download_count": a.download_count,
                            "url": a.browser_download_url,
                        } for a in release.get_assets()],
                    })

                with open(metadata_dir / "releases.json", "w") as f:
                    json.dump(releases_data, f, indent=2)

                result_parts.append(f"✅ {len(releases_data)} releases backed up")

            return "\n".join(result_parts)

        except (GithubException, Exception) as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def backup_all_repositories(
        username: str | None = None,
        include_metadata: bool = True,
    ) -> str:
        """Backup all repositories for a user.

        Args:
            username: GitHub username (defaults to authenticated user)
            include_metadata: Backup issues, PRs, releases metadata

        Returns:
            Summary of backup operations
        """
        client = get_client()
        backup_dir = get_backup_dir()

        try:
            if username:
                user = client.get_user(username)
            else:
                user = client.get_user()

            repos = user.get_repos()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_backup_dir = backup_dir / f"batch_{user.login}_{timestamp}"
            batch_backup_dir.mkdir(parents=True, exist_ok=True)

            results = []
            success_count = 0
            error_count = 0

            for repo in repos:
                try:
                    repo_dir = batch_backup_dir / repo.name
                    repo_dir.mkdir(exist_ok=True)

                    # Clone repository
                    clone_path = repo_dir / "repository"
                    Repo.clone_from(repo.clone_url, str(clone_path), mirror=True)

                    # Backup metadata if requested
                    if include_metadata:
                        metadata_dir = repo_dir / "metadata"
                        metadata_dir.mkdir(exist_ok=True)

                        # Just save basic info for batch backup
                        repo_info = {
                            "name": repo.name,
                            "full_name": repo.full_name,
                            "description": repo.description,
                            "url": repo.html_url,
                            "stars": repo.stargazers_count,
                            "backed_up_at": timestamp,
                        }

                        with open(metadata_dir / "repository.json", "w") as f:
                            json.dump(repo_info, f, indent=2)

                    results.append(f"✅ {repo.full_name}")
                    success_count += 1

                except Exception as e:
                    results.append(f"❌ {repo.full_name}: {str(e)}")
                    error_count += 1

            summary = f"""Batch backup completed!
User: {user.login}
Backup path: {batch_backup_dir}
Success: {success_count} | Errors: {error_count}

"""
            return summary + "\n".join(results)

        except GithubException as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def list_backups(repo_name: str | None = None) -> str:
        """List available backups.

        Args:
            repo_name: Optional repository name to filter

        Returns:
            List of backups with timestamps
        """
        backup_dir = get_backup_dir()

        if not backup_dir.exists():
            return f"No backups found in {backup_dir}"

        backups = []

        if repo_name:
            # List backups for specific repo
            repo_backup_dir = backup_dir / repo_name
            if repo_backup_dir.exists():
                for backup in sorted(repo_backup_dir.iterdir(), reverse=True):
                    if backup.is_dir():
                        size = sum(f.stat().st_size for f in backup.rglob("*") if f.is_file())
                        size_mb = size / (1024 * 1024)
                        backups.append(
                            f"📦 {backup.name}\n"
                            f"   Path: {backup}\n"
                            f"   Size: {size_mb:.2f} MB\n"
                        )
        else:
            # List all backups
            for item in sorted(backup_dir.iterdir()):
                if item.is_dir():
                    count = sum(1 for _ in item.iterdir())
                    backups.append(f"📁 {item.name} ({count} backups)")

        return "\n".join(backups) if backups else "No backups found"

    @mcp.tool()
    def restore_repository(
        backup_path: str,
        destination: str,
    ) -> str:
        """Restore a repository from backup.

        Args:
            backup_path: Path to backup directory
            destination: Destination path for restored repository

        Returns:
            Success message
        """
        try:
            backup_path_obj = Path(backup_path)
            dest_path = Path(destination)

            if not backup_path_obj.exists():
                return f"Error: Backup not found at {backup_path}"

            repo_path = backup_path_obj / "repository"
            if not repo_path.exists():
                return f"Error: Repository backup not found in {backup_path}"

            if dest_path.exists():
                return f"Error: Destination {dest_path} already exists"

            # Clone from the mirror backup
            Repo.clone_from(str(repo_path), str(dest_path), mirror=False)

            return f"""Repository restored successfully!
Backup: {backup_path}
Destination: {dest_path}

Note: Metadata (issues, PRs) are in {backup_path_obj / 'metadata'}
"""

        except Exception as e:
            return f"Error: {str(e)}"
