# AGENTS.md — Application Layer (`masar/application/`)

## 1. Role and Purpose

The **Application Layer** coordinates application use cases, orchestrates domain entities, and defines abstract interfaces for persistence and security. It acts as the central mediator between the inner Domain layer and outer Infrastructure and Presentation layers, enforcing business workflows, authorization boundaries, and data transformation.

---

## 2. Directory and Package Organization

```
masar/application/
├── interfaces/                 # Abstractions and contracts (Dependency Inversion)
│   ├── repositories/           # Abstract Base Classes (ABCs) for data persistence
│   │   ├── journey_repository.py
│   │   ├── section_repository.py
│   │   ├── topic_repository.py
│   │   ├── note_repository.py
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   └── __init__.py
│   ├── security/               # Security and cryptography abstractions
│   │   ├── password_hasher.py  # ABC for password hashing and verification
│   │   ├── token_service.py    # ABC for JWT generation and verification
│   │   └── __init__.py
│   ├── ai/                     # AI provider abstractions
│   │   ├── ai_provider.py      # ABC for complete() and chat() LLM operations
│   │   └── __init__.py
│   └── __init__.py
├── schemas/                    # Pydantic v2 DTOs for input validation & output serialization
│   ├── journey.py              # JourneyCreate, JourneyUpdate, JourneyResponse
│   ├── section.py              # SectionCreate, SectionUpdate, SectionResponse
│   ├── topic.py                # TopicCreate, TopicUpdate, TopicResponse
│   ├── note.py                 # NoteCreate, NoteUpdate, NoteResponse
│   ├── progress.py             # JourneyProgressSchema, SectionProgressSchema
│   ├── user.py                 # UserCreate, UserLogin, UserResponse
│   ├── token.py                # TokenResponse, TokenData
│   ├── ai.py                   # ChatMessageSchema, CompletionRequestSchema, ChatRequestSchema, AIResponseSchema
│   ├── conversation.py         # ConversationCreate, ConversationDetail, MessageCreate/Response
│   └── __init__.py
├── services/                   # Application Use Cases & Workflows
│   ├── journey_service.py      # CRUD, filtering, and ownership verification for journeys
│   ├── section_service.py      # Section lifecycle with parent journey validation
│   ├── topic_service.py        # Topic lifecycle, completion toggling, ordering
│   ├── note_service.py         # Note CRUD and topic-parent association validation
│   ├── progress_service.py     # Aggregated progress calculations across roadmaps
│   ├── user_service.py         # User registration, authentication, JWT token issuance
│   ├── ai_service.py           # AI prompt & chat orchestration and domain validation
│   ├── conversation_service.py # Multi-turn conversation workflows, persistence, and auto-titling
│   └── __init__.py
├── __init__.py                 # Top-level application re-exports
└── AGENTS.md                   # This specification file
```

---

## 3. Architectural Rules & Constraints

1. **Dependency Direction (Strict Inward):**
   - The Application layer depends on the **Domain Layer** (`masar.domain.*`).
   - The Application layer must **NEVER** import or depend on concrete implementations from the **Infrastructure Layer** (`masar.infrastructure.*`) or the **Presentation Layer** (`masar.presentation.*`).
2. **Dependency Inversion Principle (DIP):**
   - Application services receive repository and security dependencies solely as abstract interfaces injected via their `__init__` constructors.
   - Services must never instantiate concrete repositories (e.g. SQLite, JSON, or In-Memory adapters).
3. **No Framework Coupling:**
   - Application services and interfaces must remain independent of delivery frameworks (FastAPI, Starlette, CLI frameworks). They do not take HTTP `Request` or `Response` objects as arguments.
4. **Data Ownership & Cascading Authorization:**
   - Every service operation accessing or mutating user data must enforce ownership guards (`user_id` validation).
   - Child entities (`Section`, `Topic`, `Note`) must verify that their ancestor chain belongs to the calling user before allowing mutations or deletions.
5. **Separation of Concerns:**
   - Each use case service is housed in its own file under `services/`.
   - Each repository interface is housed in its own file under `interfaces/repositories/`.
   - Each DTO schema is housed in its own file under `schemas/`.
6. **Strict Typing:**
   - 100% type coverage with type hints on all function parameters, return types, and class attributes to pass `mypy --strict`.

---

## 4. Implementation Approach & Design Patterns

- **Application Services / Use Case Interactors:**
  - Services orchestrate multi-step business transactions: validating inputs, invoking repository queries, executing domain rules, and saving updated entities.
- **Pydantic Validation & Serialization (DTOs):**
  - Application schemas validate incoming payload shapes (`extra="forbid"`, string length constraints, positive IDs) before passing data to domain models.
- **Repository Pattern (Abstract Base Classes):**
  - Uses Python's `abc.ABC` and `@abstractmethod` to define standard query contracts (`save`, `get_by_id`, `list_by_*`, `update`, `delete`).
- **Cryptographic Abstraction:**
  - `PasswordHasher` and `TokenService` decouple authentication workflows from specific hashing algorithms or JWT libraries.

---

## 5. Tools & Technologies

- **Python 3.12+:** Core language runtime.
- **`abc`:** Abstract Base Classes for repository and service interfaces.
- **Pydantic v2:** High-performance validation schemas and data transfer objects (`BaseModel`, `Field`, `ConfigDict`).
- **`typing`:** Generic protocols and strict type signatures.
- **`mypy --strict`:** Static analysis verification.

---

## 6. Maintenance & Evolution Mandate

Whenever a new use case, repository method, DTO schema, or security contract is added:
- Define the abstract contract under `masar/application/interfaces/` before creating infrastructure implementations.
- Enforce strict inward dependency (no infrastructure imports).
- Verify cascading user authorization guards on any new mutating service method.
- **Update this `AGENTS.md` file** whenever new service patterns, schemas, or architectural constraints are introduced.
