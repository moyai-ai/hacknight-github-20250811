#!/usr/bin/env python3
"""
AST-based Code Chunker for RAG Systems

This module provides intelligent code chunking using Abstract Syntax Tree (AST) parsing
to create semantically meaningful chunks for code retrieval and understanding.
"""

import ast
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import textwrap


@dataclass
class CodeChunk:
    """Represents a semantic code chunk extracted from source code."""
    
    id: str
    content: str
    chunk_type: str  # 'class', 'function', 'method', 'module_docstring', 'import', 'global'
    metadata: Dict[str, Any]
    start_line: int
    end_line: int
    file_path: str
    language: str = 'python'
    parent_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for storage."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert chunk to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ASTCodeChunker:
    """
    AST-based code chunker that breaks down code into semantically meaningful chunks.
    
    This chunker uses Python's built-in AST module to parse code and extract:
    - Classes with their methods
    - Standalone functions
    - Import statements
    - Module-level docstrings
    - Global variables and constants
    """
    
    def __init__(self, max_chunk_size: int = 1500, include_context: bool = True):
        """
        Initialize the AST Code Chunker.
        
        Args:
            max_chunk_size: Maximum size of a chunk in characters
            include_context: Whether to include parent context in chunks
        """
        self.max_chunk_size = max_chunk_size
        self.include_context = include_context
        
    def chunk_file(self, file_path: str) -> List[CodeChunk]:
        """
        Chunk a Python file into semantic units.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of CodeChunk objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return self.chunk_code(source_code, file_path)
    
    def chunk_code(self, source_code: str, file_path: str = "unknown") -> List[CodeChunk]:
        """
        Chunk Python source code into semantic units.
        
        Args:
            source_code: Python source code as string
            file_path: Path to the source file (for metadata)
            
        Returns:
            List of CodeChunk objects
        """
        chunks = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            # If parsing fails, fall back to line-based chunking
            return self._fallback_chunk(source_code, file_path)
        
        # Extract module docstring if present
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            chunks.append(self._create_chunk(
                content=f'"""Module Documentation"""\n{module_docstring}',
                chunk_type="module_docstring",
                start_line=1,
                end_line=self._count_lines(module_docstring) + 2,
                file_path=file_path,
                metadata={"module": Path(file_path).stem}
            ))
        
        # Extract imports
        imports = self._extract_imports(tree, source_code)
        if imports:
            chunks.extend(imports)
        
        # Extract global variables and constants
        globals_chunk = self._extract_globals(tree, source_code)
        if globals_chunk:
            chunks.append(globals_chunk)
        
        # Extract classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_chunks = self._extract_class(node, source_code, file_path)
                chunks.extend(class_chunks)
            elif isinstance(node, ast.FunctionDef) and not self._is_nested_function(tree, node):
                func_chunk = self._extract_function(node, source_code, file_path)
                if func_chunk:
                    chunks.append(func_chunk)
        
        return chunks
    
    def _extract_class(self, node: ast.ClassDef, source: str, file_path: str) -> List[CodeChunk]:
        """Extract a class and its methods as separate chunks."""
        chunks = []
        class_name = node.name
        
        # Extract class docstring and signature
        class_docstring = ast.get_docstring(node)
        class_header = self._get_node_source(node, source, include_body=False)
        
        # Create class overview chunk
        class_overview = class_header
        if class_docstring:
            class_overview += f'\n    """{class_docstring}"""'
        
        # Add method signatures to overview
        method_signatures = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                sig = self._get_function_signature(item)
                method_signatures.append(f"    {sig}")
        
        if method_signatures:
            class_overview += "\n\n    # Methods:\n" + "\n".join(method_signatures)
        
        chunks.append(self._create_chunk(
            content=class_overview,
            chunk_type="class",
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=file_path,
            metadata={
                "class_name": class_name,
                "has_docstring": bool(class_docstring),
                "num_methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
            }
        ))
        
        # Extract methods as separate chunks
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_source = self._get_node_source(item, source)
                if method_source:
                    # Add class context if enabled
                    if self.include_context:
                        method_content = f"# In class: {class_name}\n{method_source}"
                    else:
                        method_content = method_source
                    
                    chunks.append(self._create_chunk(
                        content=method_content,
                        chunk_type="method",
                        start_line=item.lineno,
                        end_line=item.end_lineno or item.lineno,
                        file_path=file_path,
                        parent_context=class_name,
                        metadata={
                            "class_name": class_name,
                            "method_name": item.name,
                            "is_private": item.name.startswith('_'),
                            "is_dunder": item.name.startswith('__') and item.name.endswith('__'),
                            "has_docstring": bool(ast.get_docstring(item))
                        }
                    ))
        
        return chunks
    
    def _extract_function(self, node: ast.FunctionDef, source: str, file_path: str) -> Optional[CodeChunk]:
        """Extract a standalone function as a chunk."""
        func_source = self._get_node_source(node, source)
        if not func_source:
            return None
        
        return self._create_chunk(
            content=func_source,
            chunk_type="function",
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=file_path,
            metadata={
                "function_name": node.name,
                "is_private": node.name.startswith('_'),
                "has_docstring": bool(ast.get_docstring(node)),
                "num_args": len(node.args.args)
            }
        )
    
    def _extract_imports(self, tree: ast.Module, source: str) -> List[CodeChunk]:
        """Extract import statements as a single chunk."""
        import_lines = []
        import_nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
        
        if not import_nodes:
            return []
        
        # Sort by line number
        import_nodes.sort(key=lambda x: x.lineno)
        
        # Group consecutive imports
        import_groups = []
        current_group = []
        last_line = -2
        
        for node in import_nodes:
            if node.lineno - last_line <= 1:
                current_group.append(node)
            else:
                if current_group:
                    import_groups.append(current_group)
                current_group = [node]
            last_line = node.lineno
        
        if current_group:
            import_groups.append(current_group)
        
        chunks = []
        for group in import_groups:
            lines = []
            for node in group:
                line = self._get_import_statement(node)
                if line:
                    lines.append(line)
            
            if lines:
                chunks.append(self._create_chunk(
                    content="\n".join(lines),
                    chunk_type="import",
                    start_line=group[0].lineno,
                    end_line=group[-1].lineno,
                    file_path=source,
                    metadata={"num_imports": len(lines)}
                ))
        
        return chunks
    
    def _extract_globals(self, tree: ast.Module, source: str) -> Optional[CodeChunk]:
        """Extract global variables and constants."""
        global_statements = []
        
        for node in tree.body:
            if isinstance(node, ast.Assign):
                # Check if it's a module-level assignment
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        line = self._get_node_source(node, source)
                        if line:
                            global_statements.append(line)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                line = self._get_node_source(node, source)
                if line:
                    global_statements.append(line)
        
        if not global_statements:
            return None
        
        return self._create_chunk(
            content="\n".join(global_statements),
            chunk_type="global",
            start_line=1,
            end_line=len(source.splitlines()),
            file_path=source,
            metadata={"num_globals": len(global_statements)}
        )
    
    def _get_node_source(self, node: ast.AST, source: str, include_body: bool = True) -> Optional[str]:
        """Get the source code for an AST node."""
        try:
            lines = source.splitlines()
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                start = node.lineno - 1
                end = node.end_lineno
                
                if not include_body and isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    # Just get the signature/header
                    for i, child in enumerate(node.body):
                        if hasattr(child, 'lineno'):
                            end = child.lineno - 1
                            break
                
                node_lines = lines[start:end]
                # Remove common indentation
                if node_lines:
                    return textwrap.dedent("\n".join(node_lines))
            return None
        except Exception:
            return None
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get just the function signature without body."""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        signature = f"def {node.name}({', '.join(args)})"
        if node.returns:
            signature += " -> ..."
        signature += ": ..."
        
        return signature
    
    def _get_import_statement(self, node: ast.AST) -> Optional[str]:
        """Convert import node to string."""
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            return f"import {', '.join(names)}"
        elif isinstance(node, ast.ImportFrom):
            names = [alias.name for alias in node.names]
            module = node.module or ''
            return f"from {module} import {', '.join(names)}"
        return None
    
    def _is_nested_function(self, tree: ast.Module, func_node: ast.FunctionDef) -> bool:
        """Check if a function is nested inside a class or another function."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node != func_node:
                if any(child == func_node for child in ast.walk(node)):
                    return True
        return False
    
    def _create_chunk(self, content: str, chunk_type: str, start_line: int, 
                     end_line: int, file_path: str, parent_context: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> CodeChunk:
        """Create a CodeChunk object with a unique ID."""
        # Generate unique ID based on content
        chunk_id = hashlib.md5(f"{file_path}:{start_line}:{content[:100]}".encode()).hexdigest()[:12]
        
        return CodeChunk(
            id=chunk_id,
            content=content,
            chunk_type=chunk_type,
            metadata=metadata or {},
            start_line=start_line,
            end_line=end_line,
            file_path=file_path,
            parent_context=parent_context
        )
    
    def _fallback_chunk(self, source: str, file_path: str) -> List[CodeChunk]:
        """Fallback to simple line-based chunking if AST parsing fails."""
        chunks = []
        lines = source.splitlines()
        chunk_size = 50  # Lines per chunk
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = "\n".join(chunk_lines)
            
            chunks.append(self._create_chunk(
                content=chunk_content,
                chunk_type="code_block",
                start_line=i + 1,
                end_line=min(i + chunk_size, len(lines)),
                file_path=file_path,
                metadata={"fallback": True}
            ))
        
        return chunks
    
    def _count_lines(self, text: str) -> int:
        """Count the number of lines in text."""
        return len(text.splitlines())


class MultiLanguageASTChunker:
    """
    Multi-language AST chunker that supports various programming languages.
    Uses python-language-server components for broader language support.
    """
    
    def __init__(self):
        self.python_chunker = ASTCodeChunker()
        self.language_parsers = {
            'python': self.python_chunker,
            'py': self.python_chunker,
        }
    
    def chunk_file(self, file_path: str) -> List[CodeChunk]:
        """
        Chunk a code file based on its language.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            List of CodeChunk objects
        """
        path = Path(file_path)
        extension = path.suffix.lstrip('.')
        
        if extension in self.language_parsers:
            return self.language_parsers[extension].chunk_file(file_path)
        else:
            # Fallback to text-based chunking for unsupported languages
            return self._generic_chunk(file_path)
    
    def _generic_chunk(self, file_path: str) -> List[CodeChunk]:
        """Generic chunking for unsupported languages."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple function/class detection using regex
        import re
        
        chunks = []
        
        # Try to detect functions (works for many C-like languages)
        func_pattern = r'((?:public|private|protected|static|async|def|function|func)\s+[\w<>]+\s+\w+\s*\([^)]*\)\s*{[^}]*})'
        functions = re.findall(func_pattern, content, re.DOTALL)
        
        for i, func in enumerate(functions):
            chunk_id = hashlib.md5(f"{file_path}:func_{i}".encode()).hexdigest()[:12]
            chunks.append(CodeChunk(
                id=chunk_id,
                content=func,
                chunk_type="function",
                metadata={"language": Path(file_path).suffix.lstrip('.')},
                start_line=0,
                end_line=0,
                file_path=file_path
            ))
        
        # If no functions found, do line-based chunking
        if not chunks:
            lines = content.splitlines()
            chunk_size = 50
            
            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i:i + chunk_size]
                chunk_content = "\n".join(chunk_lines)
                chunk_id = hashlib.md5(f"{file_path}:lines_{i}".encode()).hexdigest()[:12]
                
                chunks.append(CodeChunk(
                    id=chunk_id,
                    content=chunk_content,
                    chunk_type="code_block",
                    metadata={"language": Path(file_path).suffix.lstrip('.')},
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                    file_path=file_path
                ))
        
        return chunks


if __name__ == "__main__":
    # Example usage
    chunker = ASTCodeChunker()
    
    # Example Python code
    sample_code = '''
"""
This is a sample module for demonstrating AST-based chunking.
"""

import os
import sys
from typing import List, Dict

# Global configuration
DEBUG = True
VERSION = "1.0.0"

class DataProcessor:
    """Processes data with various transformations."""
    
    def __init__(self, config: Dict):
        """Initialize the processor with configuration."""
        self.config = config
        self.data = []
    
    def load_data(self, path: str) -> List:
        """Load data from a file."""
        with open(path, 'r') as f:
            return f.readlines()
    
    def process(self, data: List) -> List:
        """Process the data."""
        return [self.transform(item) for item in data]
    
    def transform(self, item: str) -> str:
        """Transform a single item."""
        return item.upper()

def main():
    """Main entry point."""
    processor = DataProcessor({"debug": DEBUG})
    data = processor.load_data("input.txt")
    result = processor.process(data)
    print(result)

if __name__ == "__main__":
    main()
'''
    
    chunks = chunker.chunk_code(sample_code, "example.py")
    
    print(f"Generated {len(chunks)} chunks:\n")
    for chunk in chunks:
        print(f"Chunk Type: {chunk.chunk_type}")
        print(f"Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"Metadata: {chunk.metadata}")
        print(f"Content Preview: {chunk.content[:100]}...")
        print("-" * 50)