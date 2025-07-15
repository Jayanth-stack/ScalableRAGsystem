import sys
from pathlib import Path
from code_assistant.analyzers.analyzer_factory import AnalyzerFactory
from code_assistant.parsers.parser_factory import ParserFactory

sys.path.insert(0, str(Path(__file__).parent))

def test_analyzers():
    sample_path = Path('sample_repos/sample_python_project/main.py')
    parser = ParserFactory.create_parser_from_file(sample_path)
    elements = parser.parse_file(sample_path).code_elements
    analyzers = ['complexity', 'dependency', 'pattern', 'security', 'performance']
    results = {}
    for name in analyzers:
        analyzer = AnalyzerFactory.create_analyzer(name)
        results[name] = analyzer.analyze_file(sample_path, elements)
    print(results)

if __name__ == '__main__':
    test_analyzers()
