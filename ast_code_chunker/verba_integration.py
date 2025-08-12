#!/usr/bin/env python3
"""
Verba Integration for AST-based Code Chunking

This module integrates the AST code chunker with Verba's RAG system,
providing code-aware document processing and retrieval.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import weaviate
from weaviate.embedded import EmbeddedOptions
import ollama

from ast_chunker import ASTCodeChunker, MultiLanguageASTChunker, CodeChunk


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerbaCodeRAG:
    """
    Integration layer between AST code chunker and Verba RAG system.
    
    This class handles:
    - Code file ingestion using AST-based chunking
    - Vector embedding generation using Ollama
    - Storage in Weaviate vector database
    - Semantic code search and retrieval
    """
    
    def __init__(self, 
                 weaviate_url: str = "http://localhost:8080",
                 ollama_url: str = "http://localhost:11434",
                 embedding_model: str = "mxbai-embed-large",
                 collection_name: str = "CodeChunks"):
        """
        Initialize Verba Code RAG integration.
        
        Args:
            weaviate_url: URL of Weaviate instance
            ollama_url: URL of Ollama instance
            embedding_model: Ollama model to use for embeddings
            collection_name: Weaviate collection name for code chunks
        """
        self.weaviate_url = weaviate_url
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        
        # Initialize chunker
        self.chunker = MultiLanguageASTChunker()
        
        # Initialize Weaviate client
        self.client = self._init_weaviate()
        
        # Initialize Ollama client
        self.ollama_client = ollama.Client(host=ollama_url)
        
        # Create collection if it doesn't exist
        self._create_collection()
    
    def _init_weaviate(self) -> weaviate.Client:
        """Initialize Weaviate client."""
        try:
            client = weaviate.Client(
                url=self.weaviate_url,
                timeout_config=(5, 15)
            )
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
    
    def _create_collection(self):
        """Create Weaviate collection for code chunks if it doesn't exist."""
        schema = {
            "class": self.collection_name,
            "description": "Collection for AST-based code chunks",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The code chunk content"
                },
                {
                    "name": "chunk_type",
                    "dataType": ["string"],
                    "description": "Type of code chunk (class, function, method, etc.)"
                },
                {
                    "name": "file_path",
                    "dataType": ["string"],
                    "description": "Path to the source file"
                },
                {
                    "name": "language",
                    "dataType": ["string"],
                    "description": "Programming language"
                },
                {
                    "name": "start_line",
                    "dataType": ["int"],
                    "description": "Starting line number in source file"
                },
                {
                    "name": "end_line",
                    "dataType": ["int"],
                    "description": "Ending line number in source file"
                },
                {
                    "name": "parent_context",
                    "dataType": ["string"],
                    "description": "Parent context (e.g., class name for methods)"
                },
                {
                    "name": "metadata",
                    "dataType": ["text"],
                    "description": "Additional metadata as JSON"
                },
                {
                    "name": "embedding",
                    "dataType": ["number[]"],
                    "description": "Vector embedding of the code chunk"
                },
                {
                    "name": "indexed_at",
                    "dataType": ["date"],
                    "description": "Timestamp when chunk was indexed"
                }
            ]
        }
        
        try:
            # Check if collection exists
            existing_classes = self.client.schema.get()
            class_names = [c['class'] for c in existing_classes.get('classes', [])]
            
            if self.collection_name not in class_names:
                self.client.schema.create_class(schema)
                logger.info(f"Created Weaviate collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.ollama_client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    def index_file(self, file_path: str) -> Dict[str, Any]:
        """
        Index a code file using AST-based chunking.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Dictionary with indexing results
        """
        logger.info(f"Indexing file: {file_path}")
        
        try:
            # Chunk the file
            chunks = self.chunker.chunk_file(file_path)
            logger.info(f"Generated {len(chunks)} chunks from {file_path}")
            
            # Index each chunk
            indexed_count = 0
            errors = []
            
            for chunk in chunks:
                try:
                    # Generate embedding
                    embedding = self.generate_embedding(chunk.content)
                    
                    if not embedding:
                        errors.append(f"Failed to generate embedding for chunk {chunk.id}")
                        continue
                    
                    # Prepare data for Weaviate
                    data_object = {
                        "content": chunk.content,
                        "chunk_type": chunk.chunk_type,
                        "file_path": chunk.file_path,
                        "language": chunk.language,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "parent_context": chunk.parent_context or "",
                        "metadata": json.dumps(chunk.metadata),
                        "embedding": embedding,
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                    
                    # Add to Weaviate
                    self.client.data_object.create(
                        data_object=data_object,
                        class_name=self.collection_name
                    )
                    
                    indexed_count += 1
                    
                except Exception as e:
                    errors.append(f"Failed to index chunk {chunk.id}: {str(e)}")
            
            return {
                "file_path": file_path,
                "total_chunks": len(chunks),
                "indexed_chunks": indexed_count,
                "errors": errors,
                "success": len(errors) == 0
            }
            
        except Exception as e:
            logger.error(f"Failed to index file {file_path}: {e}")
            return {
                "file_path": file_path,
                "total_chunks": 0,
                "indexed_chunks": 0,
                "errors": [str(e)],
                "success": False
            }
    
    def index_directory(self, directory_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Index all code files in a directory.
        
        Args:
            directory_path: Path to directory
            extensions: List of file extensions to index (e.g., ['.py', '.js'])
            
        Returns:
            Dictionary with indexing results
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
        
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        results = {
            "directory": directory_path,
            "files_processed": [],
            "total_files": 0,
            "total_chunks": 0,
            "errors": []
        }
        
        # Find all code files
        code_files = []
        for ext in extensions:
            code_files.extend(directory.rglob(f"*{ext}"))
        
        results["total_files"] = len(code_files)
        
        # Index each file
        for file_path in code_files:
            result = self.index_file(str(file_path))
            results["files_processed"].append(result)
            results["total_chunks"] += result["indexed_chunks"]
            results["errors"].extend(result["errors"])
        
        return results
    
    def search(self, query: str, limit: int = 10, chunk_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for code chunks using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            chunk_types: Filter by chunk types (e.g., ['function', 'class'])
            
        Returns:
            List of matching code chunks with metadata
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        # Build Weaviate query
        near_vector = {
            "vector": query_embedding,
            "certainty": 0.7
        }
        
        query_builder = (
            self.client.query
            .get(self.collection_name, [
                "content", "chunk_type", "file_path", "language",
                "start_line", "end_line", "parent_context", "metadata"
            ])
            .with_near_vector(near_vector)
            .with_limit(limit)
        )
        
        # Add chunk type filter if specified
        if chunk_types:
            where_filter = {
                "path": ["chunk_type"],
                "operator": "ContainsAny",
                "valueStringArray": chunk_types
            }
            query_builder = query_builder.with_where(where_filter)
        
        # Execute search
        try:
            results = query_builder.do()
            
            if self.collection_name in results.get("data", {}).get("Get", {}):
                chunks = results["data"]["Get"][self.collection_name]
                
                # Parse and format results
                formatted_results = []
                for chunk in chunks:
                    metadata = json.loads(chunk.get("metadata", "{}"))
                    formatted_results.append({
                        "content": chunk["content"],
                        "chunk_type": chunk["chunk_type"],
                        "file_path": chunk["file_path"],
                        "language": chunk["language"],
                        "location": f"{chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']}",
                        "parent_context": chunk.get("parent_context"),
                        "metadata": metadata
                    })
                
                return formatted_results
            
            return []
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def generate_context(self, query: str, limit: int = 5) -> str:
        """
        Generate context for LLM by retrieving relevant code chunks.
        
        Args:
            query: Query or question about code
            limit: Number of chunks to retrieve
            
        Returns:
            Formatted context string for LLM
        """
        results = self.search(query, limit=limit)
        
        if not results:
            return "No relevant code found."
        
        context_parts = ["Here are the relevant code sections:\n"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n--- Code Chunk {i} ---")
            context_parts.append(f"File: {result['file_path']}")
            context_parts.append(f"Type: {result['chunk_type']}")
            if result.get('parent_context'):
                context_parts.append(f"Context: {result['parent_context']}")
            context_parts.append(f"Location: Lines {result['location'].split(':')[1]}")
            context_parts.append("\n```python")
            context_parts.append(result['content'])
            context_parts.append("```\n")
        
        return "\n".join(context_parts)
    
    def answer_question(self, question: str, model: str = "llama3", context_limit: int = 5) -> str:
        """
        Answer a question about code using RAG.
        
        Args:
            question: Question about the codebase
            model: Ollama model to use for generation
            context_limit: Number of code chunks to retrieve
            
        Returns:
            Generated answer
        """
        # Retrieve relevant context
        context = self.generate_context(question, limit=context_limit)
        
        # Create prompt
        prompt = f"""You are a helpful code assistant. Use the provided code context to answer the question accurately.

{context}

Question: {question}

Answer: """
        
        try:
            # Generate answer using Ollama
            response = self.ollama_client.generate(
                model=model,
                prompt=prompt
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed code chunks."""
        try:
            # Query for all chunks to get counts
            result = self.client.query.aggregate(self.collection_name).with_meta_count().do()
            
            total_chunks = result['data']['Aggregate'][self.collection_name][0]['meta']['count']
            
            # Get chunk type distribution
            chunk_types = {}
            for chunk_type in ['class', 'function', 'method', 'import', 'global', 'module_docstring']:
                where_filter = {
                    "path": ["chunk_type"],
                    "operator": "Equal",
                    "valueString": chunk_type
                }
                type_result = (
                    self.client.query.aggregate(self.collection_name)
                    .with_meta_count()
                    .with_where(where_filter)
                    .do()
                )
                count = type_result['data']['Aggregate'][self.collection_name][0]['meta']['count']
                if count > 0:
                    chunk_types[chunk_type] = count
            
            return {
                "total_chunks": total_chunks,
                "chunk_types": chunk_types,
                "collection": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                "total_chunks": 0,
                "chunk_types": {},
                "error": str(e)
            }


if __name__ == "__main__":
    # Example usage
    rag = VerbaCodeRAG()
    
    # Example: Index a Python file
    result = rag.index_file("ast_chunker.py")
    print(f"Indexing result: {result}")
    
    # Example: Search for code
    search_results = rag.search("function that extracts classes", limit=5)
    for result in search_results:
        print(f"\nFound: {result['chunk_type']} in {result['file_path']}")
        print(f"Content preview: {result['content'][:200]}...")
    
    # Example: Answer a question
    answer = rag.answer_question("How does the AST chunker extract class methods?")
    print(f"\nAnswer: {answer}")
    
    # Get statistics
    stats = rag.get_stats()
    print(f"\nStatistics: {stats}")