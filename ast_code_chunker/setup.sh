#!/bin/bash

# Setup script for AST Code Chunker with Verba integration

set -e

echo "🚀 Setting up AST Code Chunker for Verba RAG..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Make CLI executable
chmod +x cli.py

echo "✅ Setup complete!"
echo ""
echo "To use the AST Code Chunker:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Make sure Weaviate and Ollama are running (use the Verba stack)"
echo "3. Run the CLI: python cli.py --help"
echo ""
echo "Quick start examples:"
echo "  - Test connections: python cli.py test-connection"
echo "  - Index a file: python cli.py index-file your_code.py"
echo "  - Index a directory: python cli.py index-directory /path/to/code -e .py -e .js"
echo "  - Search code: python cli.py search 'function that processes data'"
echo "  - Ask questions: python cli.py ask 'How does the authentication work?'"