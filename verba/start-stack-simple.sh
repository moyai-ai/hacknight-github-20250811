#!/bin/bash
# Simple start script that uses Flox services directly

set -e

echo "🚀 Starting Verba RAG Stack..."
echo ""

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    echo "Please install Flox first: https://flox.dev/docs/install"
    exit 1
fi

# Start all services using Flox
echo "📦 Starting all services with Flox..."
echo "  • Ollama (LLM Server)"
echo "  • Weaviate (Vector Database)"
echo "  • Verba (UI)"
echo ""

# Start services in the background
flox activate --start-services &
sleep 2

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if Ollama is ready
echo "Checking Ollama status..."
if flox activate -- curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is ready!"
    
    # Pull required models
    echo ""
    echo "📥 Pulling required Ollama models..."
    flox activate -- ollama pull llama3 || echo "Note: Model may already exist"
    flox activate -- ollama pull mxbai-embed-large || echo "Note: Model may already exist"
else
    echo "⚠️  Ollama may still be starting up. You can pull models manually later with:"
    echo "  flox activate -- ollama pull llama3"
    echo "  flox activate -- ollama pull mxbai-embed-large"
fi

echo ""
echo "✅ Services are starting!"
echo ""
echo "📌 Access points:"
echo "  • Verba UI: http://localhost:8000"
echo "  • Weaviate: http://localhost:8080"
echo "  • Ollama: http://localhost:11434"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to stop services cleanly
trap 'echo ""; echo "Stopping services..."; flox services stop; exit' INT

# Keep script running
while true; do
    sleep 10
done