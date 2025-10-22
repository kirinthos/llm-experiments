#!/bin/bash

# Universal AI Chat - Server Startup Script
# Starts both MCP API server and Vue.js frontend

echo "🚀 Starting Universal AI Chat Servers..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask not found. Installing dependencies..."
    pip install -r agent-framework/requirements.txt
fi

# Kill any existing servers
echo "🧹 Cleaning up existing servers..."
pkill -f mcp_api_server.py 2>/dev/null || true
pkill -f vite 2>/dev/null || true

# Start MCP API Server in background
echo "🔧 Starting MCP API Server on port 4090..."
cd agent-framework
PYTHONPATH=.. python mcp_api_server.py &
MCP_PID=$!
cd ..

# Wait for MCP server to start
echo "⏳ Waiting for MCP server to initialize..."
sleep 5

# Check if MCP server is healthy
if curl -s http://localhost:4090/health | grep -q "healthy"; then
    echo "✅ MCP API Server started successfully"
else
    echo "❌ MCP API Server failed to start"
    kill $MCP_PID 2>/dev/null || true
    exit 1
fi

# Start Vue.js development server in background
echo "🎨 Starting Vue.js frontend on port 4091..."
cd chat-ui/chat-app
npm run dev &
VUE_PID=$!
cd ../..

# Wait for Vue.js server to start
echo "⏳ Waiting for Vue.js server to initialize..."
sleep 3

# Check if Vue.js server is running
if curl -s http://localhost:4091/ | grep -q "Universal AI Chat"; then
    echo "✅ Vue.js frontend started successfully"
else
    echo "❌ Vue.js frontend failed to start"
    kill $MCP_PID $VUE_PID 2>/dev/null || true
    exit 1
fi

# Run health tests
echo "🧪 Running health tests..."
cd chat-ui/chat-app
if node tests/server-health.test.js; then
    echo "✅ All health tests passed"
else
    echo "❌ Health tests failed"
    kill $MCP_PID $VUE_PID 2>/dev/null || true
    exit 1
fi
cd ../..

echo ""
echo "🎉 Universal AI Chat is ready!"
echo ""
echo "📱 Frontend: http://localhost:4091"
echo "🔧 MCP API:  http://localhost:4090"
echo "📊 Health:   http://localhost:4090/health"
echo ""
echo "💡 Features:"
echo "   • 10 AI models (5 OpenAI + 5 Gemini)"
echo "   • 21 MCP tools (calculator, web automation, etc.)"
echo "   • Real-time server status monitoring"
echo "   • Automated health testing"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $MCP_PID $VUE_PID 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running and show logs
echo "📋 Server logs (Ctrl+C to stop):"
echo "================================="

# Wait for user to stop
wait