import networkx as nx
from typing import Dict, List
from pathlib import Path
from .base_analyzer import BaseAnalyzer
from ..core.types import DependencyGraph, CodeElement
from ..parsers.parser_factory import ParserFactory

class DependencyAnalyzer(BaseAnalyzer):
    def analyze_file(self, file_path: Path, code_elements: List[CodeElement]) -> Dict[str, any]:
        graph = nx.DiGraph()
        parser = ParserFactory.create_parser_from_file(file_path)
        # Add nodes and edges based on imports, calls, etc.
        for elem in code_elements:
            graph.add_node(elem.name)
            for dep in elem.dependencies:
                graph.add_edge(elem.name, dep)
        return {'graph': DependencyGraph(nodes=list(graph.nodes), edges=list(graph.edges))}
    def analyze_project(self, project_path: Path, file_results: Dict[Path, Dict[str, any]]) -> Dict[str, any]:
        project_graph = nx.DiGraph()
        for res in file_results.values():
            project_graph = nx.compose(project_graph, nx.DiGraph(res['graph'].edges))
        cycles = list(nx.simple_cycles(project_graph))
        return {'project_graph': project_graph, 'cycles': cycles}
