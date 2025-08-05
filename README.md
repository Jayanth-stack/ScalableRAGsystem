# 🤖 Code Documentation Assistant

A sophisticated RAG-based system for analyzing, documenting, and understanding codebases using AI. Built with FastAPI, LangChain, and Google Gemini.

## 🌟 Features

- **Multi-Language Code Analysis**: Support for Python, JavaScript, TypeScript, Java, Go, Rust, C++, C
- **AST-Based Parsing**: Deep code understanding using Tree-sitter parsers
- **Intelligent Code Chunking**: Semantic-aware chunking with 5 different strategies
- **Multi-Model Embeddings**: Google Embedding, CodeBERT, Sentence Transformers
- **Vector Database**: ChromaDB integration with persistent storage
- **Semantic Code Search**: Find similar code patterns and functions
- **AI-Powered Documentation**: Automatic generation of comprehensive documentation
- **API Discovery**: Automatically detect and document API endpoints
- **Code Quality Analysis**: Complexity metrics and improvement suggestions
- **Git Integration**: Analyze repositories and track changes
- **Real-time Processing**: Fast, concurrent file analysis (133+ embeddings/sec)

## 🏗️ Architecture

```
Code Documentation Assistant
├── Core RAG System (Google Gemini + ChromaDB)
│   ├── AST Parser (Tree-sitter) ✅
│   ├── Intelligent Chunker ✅
│   ├── Multi-Model Embedder ✅
│   └── Vector Store (ChromaDB) ✅
├── Code Analyzer (Multi-language)
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
# Test the RAG pipeline
python test_complete_rag.py

# Test chunking and embeddings
python test_chunking.py

# Start the server (when API is ready)
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

## 📁 Project Structure

```
ScalableRAGsystem/
├── code_assistant/              # Main package
│   ├── core/                   # Core functionality ✅
│   │   ├── config.py          # Configuration management
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── types.py           # Data models & types
│   │   └── __init__.py
│   ├── parsers/               # Code parsers (AST, Tree-sitter) ✅
│   │   ├── base_parser.py     # Abstract parser base
│   │   ├── tree_sitter_parser.py # Tree-sitter implementation
│   │   ├── python_parser.py   # Python-specific enhancements
│   │   └── parser_factory.py  # Parser factory
│   ├── embeddings/            # Embedding systems ✅
│   │   ├── chunker.py         # Intelligent code chunking
│   │   ├── embedder.py        # Multi-model embedding generation
│   │   └── vector_store.py    # ChromaDB vector storage
│   ├── analyzers/             # Code analysis engines
│   ├── api/                   # API endpoints
│   ├── models/                # Database models
│   ├── utils/                 # Utilities
│   └── tests/                 # Test suite
├── sample_repos/              # Test data ✅
│   └── sample_python_project/ # Sample Python code
├── requirements.txt           # Dependencies (77 packages)
├── main.py                    # Original RAG system
├── test_complete_rag.py       # Complete pipeline test ✅
├── test_chunking.py           # Chunking & embedding test ✅
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
# Test the complete RAG pipeline
python test_complete_rag.py

# Test individual components
python test_chunking.py

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
- [x] Enhanced requirements and dependencies (77 packages)
- [x] Configuration management system
- [x] Type definitions and data models (15+ Pydantic models)
- [x] Exception handling framework
- [x] Sample test data
- [x] Environment setup automation

### ✅ Phase 2 Complete: Enhanced RAG Features
- [x] **AST Parsing Engine**: Tree-sitter multi-language parser (8 languages)
  - Multi-language support (Python, JavaScript, TypeScript, Java, Go, Rust, C++, C)
  - Complexity analysis and type hint extraction
  - Design pattern detection and inheritance analysis
  - Factory pattern for parser creation
- [x] **Intelligent Code Chunking**: 5 chunking strategies
  - Function-based, Class-based, Semantic blocks, Sliding window, Hybrid
  - Context-aware chunking with metadata preservation
  - Smart merging and docstring extraction
  - 70 chunks generated from 2 sample files
- [x] **Multi-Model Embeddings**: 3 embedding models supported
  - Google Text Embedding (768D), Sentence Transformers (384D), CodeBERT (768D)
  - Context-aware embedding with metadata integration
  - Batch processing (133+ embeddings/sec)
  - Async processing and caching
- [x] **Vector Database**: ChromaDB integration
  - Persistent storage with metadata filtering
  - Semantic search with similarity thresholds
  - Language and element type filtering
  - Production-ready with error handling

<<<<<<< HEAD
### ✅ Phase 3 Complete: Code Analysis Engine
- [x] Advanced complexity analysis
- [x] Dependency tracking and relationship mapping
- [x] Code pattern detection and best practices
- [x] Security vulnerability scanning
- [x] Performance optimization suggestions

### ✅ Phase 4 Complete: API Layer Implementation
- [x] Core API endpoints (/analyze, /search, /document, /metrics)
- [x] Request/Response models with Pydantic validation
- [x] Background tasks for async processing
- [x] Auto-generated OpenAPI documentation
- [x] Health check and status endpoints

### ✅ Phase 5 Complete: Frontend Development
- [x] Modern Next.js 14+ with TypeScript
- [x] Interactive dashboards for all features
- [x] Real-time code analysis interface
- [x] Semantic search with syntax highlighting
- [x] Documentation generator with live preview
- [x] Metrics visualization with charts
- [x] Responsive design with Tailwind CSS
- [x] API integration with React Query

### 🔮 Future Phases
- [ ] Production deployment
- [ ] Authentication & rate limiting
- [ ] Websocket progress updates

## 🎯 System Performance

**Current Benchmarks:**
- **Parsing**: 49+ code elements from complex Python files
- **Chunking**: 70 chunks from 2 files with rich metadata
- **Embedding**: 133+ embeddings/second
- **Search**: Sub-second semantic search responses
- **Languages**: 8 programming languages supported
- **File Extensions**: 19+ file extensions recognized

## 🎯 System Performance

**Current Benchmarks:**
- **Parsing**: 49+ code elements from complex Python files
- **Chunking**: 70 chunks from 2 files with rich metadata
- **Embedding**: 133+ embeddings/second
- **Search**: Sub-second semantic search responses
- **Languages**: 8 programming languages supported
- **File Extensions**: 19+ file extensions recognized

## 🛠️ Development

### Adding New Languages

1. Add language to `LanguageType` enum in `core/types.py`
2. Add file extensions to parser factory
3. Install Tree-sitter grammar: `pip install tree-sitter-<language>`
4. Implement language-specific parser enhancements

### Running Tests

```bash
# Test complete RAG pipeline
python test_complete_rag.py

# Test chunking and embeddings
python test_chunking.py

# Install test dependencies
pip install pytest pytest-cov

# Run tests (when test suite is complete)
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

**3. Tree-sitter Installation Issues**
```bash
# Reinstall tree-sitter parsers
pip uninstall tree-sitter tree-sitter-python tree-sitter-javascript
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
```

**4. ChromaDB Issues**
```bash
# Remove and recreate vector database
rm -rf chroma_db/ test_chroma_db/
python test_complete_rag.py
```

**5. Embedding Model Download**
```bash
# The first run downloads models automatically
# Ensure stable internet connection for model downloads
```

### Getting Help

- 📖 Check the test files for usage examples
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

## 🎯 Next Steps

1. **Start Phase 3**: Implement advanced code analysis engine
2. **Add More Languages**: Extend Tree-sitter parser support
3. **Build API Layer**: Create FastAPI endpoints
4. **Build Frontend**: Create a web interface
5. **Deploy**: Set up production deployment
6. **Scale**: Add distributed processing capabilities

## 🔬 Technical Highlights

**Advanced Features Implemented:**
- **AST-Aware Chunking**: Preserves code semantics and structure
- **Multi-Modal Embeddings**: Combines code content with metadata context
- **Production-Ready**: Error handling, retry logic, caching, async processing
- **Extensible Architecture**: Factory patterns and strategy patterns for flexibility
- **Type Safety**: Comprehensive Pydantic models with validation
- **Performance Optimized**: Batch processing and concurrent execution

---

**Happy Coding! 🚀** Built with ❤️ for developers who love clean, well-documented code. 