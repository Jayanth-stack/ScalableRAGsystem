"""Tree-sitter based parser implementation."""

import tree_sitter
from tree_sitter import Language, Parser, Node, Tree
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import logging

from .base_parser import BaseParser
from ..core.types import CodeElement, LanguageType, CodeElementType, AnalysisResult, AnalysisType
from ..core.exceptions import ParsingError

logger = logging.getLogger(__name__)


class TreeSitterParser(BaseParser):
    """Tree-sitter based parser for multiple programming languages."""
    
    # Language to Tree-sitter library mapping
    LANGUAGE_LIBRARIES = {
        LanguageType.PYTHON: "tree-sitter-python",
        LanguageType.JAVASCRIPT: "tree-sitter-javascript", 
        LanguageType.TYPESCRIPT: "tree-sitter-typescript",
        LanguageType.JAVA: "tree-sitter-java",
        LanguageType.GO: "tree-sitter-go",
        LanguageType.RUST: "tree-sitter-rust",
        LanguageType.CPP: "tree-sitter-cpp",
        LanguageType.C: "tree-sitter-c",
    }
    
    def __init__(self, language: LanguageType):
        """Initialize Tree-sitter parser for specific language.
        
        Args:
            language: Programming language to parse
            
        Raises:
            ParsingError: If language is not supported or Tree-sitter setup fails
        """
        self.parser: Optional[Parser] = None
        self.tree_sitter_language: Optional[Language] = None
        self.node_types: Dict[str, CodeElementType] = {}
        
        super().__init__(language)
    
    def _setup_parser(self) -> None:
        """Setup Tree-sitter parser for the specific language."""
        try:
            # Import the language-specific module
            if self.language == LanguageType.PYTHON:
                import tree_sitter_python as ts_python
                self.tree_sitter_language = Language(ts_python.language())
                self._setup_python_node_types()
                
            elif self.language == LanguageType.JAVASCRIPT:
                import tree_sitter_javascript as ts_javascript
                self.tree_sitter_language = Language(ts_javascript.language())
                self._setup_javascript_node_types()
                
            elif self.language == LanguageType.TYPESCRIPT:
                import tree_sitter_typescript as ts_typescript
                self.tree_sitter_language = Language(ts_typescript.language_typescript())
                self._setup_typescript_node_types()
                
            elif self.language == LanguageType.JAVA:
                import tree_sitter_java as ts_java
                self.tree_sitter_language = Language(ts_java.language())
                self._setup_java_node_types()
                
            elif self.language == LanguageType.GO:
                import tree_sitter_go as ts_go
                self.tree_sitter_language = Language(ts_go.language())
                self._setup_go_node_types()
                
            elif self.language == LanguageType.RUST:
                import tree_sitter_rust as ts_rust
                self.tree_sitter_language = Language(ts_rust.language())
                self._setup_rust_node_types()
                
            else:
                raise ParsingError(
                    f"Language {self.language} not yet supported",
                    language=self.language.value
                )
            
            # Create parser instance with language
            self.parser = Parser(self.tree_sitter_language)
            
            logger.info(f"Tree-sitter parser initialized for {self.language}")
            
        except ImportError as e:
            raise ParsingError(
                f"Tree-sitter library for {self.language} not installed. "
                f"Install with: pip install {self.LANGUAGE_LIBRARIES.get(self.language, 'tree-sitter-' + self.language.value)}",
                language=self.language.value
            ) from e
        except Exception as e:
            raise ParsingError(
                f"Failed to setup Tree-sitter parser for {self.language}",
                language=self.language.value
            ) from e
    
    def _setup_python_node_types(self) -> None:
        """Setup node type mappings for Python."""
        self.node_types = {
            "function_definition": CodeElementType.FUNCTION,
            "async_function_definition": CodeElementType.FUNCTION,
            "class_definition": CodeElementType.CLASS,
            "import_statement": CodeElementType.IMPORT,
            "import_from_statement": CodeElementType.IMPORT,
            "assignment": CodeElementType.VARIABLE,
            "comment": CodeElementType.COMMENT,
            "string": CodeElementType.DOCSTRING,  # Will filter for docstrings
            "decorator": CodeElementType.DECORATOR,
        }
    
    def _setup_javascript_node_types(self) -> None:
        """Setup node type mappings for JavaScript."""
        self.node_types = {
            "function_declaration": CodeElementType.FUNCTION,
            "function_expression": CodeElementType.FUNCTION,
            "arrow_function": CodeElementType.FUNCTION,
            "class_declaration": CodeElementType.CLASS,
            "method_definition": CodeElementType.METHOD,
            "import_statement": CodeElementType.IMPORT,
            "variable_declaration": CodeElementType.VARIABLE,
            "comment": CodeElementType.COMMENT,
        }
    
    def _setup_typescript_node_types(self) -> None:
        """Setup node type mappings for TypeScript."""
        self.node_types = {
            "function_declaration": CodeElementType.FUNCTION,
            "function_expression": CodeElementType.FUNCTION,
            "arrow_function": CodeElementType.FUNCTION,
            "class_declaration": CodeElementType.CLASS,
            "method_definition": CodeElementType.METHOD,
            "interface_declaration": CodeElementType.INTERFACE,
            "type_alias_declaration": CodeElementType.INTERFACE,
            "enum_declaration": CodeElementType.ENUM,
            "import_statement": CodeElementType.IMPORT,
            "variable_declaration": CodeElementType.VARIABLE,
            "comment": CodeElementType.COMMENT,
        }
    
    def _setup_java_node_types(self) -> None:
        """Setup node type mappings for Java."""
        self.node_types = {
            "method_declaration": CodeElementType.METHOD,
            "class_declaration": CodeElementType.CLASS,
            "interface_declaration": CodeElementType.INTERFACE,
            "enum_declaration": CodeElementType.ENUM,
            "import_declaration": CodeElementType.IMPORT,
            "field_declaration": CodeElementType.VARIABLE,
            "comment": CodeElementType.COMMENT,
        }
    
    def _setup_go_node_types(self) -> None:
        """Setup node type mappings for Go."""
        self.node_types = {
            "function_declaration": CodeElementType.FUNCTION,
            "method_declaration": CodeElementType.METHOD,
            "type_declaration": CodeElementType.CLASS,  # Go structs/interfaces
            "import_declaration": CodeElementType.IMPORT,
            "var_declaration": CodeElementType.VARIABLE,
            "const_declaration": CodeElementType.CONSTANT,
            "comment": CodeElementType.COMMENT,
        }
    
    def _setup_rust_node_types(self) -> None:
        """Setup node type mappings for Rust."""
        self.node_types = {
            "function_item": CodeElementType.FUNCTION,
            "impl_item": CodeElementType.CLASS,
            "struct_item": CodeElementType.STRUCT,
            "enum_item": CodeElementType.ENUM,
            "trait_item": CodeElementType.INTERFACE,
            "use_declaration": CodeElementType.IMPORT,
            "let_declaration": CodeElementType.VARIABLE,
            "const_item": CodeElementType.CONSTANT,
            "line_comment": CodeElementType.COMMENT,
            "block_comment": CodeElementType.COMMENT,
        }
    
    def parse_file(self, file_path: Path) -> AnalysisResult:
        """Parse a file using Tree-sitter.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            AnalysisResult with extracted code elements
        """
        try:
            # Get file info
            file_info = self.get_file_info(file_path)
            
            # Read content
            content = self.read_file_content(file_path)
            
            # Parse content
            code_elements = self.parse_content(content, file_path)
            
            return AnalysisResult(
                file_info=file_info,
                analysis_type=AnalysisType.SYNTAX,
                code_elements=code_elements,
                success=True,
                metrics={"elements_found": len(code_elements)}
            )
            
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            file_info = self.get_file_info(file_path) if file_path.exists() else None
            
            return AnalysisResult(
                file_info=file_info,
                analysis_type=AnalysisType.SYNTAX,
                success=False,
                error_message=str(e)
            )
    
    def parse_content(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Parse code content and extract all elements.
        
        Args:
            content: Source code content
            file_path: Optional file path for context
            
        Returns:
            List of extracted code elements
        """
        if not self.parser:
            raise ParsingError("Parser not initialized", language=self.language.value)
        
        try:
            # Parse content into AST
            tree = self.parser.parse(content.encode('utf-8'))
            
            # Extract all elements
            elements = []
            elements.extend(self._extract_elements_from_tree(tree, content, file_path))
            
            return elements
            
        except Exception as e:
            raise ParsingError(
                f"Failed to parse content",
                file_path=str(file_path) if file_path else None,
                language=self.language.value
            ) from e
    
    def _extract_elements_from_tree(self, tree: Tree, content: str, file_path: Optional[Path]) -> List[CodeElement]:
        """Extract code elements from parsed AST tree.
        
        Args:
            tree: Parsed AST tree
            content: Original source code content
            file_path: Optional file path for context
            
        Returns:
            List of extracted code elements
        """
        elements = []
        lines = content.split('\n')
        
        def traverse_node(node: Node, parent_element: Optional[str] = None) -> None:
            """Recursively traverse AST nodes."""
            try:
                # Check if this node type is one we want to extract
                element_type = self.node_types.get(node.type)
                
                if element_type:
                    element = self._create_code_element(
                        node, content, lines, file_path, element_type, parent_element
                    )
                    if element:
                        elements.append(element)
                        
                        # For classes, set as parent for child methods
                        current_parent = element.name if element_type == CodeElementType.CLASS else parent_element
                    else:
                        current_parent = parent_element
                else:
                    current_parent = parent_element
                
                # Recursively process child nodes
                for child in node.children:
                    traverse_node(child, current_parent)
                    
            except Exception as e:
                logger.warning(f"Error processing node {node.type}: {e}")
        
        # Start traversal from root
        traverse_node(tree.root_node)
        
        return elements
    
    def _create_code_element(
        self, 
        node: Node, 
        content: str, 
        lines: List[str], 
        file_path: Optional[Path],
        element_type: CodeElementType,
        parent_element: Optional[str]
    ) -> Optional[CodeElement]:
        """Create a CodeElement from an AST node.
        
        Args:
            node: AST node
            content: Full source code content
            lines: Content split into lines
            file_path: File path for context
            element_type: Type of code element
            parent_element: Parent element name (for methods in classes)
            
        Returns:
            CodeElement or None if extraction fails
        """
        try:
            # Get node position
            start_point = node.start_point
            end_point = node.end_point
            
            # Extract node content
            node_content = content[node.start_byte:node.end_byte]
            
            # Extract element name
            name = self._extract_element_name(node, element_type)
            if not name:
                return None
            
            # Create base element
            element = CodeElement(
                name=name,
                element_type=element_type,
                language=self.language,
                file_path=file_path or Path("unknown"),
                start_line=start_point[0] + 1,  # Tree-sitter uses 0-based indexing
                end_line=end_point[0] + 1,
                start_column=start_point[1],
                end_column=end_point[1],
                content=node_content,
                parent_element=parent_element
            )
            
            # Extract additional details based on element type
            self._enrich_element(element, node, content)
            
            return element
            
        except Exception as e:
            logger.warning(f"Failed to create element from node {node.type}: {e}")
            return None
    
    def _extract_element_name(self, node: Node, element_type: CodeElementType) -> Optional[str]:
        """Extract the name of a code element from its AST node.
        
        Args:
            node: AST node
            element_type: Type of code element
            
        Returns:
            Element name or None if not found
        """
        try:
            # Different languages and element types have different name extraction patterns
            if self.language == LanguageType.PYTHON:
                return self._extract_python_name(node, element_type)
            elif self.language in [LanguageType.JAVASCRIPT, LanguageType.TYPESCRIPT]:
                return self._extract_javascript_name(node, element_type)
            elif self.language == LanguageType.JAVA:
                return self._extract_java_name(node, element_type)
            elif self.language == LanguageType.GO:
                return self._extract_go_name(node, element_type)
            elif self.language == LanguageType.RUST:
                return self._extract_rust_name(node, element_type)
            else:
                return self._extract_generic_name(node)
                
        except Exception as e:
            logger.warning(f"Failed to extract name from {node.type}: {e}")
            return None
    
    def _extract_python_name(self, node: Node, element_type: CodeElementType) -> Optional[str]:
        """Extract name from Python AST node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode('utf-8')
        return None
    
    def _extract_javascript_name(self, node: Node, element_type: CodeElementType) -> Optional[str]:
        """Extract name from JavaScript/TypeScript AST node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode('utf-8')
        return None
    
    def _extract_java_name(self, node: Node, element_type: CodeElementType) -> Optional[str]:
        """Extract name from Java AST node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode('utf-8')
        return None
    
    def _extract_go_name(self, node: Node, element_type: CodeElementType) -> Optional[str]:
        """Extract name from Go AST node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode('utf-8')
        return None
    
    def _extract_rust_name(self, node: Node, element_type: CodeElementType) -> Optional[str]:
        """Extract name from Rust AST node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode('utf-8')
        return None
    
    def _extract_generic_name(self, node: Node) -> Optional[str]:
        """Generic name extraction for unsupported languages."""
        # Look for identifier children
        for child in node.children:
            if "identifier" in child.type:
                return child.text.decode('utf-8')
        return f"unnamed_{node.type}"
    
    def _enrich_element(self, element: CodeElement, node: Node, content: str) -> None:
        """Enrich code element with additional information.
        
        Args:
            element: CodeElement to enrich
            node: AST node
            content: Full source code content
        """
        # Extract docstring if available
        docstring = self._extract_docstring(node, content)
        if docstring:
            element.docstring = docstring
        
        # Extract parameters for functions/methods
        if element.element_type in [CodeElementType.FUNCTION, CodeElementType.METHOD]:
            element.parameters = self._extract_parameters(node)
        
        # Extract decorators (Python specific)
        if self.language == LanguageType.PYTHON:
            element.decorators = self._extract_decorators(node)
        
        # Calculate complexity score
        element.complexity_score = self.get_complexity_score(element)
    
    def _extract_docstring(self, node: Node, content: str) -> Optional[str]:
        """Extract docstring from function/class node."""
        # Language-specific docstring extraction
        if self.language == LanguageType.PYTHON:
            return self._extract_python_docstring(node, content)
        return None
    
    def _extract_python_docstring(self, node: Node, content: str) -> Optional[str]:
        """Extract Python docstring from node."""
        # Look for string literal as first statement in function/class body
        for child in node.children:
            if child.type == "block":
                for stmt in child.children:
                    if stmt.type == "expression_statement":
                        for expr in stmt.children:
                            if expr.type == "string":
                                docstring = expr.text.decode('utf-8')
                                # Clean up the docstring
                                return docstring.strip('"""').strip("'''").strip()
        return None
    
    def _extract_parameters(self, node: Node) -> List[Dict[str, Any]]:
        """Extract function parameters from node."""
        parameters = []
        
        # Find parameter list
        for child in node.children:
            if child.type == "parameters":
                for param in child.children:
                    if param.type == "identifier":
                        parameters.append({
                            "name": param.text.decode('utf-8'),
                            "type": None,  # Will be enhanced in language-specific parsers
                            "default": None
                        })
        
        return parameters
    
    def _extract_decorators(self, node: Node) -> List[str]:
        """Extract decorators from Python function/class."""
        decorators = []
        
        # Look for decorator nodes before the function/class
        for child in node.children:
            if child.type == "decorator":
                decorator_text = child.text.decode('utf-8')
                decorators.append(decorator_text)
        
        return decorators
    
    # Abstract method implementations (delegating to Tree-sitter parsing)
    
    def extract_functions(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract function definitions using Tree-sitter."""
        all_elements = self.parse_content(content, file_path)
        return [e for e in all_elements if e.element_type == CodeElementType.FUNCTION]
    
    def extract_classes(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract class definitions using Tree-sitter."""
        all_elements = self.parse_content(content, file_path)
        return [e for e in all_elements if e.element_type == CodeElementType.CLASS]
    
    def extract_imports(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract import statements using Tree-sitter."""
        all_elements = self.parse_content(content, file_path)
        return [e for e in all_elements if e.element_type == CodeElementType.IMPORT]
    
    def extract_comments(self, content: str, file_path: Optional[Path] = None) -> List[CodeElement]:
        """Extract comments and docstrings using Tree-sitter."""
        all_elements = self.parse_content(content, file_path)
        return [e for e in all_elements if e.element_type in [CodeElementType.COMMENT, CodeElementType.DOCSTRING]] 