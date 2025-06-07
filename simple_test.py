"""Simple test to isolate parsing issues."""

import sys
from pathlib import Path
import traceback

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from code_assistant.parsers.parser_factory import ParserFactory
    from code_assistant.core.types import LanguageType
    
    print("Creating Python parser...")
    parser = ParserFactory.create_parser(LanguageType.PYTHON)
    print(f"Parser created: {type(parser).__name__}")
    
    # Test with simple content first
    print("\nTesting with simple content...")
    simple_code = '''
def hello():
    """A simple function."""
    print("Hello!")
    return True
'''
    
    elements = parser.parse_content(simple_code)
    print(f"✅ Simple parsing successful! Found {len(elements)} elements")
    for elem in elements:
        print(f"  - {elem.element_type}: {elem.name}")
    
    # Test with file
    print("\nTesting with file...")
    main_file = Path("sample_repos/sample_python_project/main.py")
    if main_file.exists():
        result = parser.parse_file(main_file)
        if result.success:
            print(f"✅ File parsing successful! Found {len(result.code_elements)} elements")
        else:
            print(f"❌ File parsing failed: {result.error_message}")
    else:
        print("⚠️  Sample file not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc() 