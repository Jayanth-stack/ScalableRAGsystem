"""Type definitions and data models for Code Documentation Assistant."""

from typing import List, Dict, Optional, Any, Union, Literal
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class LanguageType(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    CSHARP = "csharp"
    PHP = "php"


class CodeElementType(str, Enum):
    """Types of code elements that can be extracted."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    MODULE = "module"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"
    NAMESPACE = "namespace"
    DECORATOR = "decorator"
    COMMENT = "comment"
    DOCSTRING = "docstring"


class AnalysisType(str, Enum):
    """Types of analysis that can be performed."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    DEPENDENCY = "dependency"
    COMPLEXITY = "complexity"
    QUALITY = "quality"
    SECURITY = "security"
    DOCUMENTATION = "documentation"


class FileInfo(BaseModel):
    """Information about a source code file."""
    
    path: Path
    name: str
    extension: str
    language: Optional[LanguageType] = None
    size_bytes: int
    lines_count: int
    created_at: datetime
    modified_at: datetime
    git_hash: Optional[str] = None
    encoding: str = "utf-8"
    
    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    @field_validator("language", mode="before")
    @classmethod
    def infer_language(cls, v, info):
        if v is None and "extension" in info.data:
            ext = info.data["extension"].lower()
            language_map = {
                ".py": LanguageType.PYTHON,
                ".js": LanguageType.JAVASCRIPT,
                ".jsx": LanguageType.JAVASCRIPT,
                ".ts": LanguageType.TYPESCRIPT,
                ".tsx": LanguageType.TYPESCRIPT,
                ".java": LanguageType.JAVA,
                ".go": LanguageType.GO,
                ".rs": LanguageType.RUST,
                ".cpp": LanguageType.CPP,
                ".cc": LanguageType.CPP,
                ".cxx": LanguageType.CPP,
                ".c": LanguageType.C,
                ".cs": LanguageType.CSHARP,
                ".php": LanguageType.PHP,
            }
            return language_map.get(ext)
        return v
    
    class Config:
        use_enum_values = True


class CodeElement(BaseModel):
    """Represents a code element (function, class, variable, etc.)."""
    
    name: str
    element_type: CodeElementType
    language: LanguageType
    file_path: Path
    start_line: int
    end_line: int
    start_column: int = 0
    end_column: int = 0
    content: str
    signature: Optional[str] = None
    docstring: Optional[str] = None
    comments: List[str] = Field(default_factory=list)
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    modifiers: List[str] = Field(default_factory=list)  # public, private, static, etc.
    parent_element: Optional[str] = None  # For methods in classes
    children: List[str] = Field(default_factory=list)  # For classes with methods
    dependencies: List[str] = Field(default_factory=list)  # Imported modules/functions
    complexity_score: Optional[float] = None
    
    @field_validator("file_path", mode="before")
    @classmethod
    def validate_file_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    class Config:
        use_enum_values = True


class AnalysisResult(BaseModel):
    """Result of code analysis."""
    
    file_info: FileInfo
    analysis_type: AnalysisType
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    
    # Analysis results
    code_elements: List[CodeElement] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    # Metadata
    processing_time_ms: Optional[float] = None
    parser_version: Optional[str] = None
    
    class Config:
        use_enum_values = True


class DocumentChunk(BaseModel):
    """A chunk of code or documentation for embedding."""
    
    content: str
    chunk_type: Literal["code", "comment", "docstring", "documentation"] = "code"
    language: Optional[LanguageType] = None
    file_path: Path
    start_line: int
    end_line: int
    element_name: Optional[str] = None  # Function/class name if applicable
    element_type: Optional[CodeElementType] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("file_path", mode="before")
    @classmethod
    def validate_file_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    class Config:
        use_enum_values = True


class EmbeddingResult(BaseModel):
    """Result of embedding generation."""
    
    chunk: DocumentChunk
    embedding: List[float]
    model_name: str
    embedding_dimension: int
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class SearchQuery(BaseModel):
    """Search query for code retrieval."""
    
    query: str
    language: Optional[LanguageType] = None
    element_types: List[CodeElementType] = Field(default_factory=list)
    file_patterns: List[str] = Field(default_factory=list)
    max_results: int = 10
    similarity_threshold: float = 0.7
    include_metadata: bool = True
    
    class Config:
        use_enum_values = True


class SearchResult(BaseModel):
    """Result of a search query."""
    
    chunk: DocumentChunk
    similarity_score: float
    rank: int
    explanation: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class RepositoryInfo(BaseModel):
    """Information about a code repository."""
    
    name: str
    path: Path
    url: Optional[str] = None
    branch: str = "main"
    commit_hash: Optional[str] = None
    languages: List[LanguageType] = Field(default_factory=list)
    file_count: int = 0
    total_lines: int = 0
    last_analyzed: Optional[datetime] = None
    
    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    class Config:
        use_enum_values = True


class DocumentationRequest(BaseModel):
    """Request for documentation generation."""
    
    target: Union[Path, str]  # File path or code element name
    doc_type: Literal["function", "class", "module", "api", "readme"] = "function"
    language: Optional[LanguageType] = None
    include_examples: bool = True
    include_parameters: bool = True
    include_return_type: bool = True
    style: Literal["google", "numpy", "sphinx", "markdown"] = "google"
    
    @field_validator("target", mode="before")
    @classmethod
    def validate_target(cls, v):
        if isinstance(v, str) and (v.startswith("/") or "\\" in v):
            return Path(v)
        return v
    
    class Config:
        use_enum_values = True


class DocumentationResult(BaseModel):
    """Result of documentation generation."""
    
    request: DocumentationRequest
    generated_docs: str
    confidence_score: float
    suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class APIEndpoint(BaseModel):
    """Represents an API endpoint discovered in code."""
    
    path: str
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    function_name: str
    file_path: Path
    line_number: int
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    response_type: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    @field_validator("file_path", mode="before")
    @classmethod
    def validate_file_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


class CodeQualityMetrics(BaseModel):
    """Code quality metrics for a file or project."""
    
    cyclomatic_complexity: float
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float
    duplication_ratio: float
    test_coverage: Optional[float] = None
    security_score: Optional[float] = None
    documentation_coverage: float
    
    def overall_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        scores = [
            min(100, max(0, 100 - (self.cyclomatic_complexity - 1) * 10)),
            self.maintainability_index,
            min(100, self.comment_ratio * 100),
            min(100, (1 - self.duplication_ratio) * 100),
            self.documentation_coverage * 100
        ]
        
        if self.test_coverage is not None:
            scores.append(self.test_coverage)
        if self.security_score is not None:
            scores.append(self.security_score)
            
        return sum(scores) / len(scores) 