# AGENTS.md — Infrastructure Layer (`masar/infrastructure/`)

## 1. Role and Purpose

The **Infrastructure Layer** fulfills the abstract contracts declared by the Application layer. It handles all technical external concerns: relational database persistence via SQLAlchemy 2.0, file-system storage, cryptographic operations (PBKDF2 password hashing), and JWT token management. It isolates external libraries and I/O mechanisms from the core business domain.

---

## 2. Directory and Package Organization

```
masar/infrastructure/
├── database/                   # Relational Database Engine & ORM
│   ├── models.py               # SQLAlchemy 2.0 declarative ORM models (tables, foreign keys, relationships)
│   ├── session.py              # Engine creation, connection pooling, SessionLocal provider
│   └── __init__.py
├── repositories/               # Concrete persistence implementations
│   ├── database/               # SQLAlchemy SQL repositories (PostgreSQL & SQLite)
│   │   ├── journey_repository.py
│   │   ├── section_repository.py
│   │   ├── topic_repository.py
│   │   ├── note_repository.py
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   ├── action_proposal_repository.py
│   │   ├── document_repository.py
│   │   ├── profile_repository.py
│   │   └── __init__.py
│   ├── in_memory/              # In-memory dictionaries for testing and rapid verification
│   │   └── ...
│   ├── json/                   # JSON file-based repository adapter (journeys, sections, topics, notes, users)
│   │   └── ...
│   └── __init__.py
├── security/                   # Concrete cryptographic implementations
│   ├── password.py             # PBKDF2PasswordHasher (PBKDF2-HMAC-SHA256 with per-user salt)
│   ├── jwt_token.py            # PyJWTTokenService (stateless signed tokens with HS256)
│   └── __init__.py
├── ai/                         # Concrete AI provider implementations
│   ├── openrouter_provider.py  # OpenRouter / OpenAI-compatible HTTP provider with httpx
│   ├── mock_provider.py        # In-memory MockAIProvider for offline testing and verification
│   └── __init__.py
├── storage/                    # File-system storage engines
│   ├── json_storage.py         # Thread-safe JSON persistence with file locks
│   └── __init__.py
├── exceptions.py               # Infrastructure-specific storage and connection errors
├── __init__.py                 # Top-level infrastructure re-exports
└── AGENTS.md                   # This specification file
```

---

## 3. Architectural Rules & Constraints

1. **Dependency Direction (Inward Only):**
   - Infrastructure depends on the **Application Layer** (`masar.application.interfaces.*`) and **Domain Layer** (`masar.domain.models.*`).
   - Infrastructure must **NEVER** depend on, import, or reference the **Presentation Layer** (`masar.presentation.*`).
2. **Domain Entity <-> Database Model Isolation:**
   - SQLAlchemy ORM models (`JourneyModel`, `TopicModel`, etc.) are strictly private to the Infrastructure layer.
   - Repositories must always convert ORM models into pure Domain entities before returning data to the Application layer.
   - Raw database sessions, query objects, or ORM model instances must **never** escape the repository boundary.
3. **Pluggable Architecture:**
   - Repositories must be swappable via dependency injection (Composition Root in `masar/container.py` or FastAPI dependencies).
   - Switching from In-Memory to JSON or SQLite to PostgreSQL must require zero changes to Application services or Domain rules.
4. **Transaction & Connection Safety:**
   - Database operations must handle sessions safely. Commit on success, rollback on error, and guarantee proper session closure.
5. **Strict Typing:**
   - All repository methods, helper functions, and database session utilities must maintain full type annotations for `mypy --strict`.

---

## 4. Implementation Approach & Design Patterns

- **Data Mapper Pattern:**
  - `Database*Repository` classes translate incoming Domain entities to SQLAlchemy ORM records and map database query results back to pure Domain entities using explicit `to_domain()` and `from_domain()` conversions.
- **Adapter Pattern:**
  - `PBKDF2PasswordHasher` implements `PasswordHasher` using the Python standard library `hashlib.pbkdf2_hmac` with 100,000 iterations and cryptographic salts generated via `secrets.token_hex`.
  - `PyJWTTokenService` implements `TokenService` using `PyJWT` to encode/decode tokens with claims (`sub`, `exp`, `iat`).
- **Composite Repository Support:**
  - Multiple persistence adapters coexist in separate subpackages (`database/`, `in_memory/`, `json/`), allowing automated tests to run isolated unit tests in-memory while production uses the database engine.

---

## 5. Tools & Technologies

- **Python 3.12+:** Core language runtime.
- **SQLAlchemy 2.0:** High-performance ORM and Core SQL query builder (`Mapped`, `mapped_column`, `relationship`, `select`, `Session`).
- **Alembic:** Database schema migrations (`alembic.ini`, `alembic/versions/`).
- **SQLite / PostgreSQL:** Relational database backends supported via standard connection strings.
- **PyJWT:** JSON Web Token encoding, decoding, and signature verification.
- **`hashlib` & `secrets`:** Salted PBKDF2 cryptography.
- **`httpx`:** Synchronous HTTP client for REST API communication with OpenRouter with mock transport support for unit testing.

---

## 6. Maintenance & Evolution Mandate

Whenever new database tables, repositories, storage backends, or security mechanisms are implemented:
- Create Alembic migrations whenever altering ORM schemas under `masar/infrastructure/database/models.py`.
- Maintain strict conversion to/from pure Domain entities in all repository methods.
- Ensure zero leakage of SQLAlchemy models to Application or Presentation layers.
- **Update this `AGENTS.md` file** whenever infrastructure technologies, migration patterns, or storage strategies evolve.
