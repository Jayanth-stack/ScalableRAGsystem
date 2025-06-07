"""Code embedding generation using multiple models."""

from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import logging
import time
from dataclasses import dataclass
import asyncio

import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from ..core.types import DocumentChunk, EmbeddingResult, LanguageType
from ..core.config import settings
from ..core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingModel(Enum):
    """Available embedding models."""
    GOOGLE_EMBEDDING = "google_embedding"  # Google's text-embedding-004
    CODEBERT = "codebert"  # Microsoft CodeBERT
    SENTENCE_TRANSFORMER = "sentence_transformer"  # General sentence transformer
    CODET5 = "codet5"  # CodeT5 for code understanding
    UNIXCODER = "unixcoder"  # UniXcoder for multilingual code


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model: EmbeddingModel = EmbeddingModel.GOOGLE_EMBEDDING
    batch_size: int = 32
    max_retries: int = 3
    retry_delay: float = 1.0
    normalize_embeddings: bool = True
    include_metadata: bool = True
    cache_embeddings: bool = True
    context_window: int = 512  # Max tokens for context


class CodeEmbedder:
    """Generate embeddings for code chunks using various models."""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """Initialize the code embedder.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        self.model = None
        self.model_name = None
        self.embedding_dimension = None
        self._cache = {}
        
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the embedding model."""
        try:
            if self.config.model == EmbeddingModel.GOOGLE_EMBEDDING:
                genai.configure(api_key=settings.google_api_key)
                self.model_name = "models/text-embedding-004"
                self.embedding_dimension = 768
                logger.info("Initialized Google Embedding model")
                
            elif self.config.model == EmbeddingModel.CODEBERT:
                self.model = SentenceTransformer('microsoft/codebert-base')
                self.model_name = "microsoft/codebert-base"
                self.embedding_dimension = 768
                logger.info("Initialized CodeBERT model")
                
            elif self.config.model == EmbeddingModel.SENTENCE_TRANSFORMER:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.model_name = "all-MiniLM-L6-v2"
                self.embedding_dimension = 384
                logger.info("Initialized Sentence Transformer model")
                
            elif self.config.model == EmbeddingModel.CODET5:
                self.model = SentenceTransformer('Salesforce/codet5-base')
                self.model_name = "Salesforce/codet5-base"
                self.embedding_dimension = 768
                logger.info("Initialized CodeT5 model")
                
            elif self.config.model == EmbeddingModel.UNIXCODER:
                self.model = SentenceTransformer('microsoft/unixcoder-base')
                self.model_name = "microsoft/unixcoder-base"
                self.embedding_dimension = 768
                logger.info("Initialized UniXcoder model")
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            # Fallback to sentence transformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_name = "all-MiniLM-L6-v2"
            self.embedding_dimension = 384
            logger.info("Fell back to Sentence Transformer model")
    
    def embed_chunk(self, chunk: DocumentChunk) -> EmbeddingResult:
        """Generate embedding for a single code chunk.
        
        Args:
            chunk: Document chunk to embed
            
        Returns:
            Embedding result with vector and metadata
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(chunk)
            if self.config.cache_embeddings and cache_key in self._cache:
                cached_result = self._cache[cache_key]
                logger.debug(f"Using cached embedding for {chunk.element_name}")
                return cached_result
            
            # Prepare text for embedding
            embedding_text = self._prepare_text_for_embedding(chunk)
            
            # Generate embedding
            embedding = self._generate_embedding(embedding_text)
            
            # Normalize if configured
            if self.config.normalize_embeddings:
                embedding = self._normalize_embedding(embedding)
            
            # Create result
            result = EmbeddingResult(
                chunk=chunk,
                embedding=embedding,
                model_name=self.model_name,
                embedding_dimension=len(embedding)
            )
            
            # Cache result
            if self.config.cache_embeddings:
                self._cache[cache_key] = result
            
            return result
            
        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embedding for chunk {chunk.element_name}",
                chunk_info=str(chunk.file_path)
            ) from e
    
    def embed_chunks_batch(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Generate embeddings for multiple chunks in batches.
        
        Args:
            chunks: List of document chunks to embed
            
        Returns:
            List of embedding results
        """
        results = []
        
        # Process in batches
        for i in range(0, len(chunks), self.config.batch_size):
            batch = chunks[i:i + self.config.batch_size]
            
            try:
                batch_results = self._process_batch(batch)
                results.extend(batch_results)
                
                logger.info(f"Processed batch {i//self.config.batch_size + 1}/{(len(chunks) - 1)//self.config.batch_size + 1}")
                
                # Small delay to avoid rate limiting
                if self.config.model == EmbeddingModel.GOOGLE_EMBEDDING:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error processing batch {i//self.config.batch_size + 1}: {e}")
                # Process individually as fallback
                for chunk in batch:
                    try:
                        result = self.embed_chunk(chunk)
                        results.append(result)
                    except Exception as chunk_error:
                        logger.error(f"Failed to embed chunk {chunk.element_name}: {chunk_error}")
        
        logger.info(f"Generated {len(results)} embeddings from {len(chunks)} chunks")
        return results
    
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Generate embeddings asynchronously for better performance.
        
        Args:
            chunks: List of document chunks to embed
            
        Returns:
            List of embedding results
        """
        semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
        
        async def embed_single_chunk(chunk: DocumentChunk) -> Optional[EmbeddingResult]:
            async with semaphore:
                try:
                    return await asyncio.to_thread(self.embed_chunk, chunk)
                except Exception as e:
                    logger.error(f"Async embedding failed for {chunk.element_name}: {e}")
                    return None
        
        # Create tasks for all chunks
        tasks = [embed_single_chunk(chunk) for chunk in chunks]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = [r for r in results if isinstance(r, EmbeddingResult)]
        
        logger.info(f"Async embedding completed: {len(valid_results)}/{len(chunks)} successful")
        return valid_results
    
    def _process_batch(self, batch: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process a batch of chunks for embedding."""
        if self.config.model == EmbeddingModel.GOOGLE_EMBEDDING:
            return self._process_google_batch(batch)
        else:
            return self._process_transformer_batch(batch)
    
    def _process_google_batch(self, batch: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process batch using Google Embedding API."""
        results = []
        
        for chunk in batch:
            retries = 0
            while retries < self.config.max_retries:
                try:
                    embedding_text = self._prepare_text_for_embedding(chunk)
                    
                    # Call Google Embedding API
                    response = genai.embed_content(
                        model="models/text-embedding-004",
                        content=embedding_text,
                        task_type="retrieval_document"
                    )
                    
                    embedding = response['embedding']
                    
                    if self.config.normalize_embeddings:
                        embedding = self._normalize_embedding(embedding)
                    
                    result = EmbeddingResult(
                        chunk=chunk,
                        embedding=embedding,
                        model_name=self.model_name,
                        embedding_dimension=len(embedding)
                    )
                    
                    results.append(result)
                    break
                    
                except Exception as e:
                    retries += 1
                    if retries < self.config.max_retries:
                        logger.warning(f"Retry {retries} for chunk {chunk.element_name}: {e}")
                        time.sleep(self.config.retry_delay * retries)
                    else:
                        logger.error(f"Failed to embed chunk {chunk.element_name} after {self.config.max_retries} retries: {e}")
        
        return results
    
    def _process_transformer_batch(self, batch: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process batch using Sentence Transformer models."""
        results = []
        
        # Prepare texts
        texts = [self._prepare_text_for_embedding(chunk) for chunk in batch]
        
        try:
            # Generate embeddings in batch
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Create results
            for chunk, embedding in zip(batch, embeddings):
                if self.config.normalize_embeddings:
                    embedding = self._normalize_embedding(embedding.tolist())
                else:
                    embedding = embedding.tolist()
                
                result = EmbeddingResult(
                    chunk=chunk,
                    embedding=embedding,
                    model_name=self.model_name,
                    embedding_dimension=len(embedding)
                )
                
                results.append(result)
                
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            # Fall back to individual processing
            for chunk in batch:
                try:
                    result = self.embed_chunk(chunk)
                    results.append(result)
                except Exception as chunk_error:
                    logger.error(f"Individual embedding failed for {chunk.element_name}: {chunk_error}")
        
        return results
    
    def _prepare_text_for_embedding(self, chunk: DocumentChunk) -> str:
        """Prepare chunk text for embedding with context and metadata.
        
        Args:
            chunk: Document chunk to prepare
            
        Returns:
            Formatted text ready for embedding
        """
        parts = []
        
        # Add language and type context
        if chunk.language:
            parts.append(f"Language: {chunk.language}")
        
        if chunk.element_type:
            parts.append(f"Type: {chunk.element_type}")
        
        if chunk.element_name:
            parts.append(f"Name: {chunk.element_name}")
        
        # Add metadata context if enabled
        if self.config.include_metadata and chunk.metadata:
            metadata_parts = []
            
            # Function/method specific metadata
            if chunk.element_type in ['function', 'method']:
                if 'parameters' in chunk.metadata:
                    params = chunk.metadata['parameters']
                    if params:
                        param_names = [p.get('name', '') for p in params if isinstance(p, dict)]
                        metadata_parts.append(f"Parameters: {', '.join(param_names)}")
                
                if 'return_type' in chunk.metadata and chunk.metadata['return_type']:
                    metadata_parts.append(f"Returns: {chunk.metadata['return_type']}")
                
                if 'complexity_score' in chunk.metadata and chunk.metadata['complexity_score']:
                    metadata_parts.append(f"Complexity: {chunk.metadata['complexity_score']}")
            
            # Class specific metadata
            elif chunk.element_type == 'class':
                if 'inheritance' in chunk.metadata and chunk.metadata['inheritance']:
                    metadata_parts.append(f"Inherits: {', '.join(chunk.metadata['inheritance'])}")
                
                if 'methods' in chunk.metadata and chunk.metadata['methods']:
                    metadata_parts.append(f"Methods: {', '.join(chunk.metadata['methods'])}")
            
            if metadata_parts:
                parts.extend(metadata_parts)
        
        # Add the actual code content
        parts.append("Code:")
        parts.append(chunk.content)
        
        # Join with newlines and truncate if necessary
        full_text = '\n'.join(parts)
        
        # Truncate if too long (rough token estimation: 4 chars per token)
        max_chars = self.config.context_window * 4
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "..."
        
        return full_text
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the configured model."""
        if self.config.model == EmbeddingModel.GOOGLE_EMBEDDING:
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return response['embedding']
        else:
            # Use sentence transformer
            embedding = self.model.encode([text], convert_to_numpy=True)[0]
            return embedding.tolist()
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """Normalize embedding to unit vector."""
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        if norm > 0:
            return (embedding_array / norm).tolist()
        return embedding
    
    def _get_cache_key(self, chunk: DocumentChunk) -> str:
        """Generate cache key for a chunk."""
        key_parts = [
            str(chunk.file_path),
            str(chunk.start_line),
            str(chunk.end_line),
            chunk.element_name or "",
            self.model_name,
            str(hash(chunk.content))
        ]
        return "|".join(key_parts)
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about embedding generation."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "cache_size": len(self._cache),
            "config": {
                "model": self.config.model.value,
                "batch_size": self.config.batch_size,
                "normalize_embeddings": self.config.normalize_embeddings,
                "include_metadata": self.config.include_metadata
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")
    
    def save_embeddings(self, results: List[EmbeddingResult], output_path: Path) -> None:
        """Save embeddings to file for later use.
        
        Args:
            results: List of embedding results
            output_path: Path to save embeddings
        """
        try:
            import pickle
            
            embedding_data = {
                "model_name": self.model_name,
                "embedding_dimension": self.embedding_dimension,
                "embeddings": [
                    {
                        "file_path": str(result.chunk.file_path),
                        "element_name": result.chunk.element_name,
                        "start_line": result.chunk.start_line,
                        "end_line": result.chunk.end_line,
                        "embedding": result.embedding,
                        "metadata": result.chunk.metadata
                    }
                    for result in results
                ]
            }
            
            with open(output_path, 'wb') as f:
                pickle.dump(embedding_data, f)
            
            logger.info(f"Saved {len(results)} embeddings to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
    
    def load_embeddings(self, input_path: Path) -> List[EmbeddingResult]:
        """Load embeddings from file.
        
        Args:
            input_path: Path to load embeddings from
            
        Returns:
            List of embedding results
        """
        try:
            import pickle
            
            with open(input_path, 'rb') as f:
                embedding_data = pickle.load(f)
            
            results = []
            for item in embedding_data["embeddings"]:
                # Reconstruct DocumentChunk
                chunk = DocumentChunk(
                    content="",  # Content not saved to reduce size
                    file_path=Path(item["file_path"]),
                    start_line=item["start_line"],
                    end_line=item["end_line"],
                    element_name=item["element_name"],
                    metadata=item["metadata"]
                )
                
                # Create EmbeddingResult
                result = EmbeddingResult(
                    chunk=chunk,
                    embedding=item["embedding"],
                    model_name=embedding_data["model_name"],
                    embedding_dimension=embedding_data["embedding_dimension"]
                )
                
                results.append(result)
            
            logger.info(f"Loaded {len(results)} embeddings from {input_path}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return [] 