"""Debug script to test Tree-sitter Python parsing."""

import sys
from pathlib import Path
import traceback

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Test Tree-sitter import
    print("Testing Tree-sitter imports...")
    import tree_sitter
    print("✅ tree_sitter imported")
    
    import tree_sitter_python as ts_python
    print("✅ tree_sitter_python imported")
    
    # Test language creation
    language = tree_sitter.Language(ts_python.language())
    print("✅ Language created")
    
    # Test parser creation
    parser = tree_sitter.Parser(language)
    print("✅ Parser created with language")
    
    # Test simple parsing
    test_code = '''
def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.value = 42
'''
    
    tree = parser.parse(test_code.encode('utf-8'))
    print("✅ Code parsed successfully")
    print(f"   Root node type: {tree.root_node.type}")
    print(f"   Children count: {len(tree.root_node.children)}")
    
    # Test our parsers
    print("\nTesting our parser classes...")
    from code_assistant.core.types import LanguageType
    from code_assistant.parsers.tree_sitter_parser import TreeSitterParser
    
    ts_parser = TreeSitterParser(LanguageType.PYTHON)
    print("✅ TreeSitterParser created")
    
    from code_assistant.parsers.python_parser import PythonParser
    py_parser = PythonParser()
    print("✅ PythonParser created")
    
    print("\n🎉 All debug tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc() 