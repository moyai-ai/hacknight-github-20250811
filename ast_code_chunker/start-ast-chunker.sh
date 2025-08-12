#!/usr/bin/env bash
# Simple startup script for AST Code Chunker

set -e

echo "🚀 Starting AST Code Chunker RAG Stack"
echo "======================================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed"
    echo "Please install Flox first: https://flox.dev/docs/install"
    exit 1
fi

# Check if environment exists
if [ ! -f ".flox/env/manifest.toml" ]; then
    echo "❌ Error: Flox environment not found"
    echo "Initializing Flox environment..."
    flox init
    cp manifest.toml .flox/env/manifest.toml
fi

echo "📦 Activating Flox environment and starting services..."
echo ""

# Run everything in the Flox environment
flox activate --start-services -- bash -c '
    echo "✅ Environment activated!"
    echo ""
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start (this may take up to 30 seconds)..."
    
    # Wait for Ollama
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            echo "✅ Ollama is ready"
            break
        fi
        sleep 1
    done
    
    # Wait for Weaviate
    for i in {1..30}; do
        if curl -s http://localhost:8080/v1/.well-known/ready >/dev/null 2>&1; then
            echo "✅ Weaviate is ready"
            break
        fi
        sleep 1
    done
    
    echo ""
    echo "📥 Pulling required models (this may take a few minutes)..."
    
    # Pull embedding model
    echo "  • Downloading embedding model: mxbai-embed-large"
    ollama pull mxbai-embed-large || echo "    ⚠️  Could not pull embedding model"
    
    # Pull chat model
    echo "  • Downloading chat model: llama3.2"
    ollama pull llama3.2 || echo "    ⚠️  Could not pull chat model"
    
    echo ""
    echo "📊 Initializing Weaviate schema..."
    python "$FLOX_ENV_PROJECT/cli.py" init-schema 2>/dev/null || echo "  ℹ️  Schema already exists"
    
    echo ""
    echo "=========================================="
    echo "✅ AST Code Chunker is ready!"
    echo "=========================================="
    echo ""
    echo "Services are running. Press Ctrl+C to stop."
    echo ""
    echo "In another terminal, navigate to this directory and run:"
    echo "  cd $(pwd)"
    echo "  flox activate"
    echo ""
    echo "Then use these commands:"
    echo "  • ast-chunk index-file example.py"
    echo "  • ast-chunk index-directory ./src -e .py -e .js"
    echo "  • ast-chunk search \"database connection\""
    echo "  • ast-chunk ask \"How does the authentication work?\""
    echo "  • ast-chunk stats"
    echo ""
    
    # Keep the services running
    while true; do
        sleep 60
    done
'