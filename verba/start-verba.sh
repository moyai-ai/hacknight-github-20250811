#!/bin/bash
# Start the Verba RAG stack using Flox
# This script properly activates the Flox environment and starts all services

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

echo "📦 Activating Flox environment and starting services..."
echo ""
echo "This will start:"
echo "  • Ollama (LLM Server) on http://localhost:11434"
echo "  • Weaviate (Vector Database) on http://localhost:8080"  
echo "  • Verba (UI) on http://localhost:8000"
echo ""
echo "Note: First-time setup will install Python packages, which may take a few minutes."
echo ""

# Activate the environment and start services
# This command will:
# 1. Activate the Flox environment
# 2. Install/update Python packages if needed (on first run)
# 3. Start all services defined in manifest.toml
# 4. Keep the session active
echo "Starting services (this may take a moment)..."
exec flox activate --start-services