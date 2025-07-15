from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

from ..core.types import AnalysisResult, CodeElement
from ..core.exceptions import AnalysisError

class BaseAnalyzer(ABC):
    

    @abstractmethod
    def analyze_file(self, file_path: Path, code_elements: List[CodeElement]) -> Dict[str, Any]:
        
        pass

    @abstractmethod
    def analyze_project(self, project_path: Path, file_results: Dict[Path, Dict[str, Any]]) -> Dict[str, Any]:
        
        pass
 