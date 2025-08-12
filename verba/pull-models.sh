#!/bin/bash
# Pull required Ollama models for Verba
# Run this after starting services with ./start-verba.sh

echo "📥 Pulling required Ollama models..."
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Error: Ollama is not running."
    echo "Please start services first with: ./start-verba.sh"
    exit 1
fi

echo "Pulling llama3 model (this may take a while)..."
flox activate -- ollama pull llama3

echo ""
echo "Pulling mxbai-embed-large model for embeddings..."
flox activate -- ollama pull mxbai-embed-large

echo ""
echo "✅ Models pulled successfully!"
echo ""
echo "You can now access Verba at: http://localhost:8000"