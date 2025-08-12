# Verba RAG Stack - Quick Start Guide

## Prerequisites

Install Flox if you haven't already:
```bash
brew install flox
```

## Starting the Stack

### Step 1: Start All Services

In a terminal window, run:
```bash
./start-verba.sh
```

This will:
- Activate the Flox environment
- Install Python packages (first run only, ~2-3 minutes)
- Start Ollama, Weaviate, and Verba services
- Keep the terminal session active (press Ctrl+C to stop)

**Important:** Keep this terminal window open while using Verba.

### Step 2: Pull Required Models (First Time Only)

In a **new terminal window**, run:
```bash
./pull-models.sh
```

This will download:
- `llama3` - The main language model
- `mxbai-embed-large` - The embedding model for document processing

**Note:** Model downloads can take 5-10 minutes depending on your internet connection.

### Step 3: Access Verba

Open your browser and navigate to:
- **Verba UI:** http://localhost:8000

## Using Verba

1. **Upload Documents**
   - Click on the "Documents" section
   - Upload PDFs, text files, or markdown documents
   - Wait for processing to complete

2. **Ask Questions**
   - Use the chat interface to query your documents
   - Verba will retrieve relevant passages and generate answers

## Stopping the Services

Press `Ctrl+C` in the terminal running `start-verba.sh` to stop all services.

## Troubleshooting

### Services won't start
- Make sure no other services are using ports 8000, 8080, or 11434
- Check with: `lsof -i :8000` (repeat for other ports)

### Ollama not responding
- Wait 30-60 seconds after starting for Ollama to initialize
- Check status: `curl http://localhost:11434/api/tags`

### Python package errors
- The environment will auto-install packages on first run
- If issues persist, clear cache: `rm -rf .flox/cache/python`

### Models not downloading
- Ensure Ollama is running first (start-verba.sh must be active)
- Check Ollama logs in the terminal running start-verba.sh

## Manual Commands

If you prefer manual control:

```bash
# Activate environment and start services
flox activate --start-services

# In the activated environment, pull models
ollama pull llama3
ollama pull mxbai-embed-large

# Check service status
flox services status

# Stop services
flox services stop
```