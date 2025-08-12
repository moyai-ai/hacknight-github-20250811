#!/bin/bash
# Test Goose installation using Flox environment
# This script is portable and will work on any system with Flox installed

set -e

echo "=== Goose Installation Test (Flox Edition) ==="
echo ""

# Check if Flox is installed
echo "Test 1: Checking Flox installation..."
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    echo "Please install Flox first: https://flox.dev/docs/install"
    exit 1
fi
echo "✅ Flox is installed"
flox --version
echo ""

# Navigate to script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate Flox environment and run tests
echo "Test 2: Activating Flox environment and checking Goose..."
flox activate -- bash -c '
    # Check if Goose is available in the Flox environment
    if command -v goose &> /dev/null; then
        echo "✅ Goose is installed in Flox environment"
        goose --version
    else
        echo "❌ Goose not found in Flox environment"
        echo "The Flox environment should have installed it automatically"
        exit 1
    fi
    echo ""
    
    # Check if configuration exists
    echo "Test 3: Checking Goose configuration..."
    if [ -f "$GOOSE_CONFIG_DIR/settings.json" ]; then
        echo "✅ Configuration file exists at: $GOOSE_CONFIG_DIR/settings.json"
        # Validate JSON structure
        if jq empty "$GOOSE_CONFIG_DIR/settings.json" 2>/dev/null; then
            echo "✅ Configuration file is valid JSON"
        else
            echo "⚠️  Configuration file exists but may have invalid JSON"
        fi
    else
        echo "⚠️  No configuration found. Run: flox activate && goose configure"
    fi
    echo ""
    
    # Check demo directory
    echo "Test 4: Checking demo directory..."
    if [ -d "$GOOSE_DEMO_DIR" ]; then
        echo "✅ Demo directory exists at: $GOOSE_DEMO_DIR"
        ls -la "$GOOSE_DEMO_DIR" 2>/dev/null || echo "   (empty directory)"
    else
        echo "❌ Demo directory not found"
    fi
    echo ""
    
    # Check API keys
    echo "Test 5: Checking API key configuration..."
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        echo "✅ ANTHROPIC_API_KEY is set (${#ANTHROPIC_API_KEY} characters)"
    else
        echo "⚠️  ANTHROPIC_API_KEY not set in environment"
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "✅ OPENAI_API_KEY is set (${#OPENAI_API_KEY} characters)"
    else
        echo "⚠️  OPENAI_API_KEY not set in environment"
    fi
    
    if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ No API keys found. You need to set at least one API key"
    fi
'

echo ""
echo "=== Next Steps ==="
echo "1. Activate the Flox environment:"
echo "   cd goose && flox activate"
echo ""
echo "2. Configure Goose with your API key (if not already done):"
echo "   goose configure"
echo ""
echo "3. Start a Goose session in the demo directory:"
echo "   cd \$GOOSE_DEMO_DIR"
echo "   goose session"
echo ""
echo "4. Try the demo prompt:"
echo "   'create an interactive browser-based tic-tac-toe game in javascript where a player competes against a bot'"
echo ""
echo "For more information, see: README_GOOSE.md"