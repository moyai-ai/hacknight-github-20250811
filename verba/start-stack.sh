#!/bin/bash
# Start the complete Verba RAG stack

set -e

echo "🚀 Starting Verba RAG Stack..."
echo ""

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    echo "Please install Flox first: https://flox.dev/docs/install"
    exit 1
fi

# Activate Flox environment
echo "📦 Activating Flox environment..."
eval "$(flox activate)"

# Pull Ollama models if not already present
echo ""
echo "📥 Pulling required Ollama models..."
ollama pull llama3
ollama pull mxbai-embed-large

# Start all services
echo ""
echo "🔧 Starting services..."
echo "  • Weaviate (Vector Database)"
echo "  • Ollama (LLM Server)"
echo "  • Verba (UI)"
echo ""

flox services start

echo ""
echo "✅ All services started!"
echo ""
echo "📌 Access points:"
echo "  • Verba UI: http://localhost:8000"
echo "  • Weaviate: http://localhost:8080"
echo "  • Ollama: http://localhost:11434"
echo ""
echo "Press Ctrl+C to stop all services"