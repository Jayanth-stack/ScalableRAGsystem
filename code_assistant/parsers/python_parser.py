"""Enhanced Python parser with language-specific features."""

import ast
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging

from .tree_sitter_parser import TreeSitterParser
from ..core.types import CodeElement, LanguageType, CodeElementType, AnalysisResult, AnalysisType
from ..core.exceptions import ParsingError

logger = logging.getLogger(__name__)


class PythonParser(TreeSitterParser):
    """Enhanced Python parser with Python-specific analysis."""
    
    def __init__(self):
        """Initialize Python parser."""
        super().__init__(LanguageType.PYTHON)
        
        # Python-specific patterns and keywords
        self.builtin_functions = {
            'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict',
            'set', 'tuple', 'open', 'input', 'type', 'isinstance', 'hasattr', 'getattr',
            'setattr', 'delattr', 'dir', 'vars', 'globals', 'locals', 'eval', 'exec'
        }
        
        self.magic_methods = {
            '__init__', '__str__', '__repr__', '__len__', '__getitem__', '__setitem__',
            '__delitem__', '__iter__', '__next__', '__contains__', '__call__',
            '__enter__', '__exit__', '__add__', '__sub__', '__mul__', '__div__'
        }
    
    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax using AST.
        
        Args:
            content: Python source code
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def parse_file(self, file_path: Path) -> AnalysisResult:
        """Parse Python file with enhanced analysis.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Enhanced AnalysisResult with Python-specific metrics
        """
        try:
            # Get base analysis from Tree-sitter
            result = super().parse_file(file_path)
            
            if result.success:
                # Add Python-specific analysis
                content = self.read_file_content(file_path)
                
                # Enhance elements with Python-specific information
                for element in result.code_elements:
                    self._enhance_python_element(element, content)
                
                # Add Python-specific metrics
                result.metrics.update(self._calculate_python_metrics(result.code_elements, content))
                
                # Detect code quality issues
                result.issues.extend(self._detect_python_issues(result.code_elements, content))
                
                # Generate improvement suggestions
                result.suggestions.extend(self._generate_python_suggestions(result.code_elements))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Python file {file_path}: {e}")
            file_info = self.get_file_info(file_path) if file_path.exists() else None
            
            return AnalysisResult(
                file_info=file_info,
                analysis_type=AnalysisType.SYNTAX,
                success=False,
                error_message=str(e)
            )
    
    def _enhance_python_element(self, element: CodeElement, content: str) -> None:
        """Enhance code element with Python-specific information.
        
        Args:
            element: Code element to enhance
            content: Full source code content
        """
        try:
            # Extract type hints from function signatures
            if element.element_type in ['function', 'method']:
                self._extract_type_hints(element)
                self._detect_async_function(element)
                self._analyze_function_complexity(element)
            
            # Analyze class inheritance and methods
            elif element.element_type == 'class':
                self._extract_class_inheritance(element, content)
                self._detect_class_patterns(element)
            
            # Categorize imports
            elif element.element_type == 'import':
                self._categorize_import(element)
            
            # Classify variables
            elif element.element_type == 'variable':
                self._classify_variable(element)
            
        except Exception as e:
            logger.warning(f"Failed to enhance Python element {element.name}: {e}")
    
    def _extract_type_hints(self, element: CodeElement) -> None:
        """Extract type hints from function signature.
        
        Args:
            element: Function or method element
        """
        try:
            # Parse the function signature for type hints
            lines = element.content.split('\n')
            signature_lines = []
            
            for line in lines:
                signature_lines.append(line)
                if ':' in line and 'def ' in line:
                    break
            
            signature = ' '.join(signature_lines)
            
            # Extract return type hint
            if '->' in signature:
                return_part = signature.split('->')[-1].split(':')[0].strip()
                element.return_type = return_part
            
            # Enhanced parameter extraction with type hints
            enhanced_params = []
            for param in element.parameters:
                param_info = param.copy()
                
                # Look for type hint in signature
                param_name = param['name']
                if f'{param_name}:' in signature:
                    # Extract type hint
                    type_start = signature.find(f'{param_name}:') + len(f'{param_name}:')
                    type_part = signature[type_start:].split(',')[0].split('=')[0].split(')')[0].strip()
                    param_info['type'] = type_part
                
                # Look for default value
                if f'{param_name}=' in signature:
                    default_start = signature.find(f'{param_name}=') + len(f'{param_name}=')
                    default_part = signature[default_start:].split(',')[0].split(')')[0].strip()
                    param_info['default'] = default_part
                
                enhanced_params.append(param_info)
            
            element.parameters = enhanced_params
            
        except Exception as e:
            logger.warning(f"Failed to extract type hints for {element.name}: {e}")
    
    def _detect_async_function(self, element: CodeElement) -> None:
        """Detect if function is async.
        
        Args:
            element: Function element
        """
        if 'async def' in element.content:
            element.modifiers.append('async')
    
    def _analyze_function_complexity(self, element: CodeElement) -> None:
        """Analyze function complexity in detail.
        
        Args:
            element: Function element
        """
        content = element.content
        
        # Count control flow statements
        control_flow_count = (
            content.count('if ') + content.count('elif ') + 
            content.count('for ') + content.count('while ') +
            content.count('try:') + content.count('except') +
            content.count('with ')
        )
        
        # Count nested functions/classes
        nested_count = content.count('def ') + content.count('class ') - 1  # -1 for the function itself
        
        # Calculate cyclomatic complexity (simplified)
        cyclomatic_complexity = 1 + control_flow_count  # Base complexity + decision points
        
        # Update complexity score with more sophisticated calculation
        element.complexity_score = cyclomatic_complexity + nested_count * 0.5
    
    def _extract_class_inheritance(self, element: CodeElement, content: str) -> None:
        """Extract class inheritance information.
        
        Args:
            element: Class element
            content: Full source code content
        """
        try:
            # Look for class definition line
            lines = content.split('\n')
            class_line = None
            
            for i in range(element.start_line - 1, min(element.start_line + 5, len(lines))):
                if i < len(lines) and f'class {element.name}' in lines[i]:
                    class_line = lines[i]
                    break
            
            if class_line and '(' in class_line and ')' in class_line:
                # Extract parent classes
                parents_part = class_line.split('(')[1].split(')')[0]
                if parents_part.strip():
                    parents = [p.strip() for p in parents_part.split(',')]
                    element.dependencies.extend(parents)
                    element.modifiers.extend(parents)
            
        except Exception as e:
            logger.warning(f"Failed to extract inheritance for class {element.name}: {e}")
    
    def _detect_class_patterns(self, element: CodeElement) -> None:
        """Detect common Python class patterns.
        
        Args:
            element: Class element
        """
        content = element.content.lower()
        
        # Detect design patterns
        if 'singleton' in element.name.lower() or '__new__' in content:
            element.modifiers.append('singleton_pattern')
        
        if 'factory' in element.name.lower():
            element.modifiers.append('factory_pattern')
        
        if 'observer' in element.name.lower():
            element.modifiers.append('observer_pattern')
        
        # Detect data classes
        if '@dataclass' in element.content:
            element.modifiers.append('dataclass')
        
        # Detect abstract classes
        if 'abc.ABC' in element.content or '@abstractmethod' in element.content:
            element.modifiers.append('abstract')
    
    def _categorize_import(self, element: CodeElement) -> None:
        """Categorize import statements.
        
        Args:
            element: Import element
        """
        import_content = element.content.lower()
        
        # Categorize by import type
        if import_content.startswith('from'):
            element.modifiers.append('from_import')
        elif import_content.startswith('import'):
            element.modifiers.append('direct_import')
        
        # Categorize by library type
        if any(lib in import_content for lib in ['os', 'sys', 'json', 'datetime', 're', 'pathlib']):
            element.modifiers.append('standard_library')
        elif any(lib in import_content for lib in ['numpy', 'pandas', 'matplotlib', 'requests', 'flask', 'django']):
            element.modifiers.append('third_party')
        else:
            element.modifiers.append('local_import')
    
    def _classify_variable(self, element: CodeElement) -> None:
        """Classify variable types and patterns.
        
        Args:
            element: Variable element
        """
        name = element.name
        content = element.content
        
        # Classify by naming convention
        if name.isupper():
            element.modifiers.append('constant')
        elif name.startswith('_') and not name.startswith('__'):
            element.modifiers.append('protected')
        elif name.startswith('__'):
            element.modifiers.append('private')
        
        # Detect type annotations
        if ':' in content:
            element.modifiers.append('type_annotated')
    
    def _calculate_python_metrics(self, elements: List[CodeElement], content: str) -> Dict[str, Any]:
        """Calculate Python-specific metrics.
        
        Args:
            elements: List of code elements
            content: Full source code content
            
        Returns:
            Dictionary of Python metrics
        """
        metrics = {}
        
        # Count elements by type
        element_counts = {}
        for element in elements:
            element_type = element.element_type  # Already a string due to use_enum_values
            element_counts[element_type] = element_counts.get(element_type, 0) + 1
        
        metrics['element_counts'] = element_counts
        
        # Function complexity analysis
        functions = [e for e in elements if e.element_type == 'function']
        if functions:
            complexities = [e.complexity_score or 0 for e in functions]
            metrics['avg_function_complexity'] = sum(complexities) / len(complexities)
            metrics['max_function_complexity'] = max(complexities)
            metrics['functions_with_docstrings'] = sum(1 for f in functions if f.docstring)
        
        # Class analysis
        classes = [e for e in elements if e.element_type == 'class']
        metrics['class_count'] = len(classes)
        metrics['classes_with_inheritance'] = sum(1 for c in classes if c.dependencies)
        
        # Import analysis
        imports = [e for e in elements if e.element_type == 'import']
        standard_lib = sum(1 for i in imports if 'standard_library' in i.modifiers)
        third_party = sum(1 for i in imports if 'third_party' in i.modifiers)
        local = sum(1 for i in imports if 'local_import' in i.modifiers)
        
        metrics['import_analysis'] = {
            'total': len(imports),
            'standard_library': standard_lib,
            'third_party': third_party,
            'local': local
        }
        
        # Code quality metrics
        total_lines = content.count('\n') + 1
        comment_lines = content.count('#')
        docstring_lines = content.count('"""') + content.count("'''")
        
        metrics['code_quality'] = {
            'total_lines': total_lines,
            'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0,
            'docstring_coverage': (metrics.get('functions_with_docstrings', 0) / len(functions)) if functions else 0,
            'avg_line_length': sum(len(line) for line in content.split('\n')) / total_lines if total_lines > 0 else 0
        }
        
        return metrics
    
    def _detect_python_issues(self, elements: List[CodeElement], content: str) -> List[Dict[str, Any]]:
        """Detect Python-specific code quality issues.
        
        Args:
            elements: List of code elements
            content: Full source code content
            
        Returns:
            List of detected issues
        """
        issues = []
        
        # Check for overly complex functions
        for element in elements:
            if element.element_type == 'function' and element.complexity_score and element.complexity_score > 10:
                issues.append({
                    'type': 'high_complexity',
                    'severity': 'warning',
                    'element': element.name,
                    'line': element.start_line,
                    'message': f"Function '{element.name}' has high complexity ({element.complexity_score:.1f})",
                    'suggestion': 'Consider breaking this function into smaller functions'
                })
        
        # Check for missing docstrings
        functions = [e for e in elements if e.element_type == 'function']
        for func in functions:
            if not func.docstring and not func.name.startswith('_'):
                issues.append({
                    'type': 'missing_docstring',
                    'severity': 'info',
                    'element': func.name,
                    'line': func.start_line,
                    'message': f"Function '{func.name}' is missing a docstring",
                    'suggestion': 'Add a docstring describing the function purpose, parameters, and return value'
                })
        
        # Check for long lines (basic check)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append({
                    'type': 'long_line',
                    'severity': 'style',
                    'line': i,
                    'message': f"Line {i} is too long ({len(line)} characters)",
                    'suggestion': 'Break long lines for better readability (PEP 8 recommends max 79-88 characters)'
                })
        
        return issues[:10]  # Limit to first 10 issues
    
    def _generate_python_suggestions(self, elements: List[CodeElement]) -> List[str]:
        """Generate Python-specific improvement suggestions.
        
        Args:
            elements: List of code elements
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        functions = [e for e in elements if e.element_type == 'function']
        classes = [e for e in elements if e.element_type == 'class']
        
        # Suggest type hints
        untyped_functions = [f for f in functions if not f.return_type and not f.name.startswith('_')]
        if untyped_functions:
            suggestions.append(f"Consider adding type hints to {len(untyped_functions)} functions for better code clarity")
        
        # Suggest docstring improvements
        undocumented_functions = [f for f in functions if not f.docstring and not f.name.startswith('_')]
        if undocumented_functions:
            suggestions.append(f"Add docstrings to {len(undocumented_functions)} public functions")
        
        # Suggest design patterns
        large_classes = [c for c in classes if c.complexity_score and c.complexity_score > 20]
        if large_classes:
            suggestions.append("Consider breaking down large classes into smaller, more focused classes")
        
        # Suggest async/await usage
        sync_functions = [f for f in functions if 'async' not in f.modifiers and ('requests' in f.content or 'urllib' in f.content)]
        if sync_functions:
            suggestions.append("Consider using async/await for I/O operations to improve performance")
        
        return suggestions 