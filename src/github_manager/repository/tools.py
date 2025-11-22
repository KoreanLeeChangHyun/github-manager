"""Repository management tools for MCP server."""

from typing import Callable, Any
from github import Github, GithubException


def setup_repository_tools(mcp: Any, get_client: Callable[[], Github]) -> None:
    """Setup repository management tools."""

    @mcp.tool()
    def list_repositories(
        username: str | None = None,
        sort: str = "updated",
        direction: str = "desc",
        limit: int = 30,
    ) -> str:
        """List GitHub repositories for a user.

        Args:
            username: GitHub username (defaults to authenticated user)
            sort: Sort by: created, updated, pushed, full_name
            direction: Sort direction: asc or desc
            limit: Maximum number of repositories to return

        Returns:
            Formatted list of repositories
        """
        client = get_client()

        try:
            if username:
                user = client.get_user(username)
                repos = user.get_repos(sort=sort, direction=direction)
            else:
                repos = client.get_user().get_repos(sort=sort, direction=direction)

            result = []
            for i, repo in enumerate(repos):
                if i >= limit:
                    break

                result.append(
                    f"{i+1}. {repo.full_name}\n"
                    f"   Description: {repo.description or 'N/A'}\n"
                    f"   Stars: ⭐ {repo.stargazers_count} | "
                    f"Forks: 🍴 {repo.forks_count} | "
                    f"Language: {repo.language or 'N/A'}\n"
                    f"   Updated: {repo.updated_at}\n"
                    f"   URL: {repo.html_url}\n"
                )

            return "\n".join(result) if result else "No repositories found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def get_repository_info(repo_name: str) -> str:
        """Get detailed information about a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'

        Returns:
            Detailed repository information
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)

            return f"""Repository: {repo.full_name}
Description: {repo.description or 'N/A'}
URL: {repo.html_url}
Clone URL: {repo.clone_url}
SSH URL: {repo.ssh_url}

Stats:
- Stars: ⭐ {repo.stargazers_count}
- Forks: 🍴 {repo.forks_count}
- Watchers: 👀 {repo.watchers_count}
- Open Issues: {repo.open_issues_count}
- Size: {repo.size} KB

Details:
- Language: {repo.language or 'N/A'}
- Default Branch: {repo.default_branch}
- Created: {repo.created_at}
- Updated: {repo.updated_at}
- Pushed: {repo.pushed_at}
- Private: {repo.private}
- Fork: {repo.fork}
- Archived: {repo.archived}
- License: {repo.license.name if repo.license else 'N/A'}

Topics: {', '.join(repo.get_topics()) if repo.get_topics() else 'N/A'}
"""

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def create_repository(
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True,
        gitignore_template: str | None = None,
        license_template: str | None = None,
    ) -> str:
        """Create a new GitHub repository.

        Args:
            name: Repository name
            description: Repository description
            private: Create as private repository
            auto_init: Initialize with README
            gitignore_template: .gitignore template (e.g., 'Python')
            license_template: License template (e.g., 'mit')

        Returns:
            Success message with repository URL
        """
        client = get_client()

        try:
            user = client.get_user()
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                license_template=license_template,
            )

            return f"""Repository created successfully!
Name: {repo.full_name}
URL: {repo.html_url}
Clone URL: {repo.clone_url}
SSH URL: {repo.ssh_url}
"""

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def update_repository(
        repo_name: str,
        description: str | None = None,
        homepage: str | None = None,
        private: bool | None = None,
        has_issues: bool | None = None,
        has_wiki: bool | None = None,
        has_projects: bool | None = None,
        default_branch: str | None = None,
    ) -> str:
        """Update repository settings.

        Args:
            repo_name: Repository name in format 'owner/repo'
            description: New description
            homepage: Homepage URL
            private: Make private/public
            has_issues: Enable/disable issues
            has_wiki: Enable/disable wiki
            has_projects: Enable/disable projects
            default_branch: Change default branch

        Returns:
            Success message
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)

            if description is not None:
                repo.edit(description=description)
            if homepage is not None:
                repo.edit(homepage=homepage)
            if private is not None:
                repo.edit(private=private)
            if has_issues is not None:
                repo.edit(has_issues=has_issues)
            if has_wiki is not None:
                repo.edit(has_wiki=has_wiki)
            if has_projects is not None:
                repo.edit(has_projects=has_projects)
            if default_branch is not None:
                repo.edit(default_branch=default_branch)

            return f"Repository {repo_name} updated successfully!"

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def delete_repository(repo_name: str, confirm: bool = False) -> str:
        """Delete a repository (use with caution!).

        Args:
            repo_name: Repository name in format 'owner/repo'
            confirm: Must be True to actually delete

        Returns:
            Success or confirmation message
        """
        if not confirm:
            return f"⚠️  WARNING: This will permanently delete {repo_name}!\nSet confirm=True to proceed."

        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            repo.delete()

            return f"Repository {repo_name} has been deleted."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def search_repositories(
        query: str,
        sort: str = "stars",
        order: str = "desc",
        limit: int = 10,
    ) -> str:
        """Search for repositories on GitHub.

        Args:
            query: Search query (supports GitHub search syntax)
            sort: Sort by: stars, forks, help-wanted-issues, updated
            order: Sort order: desc or asc
            limit: Maximum number of results

        Returns:
            Formatted list of matching repositories
        """
        client = get_client()

        try:
            repos = client.search_repositories(query=query, sort=sort, order=order)

            result = []
            for i, repo in enumerate(repos):
                if i >= limit:
                    break

                result.append(
                    f"{i+1}. {repo.full_name}\n"
                    f"   Description: {repo.description or 'N/A'}\n"
                    f"   Stars: ⭐ {repo.stargazers_count} | "
                    f"Forks: 🍴 {repo.forks_count} | "
                    f"Language: {repo.language or 'N/A'}\n"
                    f"   URL: {repo.html_url}\n"
                )

            return "\n".join(result) if result else "No repositories found."

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def get_repository_topics(repo_name: str) -> str:
        """Get topics (tags) for a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'

        Returns:
            List of topics
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            topics = repo.get_topics()

            if topics:
                return f"Topics for {repo_name}:\n" + "\n".join(f"- {t}" for t in topics)
            else:
                return f"No topics set for {repo_name}"

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"

    @mcp.tool()
    def set_repository_topics(repo_name: str, topics: list[str]) -> str:
        """Set topics (tags) for a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'
            topics: List of topic names

        Returns:
            Success message
        """
        client = get_client()

        try:
            repo = client.get_repo(repo_name)
            repo.replace_topics(topics)

            return f"Topics updated for {repo_name}:\n" + "\n".join(f"- {t}" for t in topics)

        except GithubException as e:
            return f"Error: {e.data.get('message', str(e))}"
