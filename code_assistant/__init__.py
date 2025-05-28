"""
Code Documentation Assistant

A sophisticated RAG-based system for analyzing, documenting, and understanding codebases.
Supports multiple programming languages with AST parsing, semantic analysis, and AI-powered insights.
"""

__version__ = "1.0.0"
__author__ = "Code Assistant Team"

from .core.config import Settings
from .core.exceptions import CodeAssistantError

__all__ = ["Settings", "CodeAssistantError"] 