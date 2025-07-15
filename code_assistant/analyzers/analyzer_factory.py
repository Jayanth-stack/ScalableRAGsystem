from typing import Dict, Type
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .complexity_analyzer import ComplexityAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .pattern_analyzer import PatternAnalyzer
from .security_analyzer import SecurityAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from ..core.types import LanguageType
from ..core.exceptions import AnalysisError

class AnalyzerFactory:
    """Factory for creating appropriate analyzers."""
    
    _analyzers: Dict[str, Type[BaseAnalyzer]] = {}
    
    @classmethod
    def register_analyzer(cls, name: str, analyzer_class: Type[BaseAnalyzer]):
        cls._analyzers[name] = analyzer_class
    
    @classmethod
    def create_analyzer(cls, name: str) -> BaseAnalyzer:
        analyzer_class = cls._analyzers.get(name)
        if not analyzer_class:
            raise AnalysisError(f"No analyzer registered for {name}")
        return analyzer_class() 

# Register built-in analyzers
AnalyzerFactory.register_analyzer('complexity', ComplexityAnalyzer)
AnalyzerFactory.register_analyzer('dependency', DependencyAnalyzer)
AnalyzerFactory.register_analyzer('pattern', PatternAnalyzer)
AnalyzerFactory.register_analyzer('security', SecurityAnalyzer)
AnalyzerFactory.register_analyzer('performance', PerformanceAnalyzer) 