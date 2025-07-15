from typing import Dict, List, Any
from pathlib import Path
from .base_analyzer import BaseAnalyzer
from ..core.types import CodeElement

class PatternAnalyzer(BaseAnalyzer):
    PATTERNS = {'singleton': 'def __new__', 'factory': '@classmethod def create', 'observer': 'notify_observers'}
    def analyze_file(self, file_path: Path, code_elements: List[CodeElement]) -> Dict[str, Any]:
        detected = {}
        for elem in code_elements:
            for pattern, signature in self.PATTERNS.items():
                if signature in elem.content:
                    detected.setdefault(pattern, []).append(elem.name)
        return {'patterns': detected, 'best_practices': ['Use type hints', 'Add docstrings'] if not detected else []}
    def analyze_project(self, project_path: Path, file_results: Dict[Path, Dict[str, Any]]) -> Dict[str, Any]:
        all_patterns = {}
        for res in file_results.values():
            for pattern, items in res['patterns'].items():
                all_patterns.setdefault(pattern, []).extend(items)
        return {'project_patterns': all_patterns}
