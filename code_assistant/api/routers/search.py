"""Search API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List
import time

from ..models import SearchRequest, SearchResponse
from ...embeddings.vector_store import ChromaVectorStore, VectorStoreConfig
from ...core.types import SearchQuery

router = APIRouter()

# Initialize vector store
vector_config = VectorStoreConfig(
    collection_name="code_embeddings",
    persist_directory="./chroma_db"
)
vector_store = ChromaVectorStore(vector_config)

@router.post("/", response_model=SearchResponse)
async def search_code(request: SearchRequest):
    """Search for code using semantic similarity."""
    start_time = time.time()
    
    try:
        # Create search query
        query = SearchQuery(
            query=request.query,
            language=request.language,
            element_types=request.element_types,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold
        )
        
        # Perform search
        results = vector_store.search(query)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "chunk": result.chunk.dict(),
                "similarity_score": result.similarity_score,
                "rank": result.rank
            })
        
        query_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=formatted_results,
            total_results=len(results),
            query_time_ms=query_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_search_stats():
    """Get search index statistics."""
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 