from typing import Dict, List, Any
from pathlib import Path
from bandit.core import manager as bandit_manager
from .base_analyzer import BaseAnalyzer
from ..core.types import CodeElement

class SecurityAnalyzer(BaseAnalyzer):
    def analyze_file(self, file_path: Path, code_elements: List[CodeElement]) -> Dict[str, Any]:
        b_mgr = bandit_manager.BanditManager()
        b_mgr.discover_files([str(file_path)])
        b_mgr.run_tests()
        issues = b_mgr.get_issue_list()
        return {'vulnerabilities': [issue.text for issue in issues]}
    def analyze_project(self, project_path: Path, file_results: Dict[Path, Dict[str, Any]]) -> Dict[str, Any]:
        all_vulns = []
        for res in file_results.values():
            all_vulns.extend(res['vulnerabilities'])
        return {'total_vulnerabilities': len(all_vulns), 'critical': sum(1 for v in all_vulns if 'high' in v.lower())}
 