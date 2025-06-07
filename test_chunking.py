"""Test script for intelligent code chunking and embedding."""

import sys
from pathlib import Path
import asyncio

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from code_assistant.embeddings.chunker import CodeChunker, ChunkingStrategy, ChunkingConfig
from code_assistant.embeddings.embedder import CodeEmbedder, EmbeddingModel, EmbeddingConfig


def test_code_chunking():
    """Test intelligent code chunking on our sample files."""
    print("🧩 Testing Intelligent Code Chunking...")
    
    # Test different chunking strategies
    strategies = [
        (ChunkingStrategy.FUNCTION_BASED, "Function-based chunking"),
        (ChunkingStrategy.HYBRID, "Hybrid chunking"),
        (ChunkingStrategy.SEMANTIC_BLOCKS, "Semantic blocks chunking")
    ]
    
    sample_file = Path("sample_repos/sample_python_project/main.py")
    
    if not sample_file.exists():
        print(f"⚠️  Sample file not found: {sample_file}")
        return
    
    for strategy, description in strategies:
        print(f"\n📋 {description}:")
        
        # Configure chunker
        config = ChunkingConfig(
            strategy=strategy,
            max_chunk_size=800,
            min_chunk_size=50,
            include_context=True,
            include_docstrings=True
        )
        
        chunker = CodeChunker(config)
        
        try:
            chunks = chunker.chunk_file(sample_file)
            print(f"   ✅ Created {len(chunks)} chunks")
            
            # Show chunk details
            for i, chunk in enumerate(chunks[:3], 1):  # Show first 3 chunks
                print(f"   📦 Chunk {i}:")
                print(f"      - Element: {chunk.element_name} ({chunk.element_type})")
                print(f"      - Lines: {chunk.start_line}-{chunk.end_line}")
                print(f"      - Size: {len(chunk.content)} chars")
                print(f"      - Type: {chunk.chunk_type}")
                
                # Show metadata highlights
                if chunk.metadata:
                    if 'function_name' in chunk.metadata:
                        complexity = chunk.metadata.get('complexity_score', 'N/A')
                        params = chunk.metadata.get('parameters', [])
                        print(f"      - Function: {chunk.metadata['function_name']}")
                        print(f"      - Complexity: {complexity}")
                        print(f"      - Parameters: {len(params) if params else 0}")
                    
                    elif 'class_name' in chunk.metadata:
                        inheritance = chunk.metadata.get('inheritance', [])
                        methods = chunk.metadata.get('methods', [])
                        print(f"      - Class: {chunk.metadata['class_name']}")
                        print(f"      - Inheritance: {', '.join(inheritance) if inheritance else 'None'}")
                        print(f"      - Methods: {len(methods) if methods else 0}")
                
                # Show a snippet of the content
                content_preview = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
                print(f"      - Preview: {repr(content_preview)}")
                print()
            
            if len(chunks) > 3:
                print(f"   ... and {len(chunks) - 3} more chunks")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_embedding_models():
    """Test different embedding models."""
    print("\n🔢 Testing Embedding Models...")
    
    # Test with a simple code chunk
    from code_assistant.core.types import DocumentChunk, LanguageType
    
    test_chunk = DocumentChunk(
        content='''def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    Args:
        n: Position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)''',
        chunk_type="code",
        language=LanguageType.PYTHON,
        file_path=Path("test.py"),
        start_line=1,
        end_line=12,
        element_name="calculate_fibonacci",
        element_type="function",
        metadata={
            "function_name": "calculate_fibonacci",
            "parameters": [{"name": "n", "type": "int"}],
            "return_type": "int",
            "complexity_score": 3.0
        }
    )
    
    # Test different models (fallback to sentence transformer if others fail)
    models = [
        (EmbeddingModel.SENTENCE_TRANSFORMER, "Sentence Transformer"),
        # (EmbeddingModel.GOOGLE_EMBEDDING, "Google Embedding"),  # Uncomment if API key is valid
        # (EmbeddingModel.CODEBERT, "CodeBERT"),  # Uncomment to test
    ]
    
    for model, model_name in models:
        print(f"\n🤖 Testing {model_name}:")
        
        try:
            config = EmbeddingConfig(
                model=model,
                include_metadata=True,
                normalize_embeddings=True
            )
            
            embedder = CodeEmbedder(config)
            
            # Generate embedding
            result = embedder.embed_chunk(test_chunk)
            
            print(f"   ✅ Generated embedding")
            print(f"   📊 Model: {result.model_name}")
            print(f"   📐 Dimension: {result.embedding_dimension}")
            print(f"   🎯 First 5 values: {result.embedding[:5]}")
            
            # Show embedding stats
            stats = embedder.get_embedding_stats()
            print(f"   📈 Stats: {stats}")
            
        except Exception as e:
            print(f"   ❌ Error with {model_name}: {e}")


def test_full_pipeline():
    """Test the complete chunking + embedding pipeline."""
    print("\n🔄 Testing Full Pipeline (Chunking + Embedding)...")
    
    sample_file = Path("sample_repos/sample_python_project/utils.py")
    
    if not sample_file.exists():
        print(f"⚠️  Sample file not found: {sample_file}")
        return
    
    try:
        # Step 1: Chunk the file
        print("   📋 Step 1: Chunking file...")
        chunker_config = ChunkingConfig(
            strategy=ChunkingStrategy.FUNCTION_BASED,
            max_chunk_size=600,
            include_context=False,  # Keep chunks focused
            include_docstrings=True
        )
        
        chunker = CodeChunker(chunker_config)
        chunks = chunker.chunk_file(sample_file)
        
        print(f"      ✅ Created {len(chunks)} chunks")
        
        # Step 2: Generate embeddings
        print("   🔢 Step 2: Generating embeddings...")
        embedder_config = EmbeddingConfig(
            model=EmbeddingModel.SENTENCE_TRANSFORMER,  # Safe fallback
            batch_size=10,
            include_metadata=True
        )
        
        embedder = CodeEmbedder(embedder_config)
        
        # Take a sample of chunks to avoid overwhelming the test
        sample_chunks = chunks[:5]  # First 5 chunks
        print(f"      📦 Processing {len(sample_chunks)} sample chunks...")
        
        embedding_results = embedder.embed_chunks_batch(sample_chunks)
        
        print(f"      ✅ Generated {len(embedding_results)} embeddings")
        
        # Step 3: Show results
        print("   📊 Step 3: Results summary...")
        for i, result in enumerate(embedding_results, 1):
            chunk = result.chunk
            print(f"      🔸 Embedding {i}:")
            print(f"         - Element: {chunk.element_name}")
            print(f"         - Type: {chunk.element_type}")
            print(f"         - Size: {len(chunk.content)} chars")
            print(f"         - Embedding dim: {result.embedding_dimension}")
            print(f"         - Vector norm: {sum(x*x for x in result.embedding)**0.5:.3f}")
            
            # Show how the text was prepared for embedding
            embedding_text = embedder._prepare_text_for_embedding(chunk)
            preview = embedding_text[:200] + "..." if len(embedding_text) > 200 else embedding_text
            print(f"         - Text preview: {repr(preview)}")
            print()
        
        # Step 4: Test saving/loading embeddings
        print("   💾 Step 4: Testing save/load...")
        output_path = Path("test_embeddings.pkl")
        
        embedder.save_embeddings(embedding_results, output_path)
        loaded_results = embedder.load_embeddings(output_path)
        
        print(f"      ✅ Saved and loaded {len(loaded_results)} embeddings")
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
        
        print("   🎉 Full pipeline test completed successfully!")
        
    except Exception as e:
        print(f"   ❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()


async def test_async_embedding():
    """Test async embedding for better performance."""
    print("\n⚡ Testing Async Embedding...")
    
    try:
        # Create some test chunks
        from code_assistant.core.types import DocumentChunk, LanguageType
        
        test_chunks = []
        for i in range(3):
            chunk = DocumentChunk(
                content=f'''def test_function_{i}():
    """Test function number {i}."""
    return {i} * 2''',
                chunk_type="code",
                language=LanguageType.PYTHON,
                file_path=Path(f"test_{i}.py"),
                start_line=1,
                end_line=3,
                element_name=f"test_function_{i}",
                element_type="function"
            )
            test_chunks.append(chunk)
        
        # Test async embedding
        config = EmbeddingConfig(model=EmbeddingModel.SENTENCE_TRANSFORMER)
        embedder = CodeEmbedder(config)
        
        start_time = asyncio.get_event_loop().time()
        results = await embedder.embed_chunks_async(test_chunks)
        end_time = asyncio.get_event_loop().time()
        
        print(f"   ✅ Async embedding completed in {end_time - start_time:.2f} seconds")
        print(f"   📊 Generated {len(results)} embeddings")
        
        for result in results:
            print(f"      - {result.chunk.element_name}: {result.embedding_dimension}D vector")
        
    except Exception as e:
        print(f"   ❌ Async embedding error: {e}")


def main():
    """Run all tests."""
    print("🚀 Starting Enhanced RAG Features Tests\n")
    
    try:
        test_code_chunking()
        test_embedding_models()
        test_full_pipeline()
        
        # Test async functionality
        print("\n" + "="*50)
        asyncio.run(test_async_embedding())
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 