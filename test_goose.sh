#!/bin/bash

# This script now uses the Flox-based setup for better portability
# The new implementation ensures Goose runs consistently on any device

echo "=== Goose Installation Test ==="
echo ""
echo "ℹ️  This script now uses Flox for portable environment management"
echo "   Redirecting to the new Flox-based test script..."
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if the new Flox-based script exists
if [ -f "$SCRIPT_DIR/goose/test_goose.sh" ]; then
    exec "$SCRIPT_DIR/goose/test_goose.sh"
else
    echo "❌ Error: Flox-based test script not found at goose/test_goose.sh"
    echo "Please ensure the goose directory exists with the Flox setup"
    exit 1
fi