# GitHub Workflow Expert

You are an expert at GitHub automation, workflows, and best practices for repository management.

## When to Use This Skill

Use this skill when:
- Creating or optimizing GitHub Actions workflows
- Setting up issue/PR templates
- Automating release processes
- Managing labels, milestones, and project boards
- Implementing GitHub automation with the GitHub Manager MCP tools

## GitHub Actions Best Practices

### Workflow Structure

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"

      - name: Run tests
        run: uv run pytest --cov=src/github_manager

      - name: Type check
        run: uv run mypy src/

      - name: Lint
        run: |
          uv run black --check src/
          uv run ruff check src/
```

### Common Workflows for This Project

#### 1. Test and Quality Check
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install uv
      - run: uv pip install -e ".[dev]"
      - run: uv run pytest
      - run: uv run mypy src/
      - run: uv run black --check src/
      - run: uv run ruff check src/
```

#### 2. Auto-Release on Tag
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

#### 3. MCP Server Health Check
```yaml
name: MCP Server Health

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install uv
      - run: uv pip install -e .
      - name: Test MCP server startup
        run: timeout 10s uv run github-manager-mcp || true
        env:
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
          GITHUB_USERNAME: ${{ secrets.GH_USERNAME }}
```

## Issue and PR Templates

### Issue Template: Bug Report
`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Report a bug in GitHub Manager MCP
title: '[BUG] '
labels: bug
assignees: ''
---

## 버그 설명
명확하고 간결한 버그 설명

## 재현 방법
1. MCP 서버 실행: `uv run github-manager-mcp`
2. 도구 호출: `tool_name(param)`
3. 에러 발생

## 예상 동작
정상적으로 작동해야 하는 방식

## 실제 동작
실제로 발생한 동작

## 환경
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.10.12]
- PyGithub: [e.g. 2.1.1]
- FastMCP: [e.g. 0.1.0]

## 추가 정보
스크린샷, 로그 등
```

### PR Template
`.github/pull_request_template.md`:

```markdown
## 변경 사항
이 PR의 변경 사항을 간략히 설명

## 변경 타입
- [ ] feat: 새로운 기능
- [ ] fix: 버그 수정
- [ ] docs: 문서 변경
- [ ] refactor: 리팩토링
- [ ] test: 테스트 추가/수정
- [ ] chore: 기타 변경

## 체크리스트
- [ ] 테스트 통과 (`uv run pytest`)
- [ ] 타입 체크 통과 (`uv run mypy src/`)
- [ ] 코드 포맷팅 완료 (`uv run black src/`)
- [ ] Lint 통과 (`uv run ruff check src/`)
- [ ] 문서 업데이트 (필요시)
- [ ] CHANGELOG.md 업데이트 (필요시)

## 관련 이슈
Closes #(이슈 번호)

## 테스트 방법
1. 변경 사항 테스트 방법
2. 예상 결과
```

## Label Management Strategy

### Recommended Labels

**Type Labels:**
- `bug` - 버그 수정
- `feature` - 새로운 기능
- `enhancement` - 기능 개선
- `docs` - 문서 관련
- `refactor` - 리팩토링
- `test` - 테스트 관련

**Priority Labels:**
- `priority: high` - 높은 우선순위
- `priority: medium` - 중간 우선순위
- `priority: low` - 낮은 우선순위

**Status Labels:**
- `status: in-progress` - 작업 중
- `status: blocked` - 차단됨
- `status: needs-review` - 리뷰 필요

**Module Labels:**
- `module: repository` - repository 도구
- `module: automation` - automation 도구
- `module: workspace` - workspace 도구
- `module: backup` - backup 도구

### Using MCP Tools for Label Management

```python
# Create standard labels
labels = [
    ("bug", "d73a4a", "Something isn't working"),
    ("feature", "0075ca", "New feature or request"),
    ("docs", "0075ca", "Documentation improvements"),
]

for name, color, description in labels:
    create_label(repo_name="owner/repo", name=name, color=color, description=description)
```

## Release Automation

### Semantic Versioning

Follow semver: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Workflow

1. **Update Version**
   ```bash
   # Update pyproject.toml
   version = "1.2.0"
   ```

2. **Create Changelog**
   ```markdown
   ## [1.2.0] - 2025-11-23

   ### Added
   - New MCP tool: archive_repository
   - GitHub workflow automation skill

   ### Fixed
   - Error handling in backup tools

   ### Changed
   - Improved documentation structure
   ```

3. **Tag and Release**
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

4. **Use MCP Tool**
   ```python
   create_release(
       repo_name="owner/repo",
       tag_name="v1.2.0",
       name="Release 1.2.0",
       body=changelog_content,
       draft=False,
       prerelease=False
   )
   ```

## Automation Recipes

### Auto-Label PRs Based on Files Changed

```yaml
name: Auto Label

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
```

`.github/labeler.yml`:
```yaml
'module: repository':
  - src/github_manager/repository/**/*

'module: automation':
  - src/github_manager/automation/**/*

'docs':
  - '**/*.md'
  - .claude/docs/**/*

'test':
  - tests/**/*
```

### Auto-Close Stale Issues

```yaml
name: Close Stale Issues

on:
  schedule:
    - cron: '0 0 * * *'

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          stale-issue-message: '이 이슈는 30일간 활동이 없어 곧 닫힐 예정입니다.'
          close-issue-message: '이 이슈는 비활성으로 인해 자동으로 닫혔습니다.'
          days-before-stale: 30
          days-before-close: 7
          stale-issue-label: 'stale'
```

## Repository Settings Best Practices

### Branch Protection Rules

```yaml
# Using MCP tools to set branch protection
# Recommended settings for 'main' branch:
- Require pull request reviews (1 approval)
- Require status checks to pass (CI tests)
- Require branches to be up to date
- Do not allow force pushes
- Do not allow deletions
```

### Required Status Checks

For main branch, require:
1. `test` - All tests pass
2. `type-check` - Mypy passes
3. `lint` - Black and Ruff pass
4. `coverage` - Minimum 80% coverage

## Using GitHub Manager MCP Tools for Automation

### Create Issue from Template

```python
# Using automation tools
issue = create_issue(
    repo_name="owner/repo",
    title="[BUG] Server startup failure",
    body=bug_template,
    labels=["bug", "priority: high", "module: server"]
)
```

### Batch Update Labels

```python
# Add label to multiple issues
for issue_number in [1, 2, 3, 4, 5]:
    add_labels_to_issue(
        repo_name="owner/repo",
        issue_number=issue_number,
        labels=["needs-triage"]
    )
```

### Automated Release Notes

```python
# Get all merged PRs since last release
prs = list_pull_requests(
    repo_name="owner/repo",
    state="closed",
    base="main"
)

# Generate release notes
release_notes = generate_release_notes(prs)

# Create release
create_release(
    repo_name="owner/repo",
    tag_name="v1.2.0",
    name="Release 1.2.0",
    body=release_notes
)
```

## Workflow Optimization Tips

1. **Cache Dependencies**
   ```yaml
   - uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
   ```

2. **Parallel Jobs**
   ```yaml
   jobs:
     test:
       strategy:
         matrix:
           python-version: ['3.10', '3.11', '3.12']
   ```

3. **Conditional Execution**
   ```yaml
   - name: Deploy
     if: github.ref == 'refs/heads/main'
     run: ./deploy.sh
   ```

4. **Reusable Workflows**
   Create `.github/workflows/reusable-test.yml` and call from other workflows

## Common GitHub Automation Patterns

### Issue Triage Bot

Monitor new issues and auto-assign labels based on content:
- Keywords "bug", "error" → label: bug
- Keywords "feature", "enhancement" → label: feature
- Keywords "docs", "documentation" → label: docs

### PR Size Labeling

- < 10 files changed → `size: S`
- 10-30 files → `size: M`
- > 30 files → `size: L`

### Auto-Merge Dependabot PRs

```yaml
- name: Auto-merge Dependabot PRs
  if: github.actor == 'dependabot[bot]'
  run: gh pr merge --auto --squash "$PR_URL"
```

## Resources

- GitHub Actions docs: https://docs.github.com/actions
- GitHub Manager automation tools: src/github_manager/automation/tools.py
- Workflow examples: .github/workflows/
