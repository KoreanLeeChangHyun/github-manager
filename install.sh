#!/bin/bash
set -e

echo "Installing GitHub Manager MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file and add your GitHub token!"
    echo ""
fi

# Install dependencies
echo "Installing dependencies with uv..."
uv pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your GITHUB_TOKEN"
echo "2. Configure your MCP client with config/mcp-config.example.json"
echo "3. Run: uv run github-manager-mcp"
echo ""
