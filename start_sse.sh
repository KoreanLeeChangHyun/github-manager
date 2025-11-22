#!/bin/bash
# Start GitHub Manager MCP Server in SSE mode

set -e

echo "🚀 Starting GitHub Manager MCP Server (SSE mode)..."
echo ""

# Default values
PORT=${MCP_PORT:-8000}
HOST=${MCP_HOST:-0.0.0.0}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--port PORT] [--host HOST]"
            exit 1
            ;;
    esac
done

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create .env file with your GITHUB_TOKEN"
    echo ""
fi

# Set environment and run
export PATH="$HOME/.local/bin:$PATH"
export MCP_TRANSPORT=sse
export MCP_PORT=$PORT
export MCP_HOST=$HOST

echo "Configuration:"
echo "  - Transport: SSE"
echo "  - Host: $HOST"
echo "  - Port: $PORT"
echo "  - URL: http://$HOST:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uv run github-manager-mcp
