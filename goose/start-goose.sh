#!/bin/bash
# Start Goose AI agent in a Flox environment
# This script ensures a consistent, portable environment for running Goose

set -e

echo "🦆 Starting Goose AI Agent..."
echo ""

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    echo "Please install Flox first: https://flox.dev/docs/install"
    exit 1
fi

# Navigate to script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check for API keys
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: No API keys detected"
    echo ""
    echo "Please set your API key first:"
    echo "  export ANTHROPIC_API_KEY='your-anthropic-key'"
    echo "  OR"
    echo "  export OPENAI_API_KEY='your-openai-key'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Activate Flox environment and start Goose
echo "📦 Activating Flox environment..."
echo ""

flox activate -- bash -c '
    # Check if Goose is configured
    if [ ! -f "$GOOSE_CONFIG_DIR/settings.json" ]; then
        echo "📝 First-time setup: Configuring Goose..."
        goose configure
        echo ""
    fi
    
    # Navigate to demo directory
    cd "$GOOSE_DEMO_DIR"
    
    echo "🚀 Starting Goose session in: $GOOSE_DEMO_DIR"
    echo ""
    echo "💡 Example prompt to try:"
    echo "   create an interactive browser-based tic-tac-toe game in javascript where a player competes against a bot"
    echo ""
    echo "Press Ctrl+C to exit the session"
    echo ""
    
    # Start Goose session
    goose session
'