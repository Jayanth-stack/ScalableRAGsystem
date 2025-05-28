"""Custom exceptions for Code Documentation Assistant."""

from typing import Optional, Any, Dict


class CodeAssistantError(Exception):
    """Base exception for Code Documentation Assistant."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ParsingError(CodeAssistantError):
    """Raised when code parsing fails."""
    
    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        language: Optional[str] = None
    ):
        super().__init__(
            message, 
            error_code="PARSING_ERROR",
            details={
                "file_path": file_path,
                "line_number": line_number,
                "language": language
            }
        )
        self.file_path = file_path
        self.line_number = line_number
        self.language = language


class AnalysisError(CodeAssistantError):
    """Raised when code analysis fails."""
    
    def __init__(
        self, 
        message: str, 
        analysis_type: Optional[str] = None,
        file_path: Optional[str] = None
    ):
        super().__init__(
            message,
            error_code="ANALYSIS_ERROR", 
            details={
                "analysis_type": analysis_type,
                "file_path": file_path
            }
        )
        self.analysis_type = analysis_type
        self.file_path = file_path


class EmbeddingError(CodeAssistantError):
    """Raised when embedding generation fails."""
    
    def __init__(self, message: str, model_name: Optional[str] = None):
        super().__init__(
            message,
            error_code="EMBEDDING_ERROR",
            details={"model_name": model_name}
        )
        self.model_name = model_name


class VectorStoreError(CodeAssistantError):
    """Raised when vector store operations fail."""
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        store_type: Optional[str] = None
    ):
        super().__init__(
            message,
            error_code="VECTOR_STORE_ERROR",
            details={
                "operation": operation,
                "store_type": store_type
            }
        )
        self.operation = operation
        self.store_type = store_type


class GitError(CodeAssistantError):
    """Raised when Git operations fail."""
    
    def __init__(
        self, 
        message: str, 
        repository_url: Optional[str] = None,
        operation: Optional[str] = None
    ):
        super().__init__(
            message,
            error_code="GIT_ERROR",
            details={
                "repository_url": repository_url,
                "operation": operation
            }
        )
        self.repository_url = repository_url
        self.operation = operation


class ConfigurationError(CodeAssistantError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            details={"config_key": config_key}
        )
        self.config_key = config_key


class RateLimitError(CodeAssistantError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(
        self, 
        message: str, 
        service: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            details={
                "service": service,
                "retry_after": retry_after
            }
        )
        self.service = service
        self.retry_after = retry_after 