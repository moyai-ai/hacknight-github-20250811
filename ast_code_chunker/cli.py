#!/usr/bin/env python3
"""
CLI for AST-based Code RAG System

Command-line interface for indexing code repositories and performing
semantic code search using AST-based chunking.
"""

import os
import sys
import time
import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from verba_integration import VerbaCodeRAG
from ast_chunker import ASTCodeChunker


console = Console()


@click.group()
@click.option('--weaviate-url', 
              default=lambda: os.environ.get('WEAVIATE_URL', 'http://localhost:8080'), 
              help='Weaviate URL')
@click.option('--ollama-url', 
              default=lambda: os.environ.get('OLLAMA_URL', 'http://localhost:11434'), 
              help='Ollama URL')
@click.option('--embedding-model', 
              default=lambda: os.environ.get('OLLAMA_EMBED_MODEL', 'mxbai-embed-large'), 
              help='Embedding model')
@click.option('--collection-name',
              default=lambda: os.environ.get('WEAVIATE_COLLECTION', 'CodeChunks'),
              help='Weaviate collection name')
@click.pass_context
def cli(ctx, weaviate_url, ollama_url, embedding_model, collection_name):
    """AST-based Code RAG System - Intelligent code chunking and retrieval"""
    ctx.ensure_object(dict)
    
    # Store configuration
    ctx.obj['config'] = {
        'weaviate_url': weaviate_url,
        'ollama_url': ollama_url,
        'embedding_model': embedding_model,
        'collection_name': collection_name
    }
    
    # Initialize RAG lazily
    ctx.obj['rag'] = None

def get_rag(ctx):
    """Lazy initialization of RAG system"""
    if ctx.obj['rag'] is None:
        config = ctx.obj['config']
        ctx.obj['rag'] = VerbaCodeRAG(
            weaviate_url=config['weaviate_url'],
            ollama_url=config['ollama_url'],
            embedding_model=config['embedding_model'],
            collection_name=config['collection_name']
        )
    return ctx.obj['rag']


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def index_file(ctx, file_path):
    """Index a single code file"""
    rag = get_rag(ctx)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Indexing {file_path}...", total=None)
        
        result = rag.index_file(file_path)
        
        progress.update(task, completed=True)
    
    if result['success']:
        console.print(f"✅ Successfully indexed {result['indexed_chunks']} chunks from {file_path}", style="green")
    else:
        console.print(f"❌ Failed to index {file_path}", style="red")
        for error in result['errors']:
            console.print(f"  - {error}", style="red")


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--extensions', '-e', multiple=True, default=['.py'], help='File extensions to index')
@click.pass_context
def index_directory(ctx, directory, extensions):
    """Index all code files in a directory"""
    rag = get_rag(ctx)
    
    extensions = list(extensions) if extensions else ['.py']
    
    console.print(f"Indexing directory: {directory}")
    console.print(f"Extensions: {', '.join(extensions)}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Indexing files...", total=None)
        
        results = rag.index_directory(directory, extensions)
        
        progress.update(task, completed=True)
    
    # Display results
    console.print(f"\n✅ Indexed {results['total_chunks']} chunks from {results['total_files']} files", style="green")
    
    if results['errors']:
        console.print(f"\n⚠️  {len(results['errors'])} errors occurred:", style="yellow")
        for error in results['errors'][:5]:
            console.print(f"  - {error}", style="yellow")
        if len(results['errors']) > 5:
            console.print(f"  ... and {len(results['errors']) - 5} more", style="yellow")


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Number of results')
@click.option('--chunk-type', '-t', multiple=True, help='Filter by chunk type')
@click.pass_context
def search(ctx, query, limit, chunk_type):
    """Search for code using semantic similarity"""
    rag = get_rag(ctx)
    
    chunk_types = list(chunk_type) if chunk_type else None
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching...", total=None)
        
        results = rag.search(query, limit=limit, chunk_types=chunk_types)
        
        progress.update(task, completed=True)
    
    if not results:
        console.print("No results found", style="yellow")
        return
    
    console.print(f"\nFound {len(results)} results for: '{query}'\n")
    
    for i, result in enumerate(results, 1):
        # Create a panel for each result
        content = Syntax(
            result['content'][:300] + ("..." if len(result['content']) > 300 else ""),
            result.get('language', 'python'),
            theme="monokai",
            line_numbers=True,
            start_line=result.get('start_line', 1)
        )
        
        title = f"[{i}] {result['chunk_type'].upper()} - {result['file_path']}"
        if result.get('parent_context'):
            title += f" (in {result['parent_context']})"
        
        panel = Panel(
            content,
            title=title,
            subtitle=f"Lines {result['location'].split(':')[1]}",
            expand=False
        )
        
        console.print(panel)


@cli.command()
@click.argument('question')
@click.option('--model', '-m', 
              default=lambda: os.environ.get('OLLAMA_CHAT_MODEL', 'llama3.2'), 
              help='LLM model to use')
@click.option('--context-limit', '-c', default=5, help='Number of code chunks to use as context')
@click.pass_context
def ask(ctx, question, model, context_limit):
    """Ask a question about the codebase"""
    rag = get_rag(ctx)
    
    console.print(f"\n❓ Question: {question}\n", style="cyan")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating answer...", total=None)
        
        answer = rag.answer_question(question, model=model, context_limit=context_limit)
        
        progress.update(task, completed=True)
    
    console.print(Panel(answer, title="Answer", border_style="green"))


@cli.command()
@click.pass_context
def stats(ctx):
    """Show statistics about indexed code"""
    rag = get_rag(ctx)
    
    stats = rag.get_stats()
    
    if 'error' in stats:
        console.print(f"Error getting stats: {stats['error']}", style="red")
        return
    
    # Create a table for chunk types
    table = Table(title="Code Index Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Chunks", str(stats['total_chunks']))
    table.add_row("Collection", stats['collection'])
    
    for chunk_type, count in stats['chunk_types'].items():
        table.add_row(f"  {chunk_type.capitalize()}", str(count))
    
    console.print(table)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for chunks (JSON)')
def preview_chunks(file_path, output):
    """Preview how a file will be chunked without indexing"""
    chunker = ASTCodeChunker()
    
    try:
        chunks = chunker.chunk_file(file_path)
        
        console.print(f"\n📄 File: {file_path}")
        console.print(f"Generated {len(chunks)} chunks:\n")
        
        for i, chunk in enumerate(chunks, 1):
            console.print(f"[{i}] {chunk.chunk_type.upper()} (lines {chunk.start_line}-{chunk.end_line})")
            
            if chunk.parent_context:
                console.print(f"    Parent: {chunk.parent_context}")
            
            if chunk.metadata:
                for key, value in chunk.metadata.items():
                    console.print(f"    {key}: {value}")
            
            # Show content preview
            content_preview = chunk.content[:150].replace('\n', ' ')
            if len(chunk.content) > 150:
                content_preview += "..."
            console.print(f"    Preview: {content_preview}", style="dim")
            console.print()
        
        # Save to file if requested
        if output:
            chunks_data = [chunk.to_dict() for chunk in chunks]
            with open(output, 'w') as f:
                json.dump(chunks_data, f, indent=2)
            console.print(f"✅ Chunks saved to {output}", style="green")
    
    except Exception as e:
        console.print(f"❌ Error chunking file: {e}", style="red")


@cli.command()
@click.pass_context
def test_connection(ctx):
    """Test connections to Weaviate and Ollama"""
    console.print("Testing connections...\n")
    
    config = ctx.obj['config']
    
    # Test Weaviate
    try:
        import weaviate
        client = weaviate.Client(url=config['weaviate_url'])
        client.schema.get()
        console.print(f"✅ Weaviate connection: OK ({config['weaviate_url']})", style="green")
    except Exception as e:
        console.print(f"❌ Weaviate connection: FAILED - {e}", style="red")
    
    # Test Ollama
    try:
        import ollama
        client = ollama.Client(host=config['ollama_url'])
        models = client.list()
        console.print(f"✅ Ollama connection: OK ({config['ollama_url']})", style="green")
        console.print(f"   Available models: {', '.join([m['name'] for m in models['models']])}")
    except Exception as e:
        console.print(f"❌ Ollama connection: FAILED - {e}", style="red")


@cli.command()
@click.pass_context
def init_schema(ctx):
    """Initialize Weaviate schema for code chunks"""
    console.print("Initializing Weaviate schema...\n")
    
    try:
        rag = get_rag(ctx)
        console.print(f"✅ Schema initialized for collection: {ctx.obj['config']['collection_name']}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to initialize schema: {e}", style="red")
        sys.exit(1)

@cli.command()
@click.pass_context
def init_models(ctx):
    """Download required Ollama models"""
    console.print("Downloading required models...\n")
    
    config = ctx.obj['config']
    
    try:
        import ollama
        client = ollama.Client(host=config['ollama_url'])
        
        # Pull embedding model
        embed_model = config['embedding_model']
        console.print(f"📥 Downloading embedding model: {embed_model}")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Pulling {embed_model}...", total=None)
            client.pull(embed_model)
            progress.update(task, completed=True)
        console.print(f"✅ {embed_model} downloaded", style="green")
        
        # Pull chat model
        chat_model = os.environ.get('OLLAMA_CHAT_MODEL', 'llama3.2')
        console.print(f"\n📥 Downloading chat model: {chat_model}")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Pulling {chat_model}...", total=None)
            client.pull(chat_model)
            progress.update(task, completed=True)
        console.print(f"✅ {chat_model} downloaded", style="green")
        
    except Exception as e:
        console.print(f"❌ Failed to download models: {e}", style="red")
        sys.exit(1)

@cli.command()
@click.pass_context
def check_services(ctx):
    """Check if required services are running"""
    console.print("Checking services...\n")
    
    config = ctx.obj['config']
    services_ok = True
    
    # Check Weaviate
    try:
        import requests
        response = requests.get(f"{config['weaviate_url']}/v1/.well-known/ready", timeout=2)
        if response.status_code == 200:
            console.print("✅ Weaviate: Running", style="green")
        else:
            console.print("⚠️  Weaviate: Not ready", style="yellow")
            services_ok = False
    except:
        console.print("❌ Weaviate: Not running", style="red")
        console.print("   Run: flox services start weaviate", style="dim")
        services_ok = False
    
    # Check Ollama
    try:
        import requests
        response = requests.get(f"{config['ollama_url']}/api/tags", timeout=2)
        if response.status_code == 200:
            console.print("✅ Ollama: Running", style="green")
        else:
            console.print("⚠️  Ollama: Not ready", style="yellow")
            services_ok = False
    except:
        console.print("❌ Ollama: Not running", style="red")
        console.print("   Run: flox services start ollama", style="dim")
        services_ok = False
    
    if not services_ok:
        console.print("\n💡 Start all services with: flox services start", style="cyan")
        sys.exit(1)
    else:
        console.print("\n✅ All services are running!", style="green")

if __name__ == '__main__':
    cli(obj={})