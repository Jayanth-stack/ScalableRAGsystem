"""Parser factory for creating language-specific parsers."""

from typing import Optional, Dict, Type
from pathlib import Path
import logging

from .base_parser import BaseParser
from .tree_sitter_parser import TreeSitterParser
from .python_parser import PythonParser
from ..core.types import LanguageType
from ..core.exceptions import ParsingError

logger = logging.getLogger(__name__)


class ParserFactory:
    """Factory for creating appropriate parsers based on language or file type."""
    
    # Registry of available parsers
    _parsers: Dict[LanguageType, Type[BaseParser]] = {
        LanguageType.PYTHON: PythonParser,
        LanguageType.JAVASCRIPT: TreeSitterParser,
        LanguageType.TYPESCRIPT: TreeSitterParser,
        LanguageType.JAVA: TreeSitterParser,
        LanguageType.GO: TreeSitterParser,
        LanguageType.RUST: TreeSitterParser,
        LanguageType.CPP: TreeSitterParser,
        LanguageType.C: TreeSitterParser,
    }
    
    # File extension to language mapping
    _extension_map = {
        '.py': LanguageType.PYTHON,
        '.pyx': LanguageType.PYTHON,
        '.pyi': LanguageType.PYTHON,
        '.js': LanguageType.JAVASCRIPT,
        '.jsx': LanguageType.JAVASCRIPT,
        '.mjs': LanguageType.JAVASCRIPT,
        '.ts': LanguageType.TYPESCRIPT,
        '.tsx': LanguageType.TYPESCRIPT,
        '.java': LanguageType.JAVA,
        '.go': LanguageType.GO,
        '.rs': LanguageType.RUST,
        '.cpp': LanguageType.CPP,
        '.cc': LanguageType.CPP,
        '.cxx': LanguageType.CPP,
        '.hpp': LanguageType.CPP,
        '.h': LanguageType.CPP,  # Could be C or C++, defaulting to C++
        '.c': LanguageType.C,
        '.cs': LanguageType.CSHARP,
        '.php': LanguageType.PHP,
    }
    
    @classmethod
    def create_parser(cls, language: LanguageType) -> BaseParser:
        """Create a parser for the specified language.
        
        Args:
            language: Programming language to create parser for
            
        Returns:
            Appropriate parser instance
            
        Raises:
            ParsingError: If no parser is available for the language
        """
        try:
            parser_class = cls._parsers.get(language)
            
            if not parser_class:
                # Fall back to generic Tree-sitter parser
                logger.warning(f"No specialized parser for {language}, using generic Tree-sitter parser")
                return TreeSitterParser(language)
            
            # For non-Python languages, pass the language to TreeSitterParser
            if parser_class == TreeSitterParser:
                return parser_class(language)
            else:
                # For specialized parsers like PythonParser
                return parser_class()
                
        except Exception as e:
            raise ParsingError(
                f"Failed to create parser for {language}",
                language=language.value
            ) from e
    
    @classmethod
    def create_parser_from_file(cls, file_path: Path) -> Optional[BaseParser]:
        """Create a parser based on file extension.
        
        Args:
            file_path: Path to the file to be parsed
            
        Returns:
            Appropriate parser instance or None if unsupported
        """
        try:
            file_ext = file_path.suffix.lower()
            language = cls._extension_map.get(file_ext)
            
            if not language:
                logger.warning(f"Unsupported file extension: {file_ext}")
                return None
            
            return cls.create_parser(language)
            
        except Exception as e:
            logger.error(f"Failed to create parser for file {file_path}: {e}")
            return None
    
    @classmethod
    def detect_language(cls, file_path: Path) -> Optional[LanguageType]:
        """Detect programming language from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected language or None if unsupported
        """
        file_ext = file_path.suffix.lower()
        return cls._extension_map.get(file_ext)
    
    @classmethod
    def is_supported_file(cls, file_path: Path) -> bool:
        """Check if a file type is supported for parsing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file type is supported, False otherwise
        """
        return cls.detect_language(file_path) is not None
    
    @classmethod
    def get_supported_languages(cls) -> list[LanguageType]:
        """Get list of supported programming languages.
        
        Returns:
            List of supported languages
        """
        return list(cls._parsers.keys())
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(cls._extension_map.keys())
    
    @classmethod
    def register_parser(cls, language: LanguageType, parser_class: Type[BaseParser]) -> None:
        """Register a new parser for a language.
        
        Args:
            language: Programming language
            parser_class: Parser class to register
        """
        cls._parsers[language] = parser_class
        logger.info(f"Registered parser {parser_class.__name__} for {language}")
    
    @classmethod
    def register_extension(cls, extension: str, language: LanguageType) -> None:
        """Register a file extension for a language.
        
        Args:
            extension: File extension (with dot, e.g., '.py')
            language: Programming language
        """
        cls._extension_map[extension.lower()] = language
        logger.info(f"Registered extension {extension} for {language}")


# Convenience functions for common operations
def parse_file(file_path: Path) -> Optional[BaseParser]:
    """Parse a file using the appropriate parser.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        Parser instance with parsed results or None if failed
    """
    parser = ParserFactory.create_parser_from_file(file_path)
    if parser:
        try:
            result = parser.parse_file(file_path)
            if result.success:
                return parser
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
    
    return None


def get_parser_for_language(language: LanguageType) -> BaseParser:
    """Get a parser for a specific language.
    
    Args:
        language: Programming language
        
    Returns:
        Parser instance for the language
    """
    return ParserFactory.create_parser(language) 