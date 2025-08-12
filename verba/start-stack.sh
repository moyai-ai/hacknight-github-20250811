#!/bin/bash
# Start the complete Verba RAG stack - all in one terminal
# This script starts services and pulls models automatically

set -e

echo "🚀 Starting Verba RAG Stack..."
echo ""

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    echo "Please install Flox first:"
    echo "  brew install flox"
    echo "  or"
    echo "  curl -fsSL https://downloads.flox.dev/by-env/stable/install.sh | sh"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "manifest.toml" ]; then
    echo "❌ Error: manifest.toml not found."
    echo "Please run this script from the verba directory."
    exit 1
fi

echo "📦 Starting all services..."
echo "  • Ollama (LLM Server)"
echo "  • Weaviate (Vector Database)"
echo "  • Verba (UI)"
echo ""
echo "Note: First-time setup will install Python packages (2-3 minutes)"
echo "      Model downloads will happen after services start (5-10 minutes)"
echo ""

# Function to check and pull models
check_and_pull_models() {
    # Wait for Ollama to be ready
    echo "⏳ Waiting for Ollama to initialize..."
    local counter=0
    local max_tries=20
    
    while ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
        if [ $counter -ge $max_tries ]; then
            echo "⚠️  Ollama is taking longer than expected."
            echo "    You can manually pull models later with:"
            echo "    flox activate -- ollama pull llama3"
            echo "    flox activate -- ollama pull mxbai-embed-large"
            return
        fi
        echo "  Waiting for Ollama... ($((counter+1))/$max_tries)"
        sleep 3
        counter=$((counter+1))
    done
    
    echo "✅ Ollama is ready!"
    echo ""
    echo "📥 Checking and pulling required models..."
    
    # Check if llama3 exists
    if ollama list 2>/dev/null | grep -q "llama3"; then
        echo "  ✓ llama3 model already exists"
    else
        echo "  ⬇ Pulling llama3 model (this may take a few minutes)..."
        ollama pull llama3 || echo "  ⚠️ Failed to pull llama3 - you can retry manually later"
    fi
    
    # Check if mxbai-embed-large exists
    if ollama list 2>/dev/null | grep -q "mxbai-embed-large"; then
        echo "  ✓ mxbai-embed-large model already exists"
    else
        echo "  ⬇ Pulling mxbai-embed-large model..."
        ollama pull mxbai-embed-large || echo "  ⚠️ Failed to pull mxbai-embed-large - you can retry manually later"
    fi
    
    echo ""
    echo "✅ Model setup complete!"
}

# Export the function so it can be used in the subshell
export -f check_and_pull_models

# Start services and run model pulling in the activated environment
exec flox activate --start-services --command "
    # Run model pulling in background after a delay
    (sleep 10 && check_and_pull_models) &
    
    echo ''
    echo '════════════════════════════════════════════════════════'
    echo '✅ Verba RAG Stack is starting!'
    echo '════════════════════════════════════════════════════════'
    echo ''
    echo '📌 Access points (wait ~30 seconds for services to start):'
    echo '  • Verba UI:  http://localhost:8000'
    echo '  • Weaviate:  http://localhost:8080'
    echo '  • Ollama:    http://localhost:11434'
    echo ''
    echo '📝 Quick tips:'
    echo '  • Models will download automatically in the background'
    echo '  • Upload documents in Verba UI to build your knowledge base'
    echo '  • Use the chat interface to query your documents'
    echo ''
    echo 'Press Ctrl+C to stop all services'
    echo '────────────────────────────────────────────────────────'
    echo ''
    
    # Keep the session alive
    exec bash
"