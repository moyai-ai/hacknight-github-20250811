# AST Code Chunker - Quick Start Guide

## 🚀 Quick Setup (One Command)

The easiest way to get started:

```bash
./start-ast-chunker.sh
```

This will:
1. ✅ Initialize the Flox environment (if needed)
2. ✅ Start Weaviate (vector database) and Ollama (LLM)
3. ✅ Download required models
4. ✅ Initialize the database schema
5. ✅ Keep services running

## 📋 Prerequisites

1. **Install Flox** (if not already installed):
   ```bash
   curl -L https://flox.dev/install | sh
   ```

2. **Clone and navigate to the project**:
   ```bash
   cd ast_code_chunker
   ```

## 🎯 Using AST Code Chunker

After running `./start-ast-chunker.sh`, open a **new terminal** and:

1. **Navigate to the project directory**:
   ```bash
   cd /path/to/ast_code_chunker
   ```

2. **Activate the Flox environment**:
   ```bash
   flox activate
   ```

3. **Use the AST chunker commands**:

   ```bash
   # Index a single file
   ast-chunk index-file example.py
   
   # Index an entire directory
   ast-chunk index-directory ./src -e .py -e .js
   
   # Search your indexed code
   ast-chunk search "database connection"
   
   # Ask questions about your code
   ast-chunk ask "How does the authentication system work?"
   
   # View statistics
   ast-chunk stats
   
   # Preview how a file would be chunked (without indexing)
   ast-chunk preview-chunks myfile.py
   ```

## 🔍 Verify Your Setup

Run the test script to check if everything is configured correctly:

```bash
./test-setup.sh
```

## 🛠️ Manual Setup (Alternative)

If you prefer to set things up manually:

1. **Initialize Flox environment**:
   ```bash
   flox init
   cp manifest.toml .flox/env/manifest.toml
   ```

2. **Activate the environment**:
   ```bash
   flox activate
   ```

3. **Start services**:
   ```bash
   flox services start
   ```

4. **Pull models**:
   ```bash
   ollama pull mxbai-embed-large
   ollama pull llama3.2
   ```

5. **Initialize schema**:
   ```bash
   python cli.py init-schema
   ```

## 📝 Common Issues

### "Module not found" errors
- Make sure you're in an activated Flox environment (`flox activate`)
- The environment will automatically install Python dependencies on first activation

### Services not starting
- Check if ports 8080 (Weaviate) and 11434 (Ollama) are available
- Stop any conflicting services using these ports

### Models not downloading
- Ensure you have a stable internet connection
- Models are large (several GB) and may take time to download
- You can manually pull models: `ollama pull mxbai-embed-large`

## 🎓 Understanding AST Chunking

AST (Abstract Syntax Tree) chunking intelligently splits code based on its structure rather than arbitrary line counts. This means:

- Functions stay together
- Classes are preserved as units
- Context is maintained for better search results
- Code relationships are understood

## 💡 Tips

1. **Start small**: Index a single file first to test the system
2. **Use extensions**: When indexing directories, specify file extensions with `-e`
3. **Ask natural questions**: The RAG system understands context
4. **Check stats**: Use `ast-chunk stats` to see what's indexed

## 🔧 Advanced Configuration

Edit `.flox/env/manifest.toml` to customize:
- Model choices (change `OLLAMA_EMBED_MODEL` or `OLLAMA_CHAT_MODEL`)
- Chunk sizes (adjust `CHUNK_SIZE`)
- Port configurations
- Data directories

## 📚 Next Steps

1. Index your codebase
2. Try different search queries
3. Ask complex questions about your code architecture
4. Explore the chunking strategies with `preview-chunks`

## 🆘 Getting Help

- Run `ast-chunk --help` for command documentation
- Check `./test-setup.sh` to diagnose issues
- Review logs in the terminal where services are running