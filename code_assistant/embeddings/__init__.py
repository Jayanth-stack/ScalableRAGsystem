"""Embedding and chunking functionality for the Code Documentation Assistant."""

from .chunker import CodeChunker, ChunkingStrategy
from .embedder import CodeEmbedder, EmbeddingModel
from .vector_store import VectorStore, ChromaVectorStore, VectorStoreConfig

__all__ = [
    "CodeChunker",
    "ChunkingStrategy", 
    "CodeEmbedder",
    "EmbeddingModel",
    "VectorStore",
    "ChromaVectorStore",
    "VectorStoreConfig"
] 