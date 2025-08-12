#!/usr/bin/env python3
"""
Test script to demonstrate AST-based chunking
"""

from ast_chunker import ASTCodeChunker
import json

def test_chunking():
    """Test the AST chunker with the example file."""
    
    print("🔍 Testing AST-based Code Chunking\n")
    print("=" * 60)
    
    # Initialize chunker
    chunker = ASTCodeChunker(include_context=True)
    
    # Chunk the test file
    chunks = chunker.chunk_file("test_example.py")
    
    print(f"✅ Generated {len(chunks)} chunks from test_example.py\n")
    
    # Display chunk statistics
    chunk_types = {}
    for chunk in chunks:
        chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
    
    print("📊 Chunk Type Distribution:")
    for chunk_type, count in sorted(chunk_types.items()):
        print(f"   - {chunk_type}: {count}")
    
    print("\n" + "=" * 60)
    print("📝 Detailed Chunk Information:\n")
    
    # Display each chunk
    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}] {chunk.chunk_type.upper()}")
        print(f"    Lines: {chunk.start_line}-{chunk.end_line}")
        
        if chunk.parent_context:
            print(f"    Parent: {chunk.parent_context}")
        
        if chunk.metadata:
            print(f"    Metadata: {json.dumps(chunk.metadata, indent=8)}")
        
        # Show content preview
        lines = chunk.content.split('\n')
        preview = lines[0] if lines else ""
        if len(preview) > 60:
            preview = preview[:57] + "..."
        print(f"    Preview: {preview}")
        
        # For methods and functions, show the signature
        if chunk.chunk_type in ['function', 'method']:
            for line in lines[:3]:
                if line.strip().startswith('def '):
                    print(f"    Signature: {line.strip()}")
                    break
        
        print()
    
    print("=" * 60)
    print("\n🎯 Example Use Cases:")
    print("1. Search for database-related code:")
    print("   - Chunks with 'database' or 'connection' would be retrieved")
    print("\n2. Find all data transformation methods:")
    print("   - Methods like '_transform_item' would be found")
    print("\n3. Understand class structures:")
    print("   - Class chunks provide overview with all method signatures")
    print("\n4. Locate configuration and constants:")
    print("   - Global variables like DEBUG_MODE and VERSION are captured")
    
    # Save chunks to file for inspection
    output_file = "test_chunks.json"
    chunks_data = [chunk.to_dict() for chunk in chunks]
    with open(output_file, 'w') as f:
        json.dump(chunks_data, f, indent=2)
    
    print(f"\n💾 Chunks saved to {output_file} for detailed inspection")
    
    return chunks


if __name__ == "__main__":
    test_chunking()