# 🤖 Code Documentation Assistant

A sophisticated RAG-based system for analyzing, documenting, and understanding codebases using AI. Built with FastAPI, LangChain, and Google Gemini.

## 🌟 Features

- **Multi-Language Code Analysis**: Support for Python, JavaScript, TypeScript, Java, Go, Rust, and more
- **AST-Based Parsing**: Deep code understanding using Abstract Syntax Trees
- **AI-Powered Documentation**: Automatic generation of comprehensive documentation
- **Semantic Code Search**: Find similar code patterns and functions
- **API Discovery**: Automatically detect and document API endpoints
- **Code Quality Analysis**: Complexity metrics and improvement suggestions
- **Git Integration**: Analyze repositories and track changes
- **Real-time Processing**: Fast, concurrent file analysis

## 🏗️ Architecture

```
Code Documentation Assistant
├── Core RAG System (Google Gemini + ChromaDB)
├── AST Parser (Tree-sitter)
├── Code Analyzer (Multi-language)
├── Embedding Engine (Hybrid: Semantic + Code)
├── Vector Store (ChromaDB + Optional Pinecone)
├── API Layer (FastAPI)
└── Frontend (Coming Soon)
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd ScalableRAGsystem
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Run the setup script
python setup_environment.py
```

This will:
- Create a `.env` file from the template
- Check all dependencies
- Validate your API keys
- Test connections

### 5. Add Your API Keys

Edit the `.env` file and add your actual API keys:

```bash
# Required
GOOGLE_API_KEY=your_actual_google_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
```

**Get API Keys:**
- 🔑 **Google Gemini**: [Get API Key](https://makersuite.google.com/app/apikey)
- 🔑 **OpenAI** (Optional): [Get API Key](https://platform.openai.com/api-keys)
- 🔑 **Pinecone** (Optional): [Get API Key](https://app.pinecone.io/)

### 6. Run the Application

```bash
# Start the server
uvicorn main:app --reload

# Or run directly
python main.py
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

## 📁 Project Structure

```
ScalableRAGsystem/
├── code_assistant/              # Main package
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── types.py           # Data models & types
│   │   └── __init__.py
│   ├── parsers/               # Code parsers (AST, Tree-sitter)
│   ├── analyzers/             # Code analysis engines
│   ├── embeddings/            # Embedding systems
│   ├── api/                   # API endpoints
│   ├── models/                # Database models
│   ├── utils/                 # Utilities
│   └── tests/                 # Test suite
├── sample_repos/              # Test data
│   └── sample_python_project/ # Sample Python code
├── requirements.txt           # Dependencies
├── main.py                    # Original RAG system
├── setup_environment.py       # Environment setup script
├── env_template.txt           # Environment template
└── README.md                  # This file
```

## 🔧 Configuration

The system uses environment variables for configuration. Key settings:

```bash
# API Keys
GOOGLE_API_KEY=required
OPENAI_API_KEY=optional
PINECONE_API_KEY=optional

# Application
DEBUG=false
DEV_MODE=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./code_assistant.db
REDIS_URL=redis://localhost:6379

# Performance
MAX_CONCURRENT_FILES=10
CACHE_TTL_HOURS=24
```

## 🧪 Testing

Test with the sample Python project:

```bash
# The system includes sample code in sample_repos/
# This demonstrates various Python constructs:
# - Classes and inheritance
# - Functions with type hints
# - Decorators
# - Documentation strings
# - Error handling
```

## 📊 Current Status

### ✅ Phase 1 Complete: Foundation & Planning
- [x] Project architecture design
- [x] Enhanced requirements and dependencies
- [x] Configuration management system
- [x] Type definitions and data models
- [x] Exception handling framework
- [x] Sample test data
- [x] Environment setup automation

### 🚧 Phase 2: Core RAG Enhancement (Next)
- [ ] AST parsing with Tree-sitter
- [ ] Code-specific document processing
- [ ] Multi-modal embeddings
- [ ] Enhanced vector storage
- [ ] Code-aware chunking strategies

### 🔮 Future Phases
- [ ] Advanced code analysis
- [ ] API layer implementation
- [ ] Frontend development
- [ ] Production deployment

## 🛠️ Development

### Adding New Languages

1. Add language to `supported_languages` in `config.py`
2. Add file extensions to `get_language_extensions()`
3. Install Tree-sitter grammar: `pip install tree-sitter-<language>`
4. Implement language-specific parser

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest code_assistant/tests/

# With coverage
pytest --cov=code_assistant
```

### Code Quality

```bash
# Format code
black code_assistant/

# Type checking
mypy code_assistant/

# Linting
flake8 code_assistant/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**2. API Key Issues**
```bash
# Run the setup script to validate
python setup_environment.py
```

**3. Database Issues**
```bash
# Remove and recreate database
rm code_assistant.db
rm -rf chroma_db/
```

**4. Permission Issues**
```bash
# Make setup script executable
chmod +x setup_environment.py
```

### Getting Help

- 📖 Check the [documentation](http://localhost:8000/docs) when running
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

## 🎯 Next Steps

1. **Complete Phase 2**: Implement AST parsing and code analysis
2. **Add More Languages**: Extend support beyond Python
3. **Build Frontend**: Create a web interface
4. **Deploy**: Set up production deployment
5. **Scale**: Add distributed processing capabilities

---

**Happy Coding! 🚀** 