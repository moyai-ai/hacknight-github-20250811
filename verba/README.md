# Verba RAG Stack with Flox

A portable, turn-key Retrieval-Augmented Generation (RAG) stack using Verba, Weaviate, and Ollama, managed by Flox for reproducible environments.

## Prerequisites

Before you can use this setup, you need to install Flox:

### Install Flox

```bash
# On macOS with Homebrew
brew install flox

# Or using the installer script
curl -fsSL https://downloads.flox.dev/by-env/stable/install.sh | sh

# Verify installation
flox --version
```

For other installation methods, visit: https://flox.dev/docs/install

## Setup Instructions

### 1. Navigate to the project directory

```bash
cd /Users/roberthommes/moyai/hcks/hacknight-github-20250811/.conductor/phoenix/verba
```

### 2. Initialize and activate the Flox environment

```bash
# Initialize the Flox environment (only needed once)
flox init

# Activate the environment
flox activate
```

### 3. Setup Ollama models (first time only)

Before starting the stack for the first time, you need to pull the required models:

```bash
./setup-models.sh
```

This will:
- Start Ollama if not running
- Pull the llama3 model for text generation
- Pull the mxbai-embed-large model for embeddings

### 4. Start the RAG stack

Use the provided script to start all services:

```bash
./start-verba.sh
```

Or manually start services:

```bash
# Start all services at once
flox services start

# Or start individual services
flox services start weaviate  # Vector database
flox services start ollama    # LLM server
flox services start verba     # UI
```

### 5. Access the application

Once all services are running:
- **Verba UI**: http://localhost:8000
- **Weaviate**: http://localhost:8080
- **Ollama API**: http://localhost:11434

## Testing the Setup

### Basic Functionality Test

1. **Check service status**:
   ```bash
   flox services status
   ```

2. **Test Ollama**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Test a simple prompt
   curl http://localhost:11434/api/generate -d '{
     "model": "llama3",
     "prompt": "Hello, how are you?",
     "stream": false
   }'
   ```

3. **Test Weaviate**:
   ```bash
   # Check Weaviate health
   curl http://localhost:8080/v1/.well-known/ready
   ```

4. **Access Verba UI**:
   - Open http://localhost:8000 in your browser
   - You should see the Verba interface

### Using Verba

1. **Upload Documents**:
   - Click on "Documents" in the Verba UI
   - Upload PDFs, text files, or other supported formats
   - Documents will be automatically processed and indexed

2. **Query Your Documents**:
   - Use the chat interface to ask questions about your uploaded documents
   - Verba will use RAG to provide context-aware answers

3. **Configure Settings**:
   - Access settings to adjust:
     - Chunk size for document processing
     - Number of retrieved chunks
     - Temperature for LLM responses
     - Model selection

## Stopping the Stack

```bash
# Use the stop script
./stop-stack.sh

# Or manually stop services
flox services stop
```

## Troubleshooting

### Flox not found
If you get "command not found: flox", ensure Flox is installed and in your PATH:
```bash
echo $PATH
which flox
```

### Port conflicts
If services fail to start due to port conflicts:
- Weaviate uses port 8080
- Ollama uses port 11434
- Verba uses port 8000

Check for conflicting services:
```bash
lsof -i :8080
lsof -i :11434
lsof -i :8000
```

### Ollama models not downloading
Ensure you have sufficient disk space and internet connection:
```bash
# Manually pull models
ollama pull llama3
ollama pull mxbai-embed-large
```

### Python/Verba installation issues
The virtual environment is created in `$FLOX_ENV_CACHE/python`. To troubleshoot:
```bash
# Activate Flox environment first
flox activate

# Check Python installation
which python
python --version

# Manually reinstall Verba
source "$FLOX_ENV_CACHE/python/bin/activate"
pip install --upgrade goldenverba
```

## Data Persistence

All data is stored in the `./verba-data` directory:
- Vector embeddings (Weaviate)
- Document metadata
- Configuration settings

This directory is gitignored but will persist between sessions.

## Advanced Configuration

Edit `manifest.toml` to customize:
- Model selection (change `OLLAMA_MODEL`)
- Embedding model (change `OLLAMA_EMBED_MODEL`)
- Port configurations
- Authentication settings
- Resource limits

## Next Steps

1. **Install additional models**:
   ```bash
   ollama pull llama3.1
   ollama pull mistral
   ollama pull phi3
   ```

2. **Customize Verba settings** in the UI for your use case

3. **Integrate with your workflow**:
   - API endpoints are available for programmatic access
   - Weaviate GraphQL interface for custom queries
   - Ollama API for direct LLM interactions

## Resources

- [Flox Documentation](https://flox.dev/docs)
- [Verba Documentation](https://github.com/weaviate/verba)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Ollama Documentation](https://ollama.ai/docs)