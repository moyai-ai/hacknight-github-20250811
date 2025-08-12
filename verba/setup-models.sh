#!/bin/bash
# Setup and pull required Ollama models for Verba
# This script handles both Ollama service startup and model pulling

set -e

echo "🔧 Setting up Ollama models for Verba..."
echo ""

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    echo "Please install Flox first:"
    echo "  brew install flox"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "manifest.toml" ]; then
    echo "❌ Error: manifest.toml not found."
    echo "Please run this script from the verba directory."
    exit 1
fi

# Function to check if Ollama is responding
check_ollama() {
    curl -s http://localhost:11434/api/tags > /dev/null 2>&1
}

# Check if Ollama is already running
if check_ollama; then
    echo "✅ Ollama is already running"
else
    echo "📦 Starting Ollama service..."
    # Start Ollama service in the background using Flox
    flox activate -- bash -c "ollama serve" &
    OLLAMA_PID=$!
    
    # Wait for Ollama to be ready (max 30 seconds)
    echo "Waiting for Ollama to start..."
    for i in {1..30}; do
        if check_ollama; then
            echo "✅ Ollama service started successfully"
            break
        fi
        sleep 1
    done
    
    if ! check_ollama; then
        echo "❌ Error: Failed to start Ollama service"
        exit 1
    fi
fi

echo ""
echo "📥 Pulling required models..."
echo ""

# Pull models using the Flox environment's ollama
echo "Pulling llama3 model (this may take a while)..."
if flox activate -- bash -c "ollama pull llama3"; then
    echo "✅ llama3 model pulled successfully"
else
    echo "⚠️  Warning: Failed to pull llama3 model"
fi

echo ""
echo "Pulling mxbai-embed-large model for embeddings..."
if flox activate -- bash -c "ollama pull mxbai-embed-large"; then
    echo "✅ mxbai-embed-large model pulled successfully"
else
    echo "⚠️  Warning: Failed to pull mxbai-embed-large model"
fi

echo ""
echo "🎉 Model setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start all services: ./start-verba.sh"
echo "  2. Access Verba at: http://localhost:8000"
echo ""

# If we started Ollama for this script, offer to keep it running
if [ ! -z "$OLLAMA_PID" ]; then
    echo "Note: Ollama is still running in the background."
    echo "You can stop it with: pkill ollama"
fi