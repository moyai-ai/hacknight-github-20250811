#!/bin/bash
# Stop the Verba RAG stack

echo "🛑 Stopping Verba RAG Stack..."
echo ""

# Check if Flox is installed
if ! command -v flox &> /dev/null; then
    echo "❌ Error: Flox is not installed."
    exit 1
fi

# Stop all Flox services
flox services stop

echo ""
echo "✅ All services stopped!"