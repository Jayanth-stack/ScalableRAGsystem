import ast
from typing import Dict, List, Any
from pathlib import Path
import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from .base_analyzer import BaseAnalyzer
from ..core.types import CodeElement, ComplexityMetrics
from ..core.exceptions import AnalysisError

class ComplexityAnalyzer(BaseAnalyzer):
    def analyze_file(self, file_path: Path, code_elements: List[CodeElement]) -> Dict[str, Any]:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Calculate cyclomatic complexity
            cc_results = radon_cc.cc_visit(content)
            avg_cc = sum(r.complexity for r in cc_results) / len(cc_results) if cc_results else 0
            
            # Calculate maintainability index
            mi_score = radon_metrics.mi_visit(content, True)
            
            # Calculate Halstead metrics
            h_visit = radon_metrics.h_visit(content)
            halstead_volume = h_visit[0].volume if h_visit else 0
            
            return {
                'complexity': ComplexityMetrics(
                    cyclomatic=avg_cc,
                    halstead=halstead_volume,
                    maintainability=mi_score
                )
            }
        except Exception as e:
            raise AnalysisError(f"Failed to analyze complexity: {e}")
    
    def analyze_project(self, project_path: Path, file_results: Dict[Path, Dict[str, Any]]) -> Dict[str, Any]:
        if not file_results:
            return {'total_complexity': 0, 'avg_maintainability': 0}
            
        total_cc = sum(r['complexity'].cyclomatic for r in file_results.values())
        avg_mi = sum(r['complexity'].maintainability for r in file_results.values()) / len(file_results)
        return {'total_complexity': total_cc, 'avg_maintainability': avg_mi}