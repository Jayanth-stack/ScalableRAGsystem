"""Intelligent code chunking using AST structure."""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
import logging
from dataclasses import dataclass

from ..core.types import (
    CodeElement, DocumentChunk, LanguageType, CodeElementType, 
    AnalysisResult, FileInfo
)
from ..parsers.parser_factory import ParserFactory

logger = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    """Strategy for chunking code."""
    FUNCTION_BASED = "function_based"  # Each function/method as a chunk
    CLASS_BASED = "class_based"  # Each class as a chunk
    SEMANTIC_BLOCKS = "semantic_blocks"  # Logical code blocks
    SLIDING_WINDOW = "sliding_window"  # Traditional sliding window
    HYBRID = "hybrid"  # Combination of strategies


@dataclass
class ChunkingConfig:
    """Configuration for code chunking."""
    strategy: ChunkingStrategy = ChunkingStrategy.HYBRID
    max_chunk_size: int = 1000  # Max characters per chunk
    min_chunk_size: int = 100   # Min characters per chunk
    overlap_size: int = 100     # Overlap between chunks
    include_context: bool = True  # Include surrounding context
    preserve_functions: bool = True  # Keep functions intact
    preserve_classes: bool = True  # Keep classes intact
    include_imports: bool = True  # Include relevant imports
    include_docstrings: bool = True  # Include docstrings separately
    merge_small_functions: bool = True  # Merge small related functions


class CodeChunker:
    """Intelligent code chunker using AST analysis."""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize the code chunker.
        
        Args:
            config: Chunking configuration
        """
        self.config = config or ChunkingConfig()
        self.parser_factory = ParserFactory()
    
    def chunk_file(self, file_path: Path) -> List[DocumentChunk]:
        """Chunk a single file using AST-aware strategies.
        
        Args:
            file_path: Path to the file to chunk
            
        Returns:
            List of document chunks
        """
        try:
            # Parse the file using appropriate parser
            parser = self.parser_factory.create_parser_from_file(file_path)
            if not parser:
                logger.warning(f"No parser available for {file_path}")
                return self._fallback_chunking(file_path)
            
            result = parser.parse_file(file_path)
            if not result.success:
                logger.warning(f"Failed to parse {file_path}: {result.error_message}")
                return self._fallback_chunking(file_path)
            
            # Read file content
            content = parser.read_file_content(file_path)
            
            # Apply chunking strategy
            if self.config.strategy == ChunkingStrategy.FUNCTION_BASED:
                chunks = self._chunk_by_functions(result, content, file_path)
            elif self.config.strategy == ChunkingStrategy.CLASS_BASED:
                chunks = self._chunk_by_classes(result, content, file_path)
            elif self.config.strategy == ChunkingStrategy.SEMANTIC_BLOCKS:
                chunks = self._chunk_semantic_blocks(result, content, file_path)
            elif self.config.strategy == ChunkingStrategy.SLIDING_WINDOW:
                chunks = self._sliding_window_chunking(content, file_path)
            else:  # HYBRID
                chunks = self._hybrid_chunking(result, content, file_path)
            
            # Post-process chunks
            chunks = self._post_process_chunks(chunks, result, content)
            
            logger.info(f"Created {len(chunks)} chunks from {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking file {file_path}: {e}")
            return self._fallback_chunking(file_path)
    
    def chunk_repository(self, repo_path: Path) -> List[DocumentChunk]:
        """Chunk all files in a repository.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of all document chunks
        """
        all_chunks = []
        
        # Find all supported files
        supported_files = []
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and self.parser_factory.is_supported_file(file_path):
                supported_files.append(file_path)
        
        logger.info(f"Found {len(supported_files)} supported files in {repo_path}")
        
        # Chunk each file
        for file_path in supported_files:
            chunks = self.chunk_file(file_path)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} total chunks from {len(supported_files)} files")
        return all_chunks
    
    def _chunk_by_functions(self, result: AnalysisResult, content: str, file_path: Path) -> List[DocumentChunk]:
        """Chunk code by functions and methods."""
        chunks = []
        lines = content.split('\n')
        
        # Get all functions and methods
        functions = [e for e in result.code_elements 
                    if e.element_type in ['function', 'method']]
        
        for func in functions:
            chunk_content = self._extract_element_content(func, lines)
            
            # Add context if enabled
            if self.config.include_context:
                chunk_content = self._add_context(func, lines, result)
            
            # Create chunk
            chunk = DocumentChunk(
                content=chunk_content,
                chunk_type="code",
                language=result.file_info.language,
                file_path=file_path,
                start_line=func.start_line,
                end_line=func.end_line,
                element_name=func.name,
                element_type=func.element_type,
                metadata={
                    "function_name": func.name,
                    "complexity_score": func.complexity_score,
                    "parameters": func.parameters,
                    "return_type": func.return_type,
                    "docstring": func.docstring,
                    "decorators": func.decorators,
                    "parent_class": func.parent_element
                }
            )
            chunks.append(chunk)
            
            # Create separate docstring chunk if exists and enabled
            if self.config.include_docstrings and func.docstring:
                doc_chunk = DocumentChunk(
                    content=func.docstring,
                    chunk_type="docstring",
                    language=result.file_info.language,
                    file_path=file_path,
                    start_line=func.start_line,
                    end_line=func.start_line + func.docstring.count('\n'),
                    element_name=func.name,
                    element_type=func.element_type,
                    metadata={
                        "function_name": func.name,
                        "docstring_type": "function_docstring"
                    }
                )
                chunks.append(doc_chunk)
        
        return chunks
    
    def _chunk_by_classes(self, result: AnalysisResult, content: str, file_path: Path) -> List[DocumentChunk]:
        """Chunk code by classes."""
        chunks = []
        lines = content.split('\n')
        
        # Get all classes
        classes = [e for e in result.code_elements if e.element_type == 'class']
        
        for cls in classes:
            # Get class content including all methods
            chunk_content = self._extract_element_content(cls, lines)
            
            # Create chunk
            chunk = DocumentChunk(
                content=chunk_content,
                chunk_type="code",
                language=result.file_info.language,
                file_path=file_path,
                start_line=cls.start_line,
                end_line=cls.end_line,
                element_name=cls.name,
                element_type=cls.element_type,
                metadata={
                    "class_name": cls.name,
                    "inheritance": cls.dependencies,
                    "methods": cls.children,
                    "decorators": cls.decorators,
                    "complexity_score": cls.complexity_score
                }
            )
            chunks.append(chunk)
            
            # Create docstring chunk if exists
            if self.config.include_docstrings and cls.docstring:
                doc_chunk = DocumentChunk(
                    content=cls.docstring,
                    chunk_type="docstring",
                    language=result.file_info.language,
                    file_path=file_path,
                    start_line=cls.start_line,
                    end_line=cls.start_line + cls.docstring.count('\n'),
                    element_name=cls.name,
                    element_type=cls.element_type,
                    metadata={
                        "class_name": cls.name,
                        "docstring_type": "class_docstring"
                    }
                )
                chunks.append(doc_chunk)
        
        return chunks
    
    def _chunk_semantic_blocks(self, result: AnalysisResult, content: str, file_path: Path) -> List[DocumentChunk]:
        """Chunk code into semantic blocks."""
        chunks = []
        lines = content.split('\n')
        
        # Group elements by logical proximity and relationships
        semantic_groups = self._group_semantic_elements(result.code_elements)
        
        for group in semantic_groups:
            if not group:
                continue
                
            # Calculate bounds of the group
            start_line = min(e.start_line for e in group)
            end_line = max(e.end_line for e in group)
            
            # Extract content
            chunk_content = '\n'.join(lines[start_line-1:end_line])
            
            # Create metadata
            metadata = {
                "semantic_group": True,
                "elements": [{"name": e.name, "type": e.element_type} for e in group],
                "group_size": len(group)
            }
            
            chunk = DocumentChunk(
                content=chunk_content,
                chunk_type="code",
                language=result.file_info.language,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                element_name=f"semantic_block_{start_line}_{end_line}",
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    def _sliding_window_chunking(self, content: str, file_path: Path) -> List[DocumentChunk]:
        """Traditional sliding window chunking as fallback."""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_size = 0
        chunk_start_line = 1
        
        for i, line in enumerate(lines, 1):
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline
            
            if current_size >= self.config.max_chunk_size:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunk = DocumentChunk(
                    content=chunk_content,
                    chunk_type="code",
                    file_path=file_path,
                    start_line=chunk_start_line,
                    end_line=i,
                    element_name=f"chunk_{chunk_start_line}_{i}",
                    metadata={"chunking_method": "sliding_window"}
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_lines = max(1, self.config.overlap_size // 50)  # Assume ~50 chars per line
                current_chunk = current_chunk[-overlap_lines:]
                current_size = sum(len(line) + 1 for line in current_chunk)
                chunk_start_line = i - overlap_lines + 1
        
        # Add final chunk if any content remains
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk = DocumentChunk(
                content=chunk_content,
                chunk_type="code",
                file_path=file_path,
                start_line=chunk_start_line,
                end_line=len(lines),
                element_name=f"chunk_{chunk_start_line}_{len(lines)}",
                metadata={"chunking_method": "sliding_window"}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _hybrid_chunking(self, result: AnalysisResult, content: str, file_path: Path) -> List[DocumentChunk]:
        """Hybrid chunking strategy combining multiple approaches."""
        chunks = []
        
        # Start with function-based chunking for primary elements
        if self.config.preserve_functions:
            function_chunks = self._chunk_by_functions(result, content, file_path)
            chunks.extend(function_chunks)
        
        # Add class-level chunks for complex classes
        if self.config.preserve_classes:
            classes = [e for e in result.code_elements if e.element_type == 'class']
            complex_classes = [c for c in classes if c.complexity_score and c.complexity_score > 10]
            
            for cls in complex_classes:
                lines = content.split('\n')
                chunk_content = self._extract_element_content(cls, lines)
                
                chunk = DocumentChunk(
                    content=chunk_content,
                    chunk_type="code",
                    language=result.file_info.language,
                    file_path=file_path,
                    start_line=cls.start_line,
                    end_line=cls.end_line,
                    element_name=cls.name,
                    element_type=cls.element_type,
                    metadata={
                        "class_name": cls.name,
                        "chunking_reason": "complex_class",
                        "complexity_score": cls.complexity_score
                    }
                )
                chunks.append(chunk)
        
        # Handle imports separately if enabled
        if self.config.include_imports:
            imports = [e for e in result.code_elements if e.element_type == 'import']
            if imports:
                import_lines = []
                for imp in imports:
                    lines = content.split('\n')
                    import_content = lines[imp.start_line-1:imp.end_line]
                    import_lines.extend(import_content)
                
                if import_lines:
                    chunk = DocumentChunk(
                        content='\n'.join(import_lines),
                        chunk_type="code",
                        language=result.file_info.language,
                        file_path=file_path,
                        start_line=1,
                        end_line=len(import_lines),
                        element_name="imports",
                        element_type="import",
                        metadata={
                            "chunk_type": "imports",
                            "import_count": len(imports)
                        }
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _group_semantic_elements(self, elements: List[CodeElement]) -> List[List[CodeElement]]:
        """Group code elements by semantic relationships."""
        groups = []
        used_elements = set()
        
        for element in elements:
            if element.name in used_elements:
                continue
                
            group = [element]
            used_elements.add(element.name)
            
            # Find related elements
            for other in elements:
                if other.name in used_elements:
                    continue
                    
                if self._are_semantically_related(element, other):
                    group.append(other)
                    used_elements.add(other.name)
            
            if len(group) > 1 or element.element_type in ['class', 'function']:
                groups.append(group)
        
        return groups
    
    def _are_semantically_related(self, elem1: CodeElement, elem2: CodeElement) -> bool:
        """Check if two elements are semantically related."""
        # Same parent (methods in same class)
        if elem1.parent_element and elem1.parent_element == elem2.parent_element:
            return True
        
        # Similar names (helper functions)
        if elem1.name.startswith(elem2.name[:3]) or elem2.name.startswith(elem1.name[:3]):
            return True
        
        # Close proximity (within 10 lines)
        if abs(elem1.start_line - elem2.end_line) <= 10:
            return True
        
        # Dependency relationship
        if elem2.name in elem1.dependencies or elem1.name in elem2.dependencies:
            return True
        
        return False
    
    def _extract_element_content(self, element: CodeElement, lines: List[str]) -> str:
        """Extract content for a code element with proper boundaries."""
        start_idx = max(0, element.start_line - 1)
        end_idx = min(len(lines), element.end_line)
        return '\n'.join(lines[start_idx:end_idx])
    
    def _add_context(self, element: CodeElement, lines: List[str], result: AnalysisResult) -> str:
        """Add surrounding context to an element."""
        context_lines = 3  # Lines of context to add
        
        start_idx = max(0, element.start_line - 1 - context_lines)
        end_idx = min(len(lines), element.end_line + context_lines)
        
        # Add relevant imports
        if self.config.include_imports:
            imports = [e for e in result.code_elements if e.element_type == 'import']
            import_lines = []
            for imp in imports:
                if any(dep in element.dependencies for dep in imp.dependencies):
                    import_lines.extend(lines[imp.start_line-1:imp.end_line])
            
            if import_lines:
                context_content = '\n'.join(import_lines) + '\n\n' + '\n'.join(lines[start_idx:end_idx])
                return context_content
        
        return '\n'.join(lines[start_idx:end_idx])
    
    def _post_process_chunks(self, chunks: List[DocumentChunk], result: AnalysisResult, content: str) -> List[DocumentChunk]:
        """Post-process chunks for optimization."""
        processed_chunks = []
        
        for chunk in chunks:
            # Skip chunks that are too small (unless they're important)
            if (len(chunk.content) < self.config.min_chunk_size and 
                chunk.element_type not in ['class', 'function']):
                continue
            
            # Trim chunks that are too large
            if len(chunk.content) > self.config.max_chunk_size:
                chunk = self._trim_chunk(chunk)
            
            processed_chunks.append(chunk)
        
        # Merge small related chunks if enabled
        if self.config.merge_small_functions:
            processed_chunks = self._merge_small_chunks(processed_chunks)
        
        return processed_chunks
    
    def _trim_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        """Trim a chunk that's too large."""
        lines = chunk.content.split('\n')
        target_lines = int(self.config.max_chunk_size / 50)  # Assume ~50 chars per line
        
        if len(lines) > target_lines:
            trimmed_lines = lines[:target_lines]
            chunk.content = '\n'.join(trimmed_lines)
            chunk.end_line = chunk.start_line + len(trimmed_lines) - 1
            
            # Update metadata
            chunk.metadata["trimmed"] = True
            chunk.metadata["original_lines"] = len(lines)
        
        return chunk
    
    def _merge_small_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Merge small related chunks."""
        merged_chunks = []
        current_group = []
        
        for chunk in chunks:
            if len(chunk.content) < self.config.min_chunk_size * 2:
                current_group.append(chunk)
            else:
                # Process accumulated small chunks
                if current_group:
                    if len(current_group) == 1:
                        merged_chunks.append(current_group[0])
                    else:
                        merged_chunk = self._create_merged_chunk(current_group)
                        merged_chunks.append(merged_chunk)
                    current_group = []
                
                merged_chunks.append(chunk)
        
        # Handle remaining small chunks
        if current_group:
            if len(current_group) == 1:
                merged_chunks.append(current_group[0])
            else:
                merged_chunk = self._create_merged_chunk(current_group)
                merged_chunks.append(merged_chunk)
        
        return merged_chunks
    
    def _create_merged_chunk(self, chunks: List[DocumentChunk]) -> DocumentChunk:
        """Create a merged chunk from multiple small chunks."""
        if not chunks:
            raise ValueError("Cannot merge empty chunk list")
        
        # Combine content
        combined_content = '\n\n'.join(chunk.content for chunk in chunks)
        
        # Calculate bounds
        start_line = min(chunk.start_line for chunk in chunks)
        end_line = max(chunk.end_line for chunk in chunks)
        
        # Create metadata
        metadata = {
            "merged_chunk": True,
            "original_chunks": len(chunks),
            "element_names": [chunk.element_name for chunk in chunks if chunk.element_name],
            "element_types": list(set(chunk.element_type for chunk in chunks if chunk.element_type))
        }
        
        return DocumentChunk(
            content=combined_content,
            chunk_type="code",
            language=chunks[0].language,
            file_path=chunks[0].file_path,
            start_line=start_line,
            end_line=end_line,
            element_name=f"merged_{start_line}_{end_line}",
            metadata=metadata
        )
    
    def _fallback_chunking(self, file_path: Path) -> List[DocumentChunk]:
        """Fallback chunking when parsing fails."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._sliding_window_chunking(content, file_path)
            
        except Exception as e:
            logger.error(f"Fallback chunking failed for {file_path}: {e}")
            return [] 