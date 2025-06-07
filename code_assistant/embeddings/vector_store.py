"""Vector store for semantic code search using ChromaDB."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import logging
import uuid
import json
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np

from ..core.types import DocumentChunk, EmbeddingResult, SearchResult, SearchQuery, LanguageType
from ..core.exceptions import VectorStoreError
from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class VectorStoreConfig:
    """Configuration for vector store."""
    collection_name: str = "code_embeddings"
    persist_directory: str = "./chroma_db"
    distance_metric: str = "cosine"  # cosine, l2, ip
    max_results: int = 50
    enable_persistence: bool = True
    embedding_dimension: Optional[int] = None


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def add_embeddings(self, results: List[EmbeddingResult]) -> bool:
        """Add embeddings to the vector store."""
        pass
    
    @abstractmethod
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search for similar code chunks."""
        pass
    
    @abstractmethod
    def delete_by_file(self, file_path: Path) -> bool:
        """Delete all embeddings for a specific file."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        pass


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of vector store."""
    
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """Initialize ChromaDB vector store.
        
        Args:
            config: Vector store configuration
        """
        self.config = config or VectorStoreConfig()
        self.client = None
        self.collection = None
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            if self.config.enable_persistence:
                persist_path = Path(self.config.persist_directory)
                persist_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize client
            if self.config.enable_persistence:
                self.client = chromadb.PersistentClient(
                    path=self.config.persist_directory,
                    settings=Settings(
                        allow_reset=True,
                        anonymized_telemetry=False
                    )
                )
            else:
                self.client = chromadb.Client()
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.config.collection_name
                )
                logger.info(f"Loaded existing collection: {self.config.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.config.collection_name,
                    metadata={
                        "description": "Code embeddings for semantic search",
                        "distance_metric": self.config.distance_metric
                    }
                )
                logger.info(f"Created new collection: {self.config.collection_name}")
            
            logger.info("ChromaDB vector store initialized successfully")
            
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize ChromaDB: {e}") from e
    
    def _get_language_value(self, language: Union[LanguageType, str, None]) -> str:
        """Get string value from language, handling both enum and string types."""
        if language is None:
            return "unknown"
        elif isinstance(language, str):
            return language
        else:
            # It's an enum
            return language.value
    
    def add_embeddings(self, results: List[EmbeddingResult]) -> bool:
        """Add embeddings to ChromaDB.
        
        Args:
            results: List of embedding results to add
            
        Returns:
            True if successful, False otherwise
        """
        if not results:
            logger.warning("No embeddings to add")
            return True
        
        try:
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            documents = []
            
            for result in results:
                chunk = result.chunk
                
                # Generate unique ID
                chunk_id = self._generate_chunk_id(chunk)
                ids.append(chunk_id)
                
                # Add embedding
                embeddings.append(result.embedding)
                
                # Prepare metadata
                metadata = {
                    "file_path": str(chunk.file_path),
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "element_name": chunk.element_name or "",
                    "element_type": chunk.element_type or "",
                    "chunk_type": chunk.chunk_type or "code",
                    "language": self._get_language_value(chunk.language),
                    "model_name": result.model_name,
                    "embedding_dimension": result.embedding_dimension
                }
                
                # Add chunk-specific metadata
                if chunk.metadata:
                    # Filter metadata to only include JSON-serializable values
                    for key, value in chunk.metadata.items():
                        # Skip certain problematic keys or None values
                        if key in ['parameters', 'methods', 'dependencies'] and not value:
                            continue
                        
                        # Sanitize the value for ChromaDB
                        sanitized_value = self._sanitize_metadata_value(value)
                        
                        # Only add if the sanitized value is meaningful
                        if sanitized_value and sanitized_value not in ["null", "[]", "{}", "empty"]:
                            metadata[key] = sanitized_value
                
                metadatas.append(metadata)
                
                # Use content as document (truncate if too long)
                content = chunk.content[:1000] if len(chunk.content) > 1000 else chunk.content
                documents.append(content)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            
            logger.info(f"Added {len(results)} embeddings to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add embeddings: {e}")
            return False
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search for similar code chunks.
        
        Args:
            query: Search query with text and filters
            
        Returns:
            List of search results sorted by similarity
        """
        try:
            # Prepare where filters (ChromaDB only supports one filter at a time)
            where_clause = None
            
            # Prioritize element type filter if specified
            if query.element_types and len(query.element_types) == 1:
                where_clause = {"element_type": query.element_types[0]}
            elif query.language:
                where_clause = {"language": self._get_language_value(query.language)}
            
            # Note: file_patterns not supported in this simple implementation
            
            # Prepare query embedding if provided
            query_embedding = None
            if hasattr(query, 'embedding') and query.embedding:
                query_embedding = query.embedding
            
            # Perform search
            if query_embedding:
                # Search using embedding
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(query.max_results, self.config.max_results),
                    where=where_clause if where_clause else None,
                    include=["documents", "metadatas", "distances"]
                )
            else:
                # Search using text
                results = self.collection.query(
                    query_texts=[query.query],
                    n_results=min(query.max_results, self.config.max_results),
                    where=where_clause if where_clause else None,
                    include=["documents", "metadatas", "distances"]
                )
            
            # Convert to SearchResult objects
            search_results = []
            
            if results["ids"][0]:  # Check if we have results
                for i, chunk_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    distance = results["distances"][0][i] if "distances" in results else 0.0
                    
                    # Calculate similarity score (1 - distance for cosine similarity)
                    similarity_score = 1.0 - distance if distance else 1.0
                    
                    # Reconstruct DocumentChunk
                    chunk = DocumentChunk(
                        content=content,
                        chunk_type=metadata.get("chunk_type", "code"),
                        language=metadata.get("language", "unknown"),  # Use metadata language as string
                        file_path=Path(metadata["file_path"]),
                        start_line=metadata["start_line"],
                        end_line=metadata["end_line"],
                        element_name=metadata.get("element_name"),
                        element_type=metadata.get("element_type"),
                        metadata=metadata
                    )
                    
                    search_result = SearchResult(
                        chunk=chunk,
                        similarity_score=similarity_score,
                        distance=distance,
                        rank=i + 1
                    )
                    
                    search_results.append(search_result)
            
            # Filter by similarity threshold
            filtered_results = [r for r in search_results if r.similarity_score >= query.similarity_threshold]
            
            logger.info(f"Search returned {len(filtered_results)} results for query: {query.query[:50]}...")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreError(f"Search failed: {e}") from e
    
    def delete_by_file(self, file_path: Path) -> bool:
        """Delete all embeddings for a specific file.
        
        Args:
            file_path: Path of file to delete embeddings for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Query for chunks from this file
            results = self.collection.get(
                where={"file_path": str(file_path)},
                include=["metadatas"]
            )
            
            if results["ids"]:
                # Delete the chunks
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} embeddings for file: {file_path}")
            else:
                logger.info(f"No embeddings found for file: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embeddings for file {file_path}: {e}")
            return False
    
    def update_embeddings(self, results: List[EmbeddingResult]) -> bool:
        """Update existing embeddings or add new ones.
        
        Args:
            results: List of embedding results to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # For each result, check if it exists and update or add
            for result in results:
                chunk_id = self._generate_chunk_id(result.chunk)
                
                # Check if chunk exists
                existing = self.collection.get(
                    ids=[chunk_id],
                    include=["metadatas"]
                )
                
                if existing["ids"]:
                    # Update existing
                    self.collection.update(
                        ids=[chunk_id],
                        embeddings=[result.embedding],
                        metadatas=[self._prepare_metadata(result.chunk, result)],
                        documents=[result.chunk.content[:1000]]
                    )
                else:
                    # Add new
                    self.add_embeddings([result])
            
            logger.info(f"Updated {len(results)} embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update embeddings: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics.
        
        Returns:
            Dictionary with store statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample of metadata to analyze
            sample = self.collection.get(
                limit=min(100, count),
                include=["metadatas"]
            )
            
            # Analyze languages and element types
            languages = {}
            element_types = {}
            
            for metadata in sample["metadatas"]:
                lang = metadata.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
                
                elem_type = metadata.get("element_type", "unknown")
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            return {
                "total_chunks": count,
                "collection_name": self.config.collection_name,
                "persist_directory": self.config.persist_directory,
                "languages": languages,
                "element_types": element_types,
                "distance_metric": self.config.distance_metric
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def reset_collection(self) -> bool:
        """Reset (clear) the collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(self.config.collection_name)
            self.collection = self.client.create_collection(
                name=self.config.collection_name,
                metadata={
                    "description": "Code embeddings for semantic search",
                    "distance_metric": self.config.distance_metric
                }
            )
            logger.info(f"Reset collection: {self.config.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False
    
    def search_similar_functions(self, function_embedding: List[float], limit: int = 10) -> List[SearchResult]:
        """Search for functions similar to the given embedding.
        
        Args:
            function_embedding: Embedding vector of reference function
            limit: Maximum number of results
            
        Returns:
            List of similar functions
        """
        try:
            results = self.collection.query(
                query_embeddings=[function_embedding],
                n_results=limit,
                where={"element_type": "function"},
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            if results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    content = results["documents"][0][i]
                    distance = results["distances"][0][i]
                    
                    chunk = DocumentChunk(
                        content=content,
                        file_path=Path(metadata["file_path"]),
                        start_line=metadata["start_line"],
                        end_line=metadata["end_line"],
                        element_name=metadata.get("element_name"),
                        element_type="function",
                        metadata=metadata
                    )
                    
                    search_result = SearchResult(
                        chunk=chunk,
                        similarity_score=1.0 - distance,
                        distance=distance,
                        rank=i + 1
                    )
                    
                    search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search similar functions: {e}")
            return []
    
    def _generate_chunk_id(self, chunk: DocumentChunk) -> str:
        """Generate unique ID for a chunk."""
        # Use file path, line numbers, and element name for unique ID
        id_parts = [
            str(chunk.file_path),
            str(chunk.start_line),
            str(chunk.end_line),
            chunk.element_name or "unnamed",
            chunk.element_type or "unknown"
        ]
        
        # Create a deterministic ID
        id_string = "|".join(id_parts)
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, id_string))
    
    def _is_serializable(self, value: Any) -> bool:
        """Check if a value is JSON serializable."""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False
    
    def _sanitize_metadata_value(self, value: Any) -> Any:
        """Sanitize metadata value for ChromaDB storage."""
        if value is None:
            return "null"  # Convert None to string
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            # Convert list to string representation
            return str(value) if value else "[]"
        elif isinstance(value, dict):
            # Convert dict to string representation
            return str(value) if value else "{}"
        else:
            # Convert any other type to string
            return str(value) if value else "empty"
    
    def _prepare_metadata(self, chunk: DocumentChunk, result: EmbeddingResult) -> Dict[str, Any]:
        """Prepare metadata for storage."""
        metadata = {
            "file_path": str(chunk.file_path),
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "element_name": chunk.element_name or "",
            "element_type": chunk.element_type or "",
            "chunk_type": chunk.chunk_type or "code",
            "language": self._get_language_value(chunk.language),
            "model_name": result.model_name,
            "embedding_dimension": result.embedding_dimension
        }
        
        # Add chunk-specific metadata with proper sanitization
        if chunk.metadata:
            for key, value in chunk.metadata.items():
                # Sanitize the value for ChromaDB
                sanitized_value = self._sanitize_metadata_value(value)
                metadata[key] = sanitized_value
        
        return metadata 