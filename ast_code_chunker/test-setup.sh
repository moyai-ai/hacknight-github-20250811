#!/usr/bin/env bash
# Test script to verify AST Code Chunker setup

echo "🔍 Testing AST Code Chunker Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Flox
echo -n "Checking Flox installation... "
if command -v flox &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "  Please install Flox: https://flox.dev/docs/install"
    exit 1
fi

# Check Flox environment
echo -n "Checking Flox environment... "
if [ -f ".flox/env/manifest.toml" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "  Run: flox init && cp manifest.toml .flox/env/manifest.toml"
fi

# Check if in Flox environment
echo -n "Checking if Flox is activated... "
if [ -n "$FLOX_ENV" ]; then
    echo -e "${GREEN}✓${NC}"
    
    # Check Python
    echo -n "Checking Python... "
    if python --version &> /dev/null; then
        echo -e "${GREEN}✓${NC} ($(python --version 2>&1))"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    # Check Python packages
    echo -n "Checking Python packages... "
    if python -c "import weaviate, ollama, jedi, click, rich" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠${NC} Some packages missing - they will be installed on first run"
    fi
    
    # Check Ollama service
    echo -n "Checking Ollama service... "
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} (running)"
    else
        echo -e "${YELLOW}⚠${NC} (not running - start with: flox services start ollama)"
    fi
    
    # Check Weaviate service
    echo -n "Checking Weaviate service... "
    if curl -s http://localhost:8080/v1/.well-known/ready >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} (running)"
    else
        echo -e "${YELLOW}⚠${NC} (not running - start with: flox services start weaviate)"
    fi
    
    # Check Ollama models
    echo -n "Checking Ollama models... "
    if ollama list 2>/dev/null | grep -q "mxbai-embed-large"; then
        echo -e "${GREEN}✓${NC} (embedding model found)"
    else
        echo -e "${YELLOW}⚠${NC} (embedding model not found - pull with: ollama pull mxbai-embed-large)"
    fi
    
else
    echo -e "${YELLOW}⚠${NC}"
    echo "  Run: flox activate"
    echo ""
    echo "Or use the all-in-one startup script:"
    echo "  ./start-ast-chunker.sh"
fi

echo ""
echo "=================================="
echo "To start everything at once, run:"
echo "  ./start-ast-chunker.sh"
echo ""