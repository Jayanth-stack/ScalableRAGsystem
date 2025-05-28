"""Configuration management for Code Documentation Assistant."""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # === API Configuration ===
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    
    # === Application Settings ===
    app_name: str = "Code Documentation Assistant"
    app_version: str = "1.0.0"
    debug: bool = Field(False, env="DEBUG")
    
    # === Database Configuration ===
    database_url: str = Field("sqlite:///./code_assistant.db", env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # === Vector Store Configuration ===
    chroma_persist_directory: str = "./chroma_db"
    pinecone_environment: Optional[str] = Field(None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = "code-assistant"
    
    # === Embedding Configuration ===
    embedding_model: str = "models/embedding-001"  # Google's embedding model
    code_embedding_model: str = "microsoft/codebert-base"
    embedding_dimension: int = 768
    
    # === LLM Configuration ===
    primary_llm_model: str = "models/gemini-1.5-pro"
    code_llm_model: str = "models/gemini-1.5-pro"
    llm_temperature: float = 0.1
    max_tokens: int = 4096
    
    # === Code Analysis Configuration ===
    supported_languages: List[str] = [
        "python", "javascript", "typescript", "java", 
        "go", "rust", "cpp", "c", "csharp", "php"
    ]
    max_file_size_mb: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # === Processing Configuration ===
    max_concurrent_files: int = 10
    analysis_timeout_seconds: int = 300
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    
    # === Directory Configuration ===
    base_directory: Path = Field(default_factory=lambda: Path.cwd())
    temp_directory: str = "./temp"
    logs_directory: str = "./logs"
    
    # === Git Configuration ===
    git_clone_depth: int = 1
    ignore_patterns: List[str] = [
        "*.pyc", "__pycache__", ".git", "node_modules", 
        ".venv", "venv", "*.log", ".DS_Store"
    ]
    
    @validator("base_directory", pre=True)
    def validate_base_directory(cls, v):
        """Ensure base directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("supported_languages")
    def validate_languages(cls, v):
        """Ensure supported languages are lowercase."""
        return [lang.lower() for lang in v]
    
    def get_language_extensions(self) -> Dict[str, List[str]]:
        """Get file extensions for supported languages."""
        return {
            "python": [".py", ".pyx", ".pyi"],
            "javascript": [".js", ".jsx", ".mjs"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "go": [".go"],
            "rust": [".rs"],
            "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
            "c": [".c", ".h"],
            "csharp": [".cs"],
            "php": [".php"]
        }
    
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if a file is supported for analysis."""
        extensions = self.get_language_extensions()
        file_ext = file_path.suffix.lower()
        
        for lang_extensions in extensions.values():
            if file_ext in lang_extensions:
                return True
        return False
    
    def get_file_language(self, file_path: Path) -> Optional[str]:
        """Determine the programming language of a file."""
        extensions = self.get_language_extensions()
        file_ext = file_path.suffix.lower()
        
        for language, lang_extensions in extensions.items():
            if file_ext in lang_extensions:
                return language
        return None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 