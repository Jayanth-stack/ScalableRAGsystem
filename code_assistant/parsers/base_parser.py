"""Abstract base parser for code analysis."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.types import CodeElement, FileInfo, LanguageType, AnalysisResult
from ..core.exceptions import ParsingError


class BaseParser(ABC):
    """Abstract base class for all code parsers."""
    
    def __init__(self, language: LanguageType):
        """Initialize parser for specific language.
        
        Args:
            language: Programming language this parser handles
        """
        self.language = language
        self._setup_parser()
    
    @abstractmethod
    def _setup_parser(self) -> None:
        """Setup language-specific parser components."""
        pass
    
    @abstractmethod
    def parse_file(self, file_path: Path) -> AnalysisResult:
        """Parse a single file and extract code elements.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            AnalysisResult containing extracted code elements
            
        Raises:
            ParsingError: If parsing fails
        """
        pass
    
    @abstractmethod
    def parse_content(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Parse code content string and extract elements.
        
        Args:
            content: Source code content
            file_path: Optional file path for context
            
        Returns:
            List of extracted code elements
            
        Raises:
            ParsingError: If parsing fails
        """
        pass
    
    @abstractmethod
    def extract_functions(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract function definitions from code.
        
        Args:
            content: Source code content
            file_path: Optional file path for context
            
        Returns:
            List of function CodeElements
        """
        pass
    
    @abstractmethod
    def extract_classes(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract class definitions from code.
        
        Args:
            content: Source code content
            file_path: Optional file path for context
            
        Returns:
            List of class CodeElements
        """
        pass
    
    @abstractmethod
    def extract_imports(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract import statements from code.
        
        Args:
            content: Source code content
            file_path: Optional file path for context
            
        Returns:
            List of import CodeElements
        """
        pass
    
    @abstractmethod
    def extract_comments(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract comments and docstrings from code.
        
        Args:
            content: Source code content
            file_path: Optional file path for context
            
        Returns:
            List of comment CodeElements
        """
        pass
    
    def get_file_info(self, file_path: Path) -> FileInfo:
        """Get file information for a source file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object with file metadata
            
        Raises:
            ParsingError: If file cannot be accessed
        """
        try:
            stat = file_path.stat()
            
            # Count lines
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines_count = sum(1 for _ in f)
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines_count = sum(1 for _ in f)
            
            return FileInfo(
                path=file_path,
                name=file_path.name,
                extension=file_path.suffix,
                language=self.language,
                size_bytes=stat.st_size,
                lines_count=lines_count,
                created_at=stat.st_ctime,
                modified_at=stat.st_mtime
            )
            
        except Exception as e:
            raise ParsingError(
                f"Failed to get file info for {file_path}",
                file_path=str(file_path),
                language=self.language.value
            ) from e
    
    def read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
            
        Raises:
            ParsingError: If file cannot be read
        """
        try:
            # Try UTF-8 first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Fallback to latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
                    
        except Exception as e:
            raise ParsingError(
                f"Failed to read file {file_path}",
                file_path=str(file_path),
                language=self.language.value
            ) from e
    
    def validate_syntax(self, content: str) -> bool:
        """Validate if the code has valid syntax.
        
        Args:
            content: Source code content
            
        Returns:
            True if syntax is valid, False otherwise
        """
        # Base implementation - subclasses should override
        return True
    
    def get_complexity_score(self, element: CodeElement) -> float:
        """Calculate complexity score for a code element.
        
        Args:
            element: Code element to analyze
            
        Returns:
            Complexity score (higher = more complex)
        """
        # Basic implementation based on content length and nesting
        content_lines = element.content.count('\n') + 1
        indentation_levels = max(
            (line.count('    ') + line.count('\t')) 
            for line in element.content.split('\n') 
            if line.strip()
        ) if element.content.strip() else 0
        
        # Simple heuristic: lines + nesting penalty
        return content_lines + (indentation_levels * 2)
    
    def extract_metadata(self, element: CodeElement) -> Dict[str, Any]:
        """Extract additional metadata for a code element.
        
        Args:
            element: Code element to analyze
            
        Returns:
            Dictionary of metadata
        """
        return {
            "line_count": element.end_line - element.start_line + 1,
            "character_count": len(element.content),
            "complexity_score": self.get_complexity_score(element),
            "has_docstring": bool(element.docstring),
            "has_comments": bool(element.comments),
            "parameter_count": len(element.parameters)
        } 