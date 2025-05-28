#!/usr/bin/env python3
"""
Environment Setup Script for Code Documentation Assistant

This script helps you set up your environment variables and validate your API keys.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    template_file = Path("env_template.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ env_template.txt not found. Please ensure it exists.")
        return False
    
    try:
        # Copy template to .env
        with open(template_file, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("📝 Please edit .env file and add your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def load_env_vars() -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    env_file = Path(".env")
    
    if not env_file.exists():
        return env_vars
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
    
    return env_vars


def validate_google_api_key(api_key: str) -> bool:
    """Validate Google API key format."""
    if not api_key or api_key == "your_google_api_key_here":
        return False
    
    # Basic format check for Google API keys
    if api_key.startswith("AIza") and len(api_key) == 39:
        return True
    
    print("⚠️  Google API key format seems incorrect. Expected format: AIza... (39 characters)")
    return False


def validate_openai_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format."""
    if not api_key or api_key == "your_openai_api_key_here":
        return True  # Optional key
    
    # Basic format check for OpenAI API keys
    if api_key.startswith("sk-") and len(api_key) >= 48:
        return True
    
    print("⚠️  OpenAI API key format seems incorrect. Expected format: sk-... (48+ characters)")
    return False


def test_google_api_connection(api_key: str) -> bool:
    """Test Google API connection."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try to list models to test connection
        models = list(genai.list_models())
        if models:
            print("✅ Google API connection successful")
            print(f"📊 Found {len(models)} available models")
            return True
        else:
            print("⚠️  Google API connected but no models found")
            return False
            
    except ImportError:
        print("⚠️  google-generativeai package not installed. Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Google API connection failed: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "python-dotenv",
        "langchain",
        "langchain-community",
        "langchain-google-genai",
        "chromadb",
        "google-generativeai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True


def main():
    """Main setup function."""
    print("🚀 Code Documentation Assistant - Environment Setup")
    print("=" * 60)
    
    # Step 1: Create .env file
    print("\n1️⃣  Setting up environment file...")
    if not create_env_file():
        return False
    
    # Step 2: Check dependencies
    print("\n2️⃣  Checking dependencies...")
    deps_ok = check_dependencies()
    
    # Step 3: Load and validate environment variables
    print("\n3️⃣  Validating environment variables...")
    env_vars = load_env_vars()
    
    if not env_vars:
        print("❌ No environment variables found. Please edit .env file.")
        return False
    
    # Validate Google API key (required)
    google_key = env_vars.get("GOOGLE_API_KEY", "")
    if not validate_google_api_key(google_key):
        print("❌ Google API key is required. Please add it to .env file.")
        print("🔗 Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    # Validate OpenAI API key (optional)
    openai_key = env_vars.get("OPENAI_API_KEY", "")
    validate_openai_api_key(openai_key)
    
    # Step 4: Test API connections
    print("\n4️⃣  Testing API connections...")
    if deps_ok:
        test_google_api_connection(google_key)
    
    # Step 5: Final status
    print("\n" + "=" * 60)
    print("🎉 Setup Summary:")
    print(f"✅ Environment file: {'Created' if Path('.env').exists() else 'Missing'}")
    print(f"✅ Dependencies: {'OK' if deps_ok else 'Missing packages'}")
    print(f"✅ Google API: {'Configured' if validate_google_api_key(google_key) else 'Not configured'}")
    print(f"✅ OpenAI API: {'Configured' if openai_key and openai_key != 'your_openai_api_key_here' else 'Optional - not configured'}")
    
    if deps_ok and validate_google_api_key(google_key):
        print("\n🚀 You're ready to start! Run:")
        print("   python main.py")
        print("   # or")
        print("   uvicorn main:app --reload")
        return True
    else:
        print("\n⚠️  Please fix the issues above before continuing.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 