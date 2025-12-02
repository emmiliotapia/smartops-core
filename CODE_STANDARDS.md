# Code Standards - SmartOps Core

## Language Rules

### Code & Commits: English Only
- ✅ Function names: English
- ✅ Variable names: English  
- ✅ Docstrings: English
- ✅ Comments: English
- ✅ Log messages: English
- ✅ Commit messages: English (with scope prefixes)
- ❌ No special characters (á, é, ñ, etc)

Example commit:
```
refactor: Convert code to English for clean architecture
```

### Documentation: English or Colored Text
- ✅ README.md: English
- ✅ API docs: English
- ✅ Terminal output: Can use colors + emojis (for humans)
- ✅ Status reports: English + visual formatting

## Architecture Principles

### Clean Architecture Layers
```
Router (HTTP)
    ↓
Service (Business Logic)
    ↓
Models (Data)
    ↓
Database (Persistence)
```

### Each Layer Has Single Responsibility

**Router Layer (app/routers/)**
- HTTP request/response handling
- Input validation (via Pydantic schemas)
- Error responses
- FastAPI decorators

**Service Layer (app/services/)**
- Business logic encapsulation
- External API calls (OpenAI, etc)
- Data processing
- Independent of HTTP

**Models Layer (app/modules/demo/)**
- SQLAlchemy ORM models
- Data structures
- Database constraints

**Schema Layer (app/modules/demo/)**
- Pydantic DTOs
- Request/response validation
- Type checking

## File Structure

```
app/
├── main.py              # FastAPI app entry
├── database.py          # DB connection config
├── core/                # Core configurations
├── modules/demo/
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── constants.py     # Demo constants
├── routers/demo.py      # HTTP endpoints
└── services/
    └── demo_rag.py      # RAG business logic

tests/
├── conftest.py          # Test fixtures
├── test_schemas.py      # Schema validation
├── test_database.py     # ORM tests
├── test_rag_service.py  # Service logic
├── test_endpoints.py    # HTTP tests
└── test_integration.py  # End-to-end tests
```

## Naming Conventions

### Classes
- Services: `DemoRAGService`, `DocumentProcessor`
- Models: `DemoSession`, `DemoVector`
- Schemas: `MessageRequest`, `NeuralizerResponse`

### Functions
- Private: `_get_embedding()`, `_chunk_text()`
- Public: `index_demo_document()`, `query_demo()`
- Handlers: `upload_demo()`, `send_message()`

### Variables
- Constants: `MAX_CHUNK_SIZE`, `NEURALIZER_SECRET`
- Regular: `session_id`, `file_path`, `embedding`
- Booleans: `is_active`, `has_content`

## Docstring Format

```python
def function_name(arg1: str, arg2: int) -> dict:
    """
    One-line summary.

    Extended description if needed.

    Args:
        arg1: Description.
        arg2: Description.

    Returns:
        Description of return value.

    Raises:
        ValueError: When validation fails.
    """
    pass
```

## Git Commit Conventions

### Format
```
<type>: <subject>

<body (optional)>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code reorganization
- `docs`: Documentation changes
- `test`: Test additions
- `chore`: Maintenance tasks
- `cleanup`: Remove unused code

### Examples
```
feat: Add RAG semantic search endpoint
fix: Handle empty PDF documents
refactor: Convert code to English for clean architecture
cleanup: Remove deprecated test scripts
docs: Update API documentation
```

## No Hardcoded Secrets

- ✅ All secrets in `.env`
- ✅ Use `os.getenv()` to read
- ✅ Never commit `.env` (in `.gitignore`)
- ✅ Provide `.env.example` template

## Testing Standards

- Unit tests for each layer
- Mock external APIs (OpenAI)
- Use pytest + fixtures
- Aim for >80% coverage
- Test file name: `test_<module>.py`

## Code Review Checklist

- [ ] English only (no special chars)
- [ ] Single responsibility per class
- [ ] Proper error handling
- [ ] Meaningful variable names
- [ ] Docstrings present
- [ ] No hardcoded secrets
- [ ] Tests passing
- [ ] Git history clean
