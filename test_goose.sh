#!/bin/bash

echo "=== Goose Installation Test ==="
echo ""

# Test 1: Check if Goose is installed
echo "Test 1: Checking Goose installation..."
if command -v goose &> /dev/null; then
    echo "✅ Goose is installed"
    goose --version
else
    echo "❌ Goose not found in PATH"
    echo "Try adding to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
    exit 1
fi
echo ""

# Test 2: Check if configuration exists
echo "Test 2: Checking Goose configuration..."
if [ -f "$HOME/.config/goose/settings.json" ]; then
    echo "✅ Configuration file exists"
else
    echo "⚠️  No configuration found. Run: goose configure"
fi
echo ""

# Test 3: Check demo directory
echo "Test 3: Checking demo directory..."
if [ -d "goose-demo" ]; then
    echo "✅ Demo directory exists"
    ls -la goose-demo/
else
    echo "✅ Demo directory created at: $(pwd)/goose-demo"
fi
echo ""

echo "=== Next Steps ==="
echo "1. Configure Goose with your API key:"
echo "   goose configure"
echo ""
echo "2. Start a Goose session in the demo directory:"
echo "   cd goose-demo"
echo "   goose session"
echo ""
echo "3. Paste this prompt to create the demo:"
echo "   'create an interactive browser-based tic-tac-toe game in javascript where a player competes against a bot'"
echo ""
echo "For detailed instructions, see: README_GOOSE.md"