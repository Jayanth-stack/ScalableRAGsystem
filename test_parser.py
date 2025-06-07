"""Test script for the AST parsing system."""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from code_assistant.parsers.parser_factory import ParserFactory
from code_assistant.core.types import LanguageType


def test_parser_creation():
    """Test parser creation for different languages."""
    print("🧪 Testing Parser Creation...")
    
    # Test Python parser creation
    try:
        python_parser = ParserFactory.create_parser(LanguageType.PYTHON)
        print(f"✅ Python parser created: {type(python_parser).__name__}")
    except Exception as e:
        print(f"❌ Failed to create Python parser: {e}")
    
    # Test file-based parser creation
    sample_file = Path("sample_repos/sample_python_project/main.py")
    if sample_file.exists():
        try:
            parser = ParserFactory.create_parser_from_file(sample_file)
            print(f"✅ Parser created for {sample_file}: {type(parser).__name__}")
        except Exception as e:
            print(f"❌ Failed to create parser for {sample_file}: {e}")
    else:
        print(f"⚠️  Sample file not found: {sample_file}")


def test_python_parsing():
    """Test parsing of Python files."""
    print("\n🐍 Testing Python File Parsing...")
    
    # Test main.py
    main_file = Path("sample_repos/sample_python_project/main.py")
    if main_file.exists():
        try:
            parser = ParserFactory.create_parser(LanguageType.PYTHON)
            result = parser.parse_file(main_file)
            
            if result.success:
                print(f"✅ Successfully parsed {main_file}")
                print(f"   📊 Found {len(result.code_elements)} code elements")
                
                # Show element breakdown
                element_types = {}
                for element in result.code_elements:
                    elem_type = element.element_type  # Already a string
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                
                for elem_type, count in element_types.items():
                    print(f"   - {elem_type}: {count}")
                
                # Show some specific elements
                functions = [e for e in result.code_elements if e.element_type == 'function']
                if functions:
                    print(f"\n   🔧 Functions found:")
                    for func in functions[:3]:  # Show first 3
                        complexity = f" (complexity: {func.complexity_score:.1f})" if func.complexity_score else ""
                        docstring = " [has docstring]" if func.docstring else " [no docstring]"
                        print(f"   - {func.name}{complexity}{docstring}")
                
                classes = [e for e in result.code_elements if e.element_type == 'class']
                if classes:
                    print(f"\n   📦 Classes found:")
                    for cls in classes:
                        inheritance = f" extends {', '.join(cls.dependencies)}" if cls.dependencies else ""
                        print(f"   - {cls.name}{inheritance}")
                
                # Show metrics if available
                if result.metrics:
                    print(f"\n   📈 Metrics:")
                    for key, value in result.metrics.items():
                        if isinstance(value, dict):
                            print(f"   - {key}:")
                            for sub_key, sub_value in value.items():
                                print(f"     • {sub_key}: {sub_value}")
                        else:
                            print(f"   - {key}: {value}")
                
                # Show issues if any
                if result.issues:
                    print(f"\n   ⚠️  Issues found:")
                    for issue in result.issues[:3]:  # Show first 3
                        print(f"   - {issue['type']}: {issue['message']}")
                
            else:
                print(f"❌ Failed to parse {main_file}: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Exception parsing {main_file}: {e}")
    else:
        print(f"⚠️  Sample file not found: {main_file}")


def test_utils_parsing():
    """Test parsing of utils.py file."""
    print("\n🛠️  Testing utils.py Parsing...")
    
    utils_file = Path("sample_repos/sample_python_project/utils.py")
    if utils_file.exists():
        try:
            parser = ParserFactory.create_parser(LanguageType.PYTHON)
            result = parser.parse_file(utils_file)
            
            if result.success:
                print(f"✅ Successfully parsed {utils_file}")
                print(f"   📊 Found {len(result.code_elements)} code elements")
                
                # Show decorators found
                decorators = [e for e in result.code_elements if e.decorators]
                if decorators:
                    print(f"\n   🎨 Functions with decorators:")
                    for elem in decorators:
                        print(f"   - {elem.name}: {', '.join(elem.decorators)}")
                
                # Show functions with type hints
                typed_functions = [e for e in result.code_elements 
                                 if e.element_type == 'function' and e.return_type]
                if typed_functions:
                    print(f"\n   🏷️  Functions with type hints:")
                    for func in typed_functions:
                        print(f"   - {func.name} -> {func.return_type}")
                
            else:
                print(f"❌ Failed to parse {utils_file}: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Exception parsing {utils_file}: {e}")
    else:
        print(f"⚠️  Sample file not found: {utils_file}")


def test_supported_languages():
    """Test supported languages and extensions."""
    print("\n🌐 Testing Supported Languages...")
    
    languages = ParserFactory.get_supported_languages()
    print(f"✅ Supported languages ({len(languages)}):")
    for lang in languages:
        print(f"   - {lang.value}")
    
    extensions = ParserFactory.get_supported_extensions()
    print(f"\n✅ Supported extensions ({len(extensions)}):")
    for ext in sorted(extensions):
        lang = ParserFactory.detect_language(Path(f"test{ext}"))
        print(f"   - {ext} → {lang.value if lang else 'unknown'}")


def main():
    """Run all tests."""
    print("🚀 Starting AST Parser Tests\n")
    
    try:
        test_parser_creation()
        test_python_parsing()
        test_utils_parsing()
        test_supported_languages()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 