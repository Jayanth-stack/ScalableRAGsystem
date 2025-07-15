from typing import Dict, List, Any
from pathlib import Path
from .base_analyzer import BaseAnalyzer
from ..core.types import CodeElement

class PerformanceAnalyzer(BaseAnalyzer):
    def analyze_file(self, file_path: Path, code_elements: List[CodeElement]) -> Dict[str, Any]:
        suggestions = []
        for elem in code_elements:
            if 'for ' in elem.content and 'range(' in elem.content:
                suggestions.append(f'Use enumerate in {elem.name}')
            if 'O(n^2)' in elem.comments:
                suggestions.append(f'Optimize algorithm in {elem.name}')
        return {'suggestions': suggestions}
    def analyze_project(self, project_path: Path, file_results: Dict[Path, Dict[str, Any]]) -> Dict[str, Any]:
        all_sugs = [s for res in file_results.values() for s in res['suggestions']]
        return {'total_suggestions': len(all_sugs)}
