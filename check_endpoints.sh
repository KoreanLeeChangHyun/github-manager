#!/bin/bash
# Check available endpoints when running in SSE mode

echo "Starting MCP server in SSE mode..."
echo ""

# Start server in background
MCP_TRANSPORT=sse MCP_PORT=8001 uv run github-manager-mcp &
SERVER_PID=$!

# Wait for server to start
sleep 3

echo "Server running on PID: $SERVER_PID"
echo ""
echo "Available endpoints:"
echo "===================="
echo ""
echo "1. SSE endpoint (MCP protocol):"
echo "   http://localhost:8001/sse"
echo ""
echo "2. Health check (if available):"
curl -s http://localhost:8001/health 2>/dev/null && echo "" || echo "   Not available"
echo ""
echo "3. Root endpoint:"
curl -s http://localhost:8001/ 2>/dev/null | head -20
echo ""
echo "4. Docs endpoint:"
curl -s http://localhost:8001/docs 2>/dev/null | head -20 || echo "   Standard /docs not available"
echo ""
echo "5. OpenAPI schema:"
curl -s http://localhost:8001/openapi.json 2>/dev/null | head -20 || echo "   Standard /openapi.json not available"
echo ""

# Kill server
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo "Server stopped."
