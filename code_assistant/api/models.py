"""API request and response models."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path

from ..core.types import LanguageType, CodeElementType, AnalysisType

class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    target: str = Field(..., description="File path or repository URL")
    analysis_types: List[str] = Field(
        default=["complexity", "dependency", "pattern"],
        description="Types of analysis to perform"
    )
    language: Optional[LanguageType] = None
    async_mode: bool = Field(default=True, description="Run analysis asynchronously")

class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    task_id: str
    status: str
    created_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SearchRequest(BaseModel):
    """Request model for code search."""
    query: str = Field(..., description="Search query")
    language: Optional[LanguageType] = None
    element_types: List[CodeElementType] = Field(default_factory=list)
    max_results: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SearchResponse(BaseModel):
    """Response model for search results."""
    results: List[Dict[str, Any]]
    total_results: int
    query_time_ms: float

class DocumentationRequest(BaseModel):
    """Request model for documentation generation."""
    target: str = Field(..., description="Code element or file path")
    doc_type: str = Field(default="function", description="Type of documentation")
    style: str = Field(default="google", description="Documentation style")
    include_examples: bool = True

class DocumentationResponse(BaseModel):
    """Response model for generated documentation."""
    documentation: str
    confidence_score: float
    suggestions: List[str]

class MetricsRequest(BaseModel):
    """Request model for code metrics."""
    target: str = Field(..., description="File or project path")
    metric_types: List[str] = Field(
        default=["complexity", "quality", "coverage"],
        description="Types of metrics to calculate"
    )

class MetricsResponse(BaseModel):
    """Response model for code metrics."""
    metrics: Dict[str, Any]
    timestamp: datetime
    file_count: int
    total_lines: int

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)

class TaskStatusResponse(BaseModel):
    """Response for task status queries."""
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime 