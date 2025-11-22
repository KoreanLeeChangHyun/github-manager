#!/usr/bin/env python3
"""List all available MCP tools with descriptions and parameters."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from github_manager.server import mcp

def list_tools():
    """List all registered MCP tools."""
    print("=" * 80)
    print("GitHub Manager MCP Server - Available Tools")
    print("=" * 80)
    print()

    # Get all tools from the MCP server
    tools = mcp._tool_manager._tools

    if not tools:
        print("No tools registered!")
        return

    # Group tools by category
    categories = {
        'Repository Management': [],
        'Issues': [],
        'Pull Requests': [],
        'Releases': [],
        'Labels': [],
        'Workflows': [],
        'Workspace': [],
        'Backup': [],
    }

    for tool_name, tool_func in tools.items():
        doc = tool_func.__doc__ or "No description"
        doc_lines = doc.strip().split('\n')
        description = doc_lines[0].strip()

        # Categorize
        if 'repository' in tool_name or 'repositories' in tool_name:
            if 'backup' in tool_name:
                categories['Backup'].append((tool_name, description))
            elif 'workspace' in tool_name or 'clone' in tool_name or 'pull' in tool_name or 'branch' in tool_name:
                categories['Workspace'].append((tool_name, description))
            else:
                categories['Repository Management'].append((tool_name, description))
        elif 'issue' in tool_name:
            categories['Issues'].append((tool_name, description))
        elif 'pull' in tool_name or 'pr' in tool_name:
            categories['Pull Requests'].append((tool_name, description))
        elif 'release' in tool_name:
            categories['Releases'].append((tool_name, description))
        elif 'label' in tool_name:
            categories['Labels'].append((tool_name, description))
        elif 'workflow' in tool_name:
            categories['Workflows'].append((tool_name, description))
        elif 'workspace' in tool_name or 'clone' in tool_name or 'branch' in tool_name or 'sync' in tool_name:
            categories['Workspace'].append((tool_name, description))
        elif 'backup' in tool_name or 'restore' in tool_name:
            categories['Backup'].append((tool_name, description))

    # Print categorized tools
    total = 0
    for category, tools_list in categories.items():
        if tools_list:
            print(f"\n{category}")
            print("-" * 80)
            for tool_name, description in sorted(tools_list):
                print(f"  • {tool_name}")
                print(f"    {description}")
                total += 1

    print()
    print("=" * 80)
    print(f"Total: {total} tools")
    print("=" * 80)
    print()

    # Resources
    print("Resources:")
    print("-" * 80)
    resources = mcp._resource_manager._resources
    for resource_uri, resource_func in resources.items():
        doc = resource_func.__doc__ or "No description"
        print(f"  • {resource_uri}")
        print(f"    {doc.strip().split(chr(10))[0]}")
    print()

if __name__ == "__main__":
    list_tools()
