# Flox Verba RAG Stack Implementation

## Overview

This project implements a complete Retrieval-Augmented Generation (RAG) stack using Flox.dev's portable environment management system, featuring:
- **Verba**: Open-source RAG application for document Q&A
- **Weaviate**: Vector database for embedding storage
- **Ollama**: Local LLM inference server
- **Flox**: Reproducible development environment manager

## Project Structure

```
verba/
├── manifest.toml       # Flox environment configuration
├── start-stack.sh      # Quick start script for all services
├── stop-stack.sh       # Stop all services
├── .envrc             # Directory-based environment activation
├── .gitignore         # Excludes data and cache directories
└── README.md          # Detailed usage documentation
```

## Prerequisites

### Install Flox

Flox is required to manage the development environment. Install it using one of these methods:

```bash
# macOS with Homebrew
brew install flox

# Universal installer
curl -fsSL https://downloads.flox.dev/by-env/stable/install.sh | sh

# Verify installation
flox --version
```

## Quick Start

### 1. Navigate to Project Directory

```bash
cd /Users/roberthommes/moyai/hcks/hacknight-github-20250811/.conductor/phoenix/verba
```

### 2. Initialize Flox Environment

```bash
# First-time setup
flox init

# Activate the environment
flox activate
```

### 3. Start the RAG Stack

```bash
# Use the convenient start script
./start-stack.sh
```

This script will:
- Verify Flox installation
- Activate the environment
- Download required Ollama models (llama3, mxbai-embed-large)
- Start all services (Weaviate, Ollama, Verba)

### 4. Access the Application

Once running, access:
- **Verba UI**: http://localhost:8000
- **Weaviate API**: http://localhost:8080
- **Ollama API**: http://localhost:11434

## Testing the Setup

### Service Health Checks

```bash
# Check all services status
flox services status

# Test Ollama
curl http://localhost:11434/api/tags

# Test Weaviate
curl http://localhost:8080/v1/.well-known/ready

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "What is RAG?",
  "stream": false
}'
```

### Using Verba

1. **Upload Documents**
   - Navigate to http://localhost:8000
   - Click "Documents" section
   - Upload PDFs, text files, or markdown documents
   - Wait for processing and indexing

2. **Query Your Knowledge Base**
   - Use the chat interface
   - Ask questions about uploaded documents
   - Adjust retrieval settings as needed

3. **Configure Settings**
   - Chunk size for document splitting
   - Number of retrieved contexts
   - LLM temperature and parameters
   - Embedding model selection

## Key Features

### Environment Configuration (manifest.toml)

The Flox manifest includes:
- **Python 3.10** virtual environment
- **Weaviate 1.25.9** vector database
- **Ollama 0.3.5** LLM server
- **Auto-installation** of Verba package
- **Service orchestration** for all components

### Services Management

```bash
# Start all services
flox services start

# Start individual services
flox services start weaviate
flox services start ollama
flox services start verba

# Stop all services
./stop-stack.sh
# or
flox services stop
```

### Data Persistence

All data is stored in `./verba-data/`:
- Vector embeddings
- Document metadata
- Configuration settings
- Upload history

This directory persists between sessions but is gitignored.

## Troubleshooting

### Common Issues

**Flox Command Not Found**
```bash
# Check PATH
echo $PATH
# Reinstall Flox if needed
```

**Port Conflicts**
```bash
# Check ports in use
lsof -i :8080  # Weaviate
lsof -i :11434 # Ollama
lsof -i :8000  # Verba
```

**Model Download Issues**
```bash
# Manually download models
ollama pull llama3
ollama pull mxbai-embed-large
```

**Python/Verba Issues**
```bash
# Activate environment and reinstall
flox activate
source "$FLOX_ENV_CACHE/python/bin/activate"
pip install --upgrade goldenverba
```

## Advanced Usage

### Add More Models

```bash
# Popular models for RAG
ollama pull llama3.1
ollama pull mistral
ollama pull phi3
ollama pull mixtral
```

### Customize Configuration

Edit `manifest.toml` to modify:
- `OLLAMA_MODEL`: Change default LLM
- `OLLAMA_EMBED_MODEL`: Change embedding model
- Port configurations
- Memory limits
- Authentication settings

### API Integration

```python
# Example: Query Weaviate directly
import weaviate

client = weaviate.Client("http://localhost:8080")

# Query your data
result = client.query.get("Document", ["content", "title"]).with_limit(5).do()
```

### Production Considerations

For production deployment:
1. Enable authentication in Weaviate
2. Configure HTTPS endpoints
3. Set resource limits in manifest.toml
4. Implement backup strategies for verba-data
5. Monitor service health and logs

## What This Setup Provides

✅ **Complete RAG Stack**: Everything needed for document Q&A in one environment  
✅ **Local LLM Inference**: Privacy-preserving, no external API calls  
✅ **Portable Environment**: Reproducible setup across machines with Flox  
✅ **Easy Management**: Simple scripts for starting/stopping services  
✅ **Persistent Storage**: Your data and embeddings are preserved  
✅ **Web Interface**: User-friendly UI for document management and queries  

## Next Steps

1. **Install Flox** if you haven't already
2. **Run the setup** using the quick start commands
3. **Upload documents** to build your knowledge base
4. **Experiment** with different models and settings
5. **Integrate** with your existing workflows via APIs

## Resources

- [Flox Documentation](https://flox.dev/docs)
- [Verba GitHub Repository](https://github.com/weaviate/verba)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Ollama Model Library](https://ollama.ai/library)
- [Original Tutorial](https://flox.dev/popular-packages/get-a-portable-turn-key-rag-stack-with-verba-and-flox/)

## Support

For issues or questions:
- Flox: [flox.dev/community](https://flox.dev/community)
- Verba: [GitHub Issues](https://github.com/weaviate/verba/issues)
- Weaviate: [Community Forum](https://forum.weaviate.io/)