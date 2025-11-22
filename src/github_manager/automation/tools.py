"""Automation tools for MCP server - issues, PRs, releases."""

from typing import Callable, Any
from github import Github, GithubException


def setup_automation_tools(mcp: Any, get_client: Callable[[], Github]) -> None:
    """Setup automation tools."""

    # ===== Issues =====
    @mcp.tool()
    def list_issues(
        repo_name: str,
        state: str = "open",
        labels: list[str] | None = None,
        limit: int = 20,
    ) -> str:
        """List issues in a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'
            state: Issue state: open, closed, or all
            labels: Filter by label names
            limit: Maximum number of issues

        Returns:
            Formatted list of issues
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            issues = repo.get_issues(state=state, labels=labels or [])

            result = []
            for i, issue in enumerate(issues):
                if i >= limit:
                    break
                if issue.pull_request:  # Skip PRs
                    continue

                labels_str = ", ".join(l.name for l in issue.labels) if issue.labels else "N/A"

                result.append(
                    f"#{issue.number}: {issue.title}\n"
                    f"   State: {issue.state} | Labels: {labels_str}\n"
                    f"   Created: {issue.created_at} by {issue.user.login}\n"
                    f"   Comments: {issue.comments}\n"
                    f"   URL: {issue.html_url}\n"
                )

            return "\n".join(result) if result else "No issues found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def create_issue(
        repo_name: str,
        title: str,
        body: str = "",
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> str:
        """Create a new issue.

        Args:
            repo_name: Repository name in format 'owner/repo'
            title: Issue title
            body: Issue body/description
            labels: Label names to apply
            assignees: Usernames to assign

        Returns:
            Success message with issue URL
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or [],
            )

            return f"""Issue created successfully!
#{issue.number}: {issue.title}
URL: {issue.html_url}
"""

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def close_issue(repo_name: str, issue_number: int, comment: str | None = None) -> str:
        """Close an issue.

        Args:
            repo_name: Repository name in format 'owner/repo'
            issue_number: Issue number
            comment: Optional closing comment

        Returns:
            Success message
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            issue = repo.get_issue(issue_number)

            if comment:
                issue.create_comment(comment)

            issue.edit(state="closed")

            return f"Issue #{issue_number} closed successfully."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    # ===== Pull Requests =====
    @mcp.tool()
    def list_pull_requests(
        repo_name: str,
        state: str = "open",
        limit: int = 20,
    ) -> str:
        """List pull requests in a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'
            state: PR state: open, closed, or all
            limit: Maximum number of PRs

        Returns:
            Formatted list of pull requests
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            pulls = repo.get_pulls(state=state)

            result = []
            for i, pr in enumerate(pulls):
                if i >= limit:
                    break

                status = "✅ Merged" if pr.merged else f"State: {pr.state}"

                result.append(
                    f"#{pr.number}: {pr.title}\n"
                    f"   {status} | {pr.head.ref} → {pr.base.ref}\n"
                    f"   Created: {pr.created_at} by {pr.user.login}\n"
                    f"   Comments: {pr.comments} | Commits: {pr.commits}\n"
                    f"   URL: {pr.html_url}\n"
                )

            return "\n".join(result) if result else "No pull requests found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def create_pull_request(
        repo_name: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = "",
        draft: bool = False,
    ) -> str:
        """Create a new pull request.

        Args:
            repo_name: Repository name in format 'owner/repo'
            title: PR title
            head: Head branch (source)
            base: Base branch (target, default: main)
            body: PR description
            draft: Create as draft PR

        Returns:
            Success message with PR URL
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            pr = repo.create_pull(
                title=title,
                head=head,
                base=base,
                body=body,
                draft=draft,
            )

            return f"""Pull request created successfully!
#{pr.number}: {pr.title}
{head} → {base}
URL: {pr.html_url}
"""

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def merge_pull_request(
        repo_name: str,
        pr_number: int,
        commit_message: str | None = None,
        merge_method: str = "merge",
    ) -> str:
        """Merge a pull request.

        Args:
            repo_name: Repository name in format 'owner/repo'
            pr_number: PR number
            commit_message: Optional commit message
            merge_method: Method: merge, squash, or rebase

        Returns:
            Success message
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            pr.merge(
                commit_message=commit_message,
                merge_method=merge_method,
            )

            return f"Pull request #{pr_number} merged successfully using {merge_method}."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    # ===== Releases =====
    @mcp.tool()
    def list_releases(repo_name: str, limit: int = 10) -> str:
        """List releases in a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'
            limit: Maximum number of releases

        Returns:
            Formatted list of releases
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            releases = repo.get_releases()

            result = []
            for i, release in enumerate(releases):
                if i >= limit:
                    break

                prerelease = " (pre-release)" if release.prerelease else ""
                draft = " [DRAFT]" if release.draft else ""

                result.append(
                    f"{release.tag_name}: {release.title or release.tag_name}{draft}{prerelease}\n"
                    f"   Published: {release.published_at or 'Not published'}\n"
                    f"   Author: {release.author.login if release.author else 'N/A'}\n"
                    f"   Downloads: {sum(a.download_count for a in release.get_assets())}\n"
                    f"   URL: {release.html_url}\n"
                )

            return "\n".join(result) if result else "No releases found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def create_release(
        repo_name: str,
        tag_name: str,
        name: str,
        body: str = "",
        target_commitish: str | None = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> str:
        """Create a new release.

        Args:
            repo_name: Repository name in format 'owner/repo'
            tag_name: Tag name (e.g., 'v1.0.0')
            name: Release title
            body: Release notes
            target_commitish: Target branch/commit (default: default branch)
            draft: Create as draft
            prerelease: Mark as pre-release

        Returns:
            Success message with release URL
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            release = repo.create_git_release(
                tag=tag_name,
                name=name,
                message=body,
                draft=draft,
                prerelease=prerelease,
                target_commitish=target_commitish or repo.default_branch,
            )

            return f"""Release created successfully!
{tag_name}: {name}
URL: {release.html_url}
"""

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    # ===== Labels =====
    @mcp.tool()
    def list_labels(repo_name: str) -> str:
        """List labels in a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'

        Returns:
            Formatted list of labels
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            labels = repo.get_labels()

            result = []
            for label in labels:
                result.append(f"- {label.name} (#{label.color}): {label.description or 'N/A'}")

            return "\n".join(result) if result else "No labels found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def create_label(
        repo_name: str,
        name: str,
        color: str,
        description: str = "",
    ) -> str:
        """Create a new label.

        Args:
            repo_name: Repository name in format 'owner/repo'
            name: Label name
            color: Color hex code (without #)
            description: Label description

        Returns:
            Success message
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            label = repo.create_label(
                name=name,
                color=color.lstrip('#'),
                description=description,
            )

            return f"Label '{label.name}' created successfully (#{label.color})."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    # ===== Workflows (Actions) =====
    @mcp.tool()
    def list_workflow_runs(
        repo_name: str,
        workflow_name: str | None = None,
        limit: int = 10,
    ) -> str:
        """List workflow runs (GitHub Actions).

        Args:
            repo_name: Repository name in format 'owner/repo'
            workflow_name: Optional workflow file name to filter
            limit: Maximum number of runs

        Returns:
            Formatted list of workflow runs
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)

            if workflow_name:
                workflow = repo.get_workflow(workflow_name)
                runs = workflow.get_runs()
            else:
                runs = repo.get_workflow_runs()

            result = []
            for i, run in enumerate(runs):
                if i >= limit:
                    break

                status_emoji = {
                    "success": "✅",
                    "failure": "❌",
                    "cancelled": "🚫",
                    "in_progress": "🔄",
                }.get(run.conclusion or run.status, "⚪")

                result.append(
                    f"{status_emoji} Run #{run.run_number}: {run.name}\n"
                    f"   Status: {run.conclusion or run.status}\n"
                    f"   Branch: {run.head_branch}\n"
                    f"   Created: {run.created_at}\n"
                    f"   URL: {run.html_url}\n"
                )

            return "\n".join(result) if result else "No workflow runs found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"
