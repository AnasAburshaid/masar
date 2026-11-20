# AGENTS.md — Domain Layer (`masar/domain/`)

## 1. Role and Purpose

The **Domain Layer** is the foundational core of the Masar learning tracker platform. It encapsulates the enterprise business concepts, entities, value objects, domain rules, and domain-specific exceptions. It defines *what* the system does and represents from a business perspective, completely decoupled from *how* data is stored, delivered, or displayed.

---

## 2. Directory and Package Organization

```
masar/domain/
├── models/                     # Core domain entities and value objects
│   ├── journey.py              # Journey entity (root of learning roadmap)
│   ├── section.py              # Section entity (milestone partition inside a journey)
│   ├── topic.py                # Topic entity (individual subject to study/master)
│   ├── note.py                 # Note entity (developer observations/insights attached to a topic)
│   ├── progress.py             # Progress value object (calculation results, percentages, completion status)
│   ├── user.py                 # User entity (account identity, email, password hash)
│   ├── ai.py                   # AI value objects (ChatMessage, AIUsage, AIResponse)
│   ├── conversation.py         # Conversation and ConversationMessage entities
│   ├── action.py               # ProposedAction, ActionResult, ActionProposal entities
│   ├── document.py             # Document entity (uploaded learning materials, PDF/MD/TXT)
│   ├── profile.py              # ProfileItem entity and LearningProfile aggregate (skills, goals, levels)
│   └── __init__.py             # Re-exports of all domain models
├── exceptions/                 # Granular domain exception hierarchy
│   ├── base.py                 # DomainError base class and semantic classifications
│   ├── journey.py              # JourneyNotFound, JourneyTitleRequired, etc.
│   ├── section.py              # SectionNotFound, SectionTitleRequired, etc.
│   ├── topic.py                # TopicNotFound, InvalidTopicStatus, etc.
│   ├── note.py                 # NoteNotFound, NoteContentRequired, etc.
│   ├── user.py                 # UserNotFound, UserAlreadyExists, InvalidCredentials, etc.
│   ├── ai.py                   # AIError, AIAuthenticationError, AIRateLimitError, AITimeoutError, etc.
│   ├── conversation.py         # ConversationNotFound, ConversationAccessDenied, etc.
│   ├── action.py               # UnknownToolError, ActionProposalNotFoundError, ActionExecutionError, etc.
│   ├── document.py             # DocumentError, UnsupportedFileType, FileTooLarge, etc.
│   ├── profile.py              # ProfileError, ProfileItemNotFoundError, ProfileAccessDeniedError
│   ├── storage.py              # Domain-level persistence failure exceptions
│   └── __init__.py             # Clean re-exports of all domain exceptions
├── types.py                    # Domain enums and type aliases (e.g., TopicStatus)
├── __init__.py                 # Top-level domain re-exports
└── AGENTS.md                   # This specification file
```

---

## 3. Architectural Rules & Constraints

1. **Strict Inward Dependency (Zero Coupling Outward):**
   - The Domain Layer must **NEVER** import from the Application layer, Infrastructure layer, or Presentation layer.
   - Any dependency on frameworks (FastAPI, SQLAlchemy, Pydantic, Click) is strictly forbidden in the Domain.
2. **Standard Library Only:**
   - The domain must rely solely on the Python Standard Library (`dataclasses`, `datetime`, `enum`, `typing`, `abc`).
3. **No Persistence or Network Knowledge:**
   - Domain models must have no knowledge of database tables, foreign key constraints, JSON formats, or HTTP request/response schemas.
4. **Data Integrity & Invariants:**
   - Entities must protect their invariants. Validation of business rules (e.g. non-empty titles, valid topic statuses, progress bounds `0.0 <= percentage <= 100.0`) must be enforced within the domain.
5. **Separation of Files:**
   - Every domain concept has its own file. Do not combine multiple domain models into a single file.
6. **Strict Typing:**
   - All models, attributes, methods, and functions must be fully type-annotated to pass `mypy --strict`.

---

## 4. Implementation Approach & Design Patterns

- **Entities vs. Value Objects:**
  - *Entities* (`Journey`, `Section`, `Topic`, `Note`, `User`): Defined with unique identity (`id: Optional[int]`) and lifecycle tracking (`created_at`, `updated_at`).
  - *Value Objects* (`Progress`): Immutable data representations defined by their attributes rather than an identity, representing calculations like completion percentages and topic counters.
- **Granular Exception Hierarchy:**
  - All domain exceptions inherit from `DomainError`.
  - Semantic categories (`EntityNotFoundError`, `ValidationError`, `ConflictError`, `UnauthorizedError`, `ForbiddenError`) allow outer layers (e.g. FastAPI exception handlers) to map domain errors to HTTP status codes cleanly without domain leakage.
- **State Encapsulation:**
  - Topic statuses are represented via the `TopicStatus` enum (`NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`).
  - Topic transition methods ensure safe mutations without arbitrary string assignments.

---

## 5. Tools & Technologies

- **Python 3.12+:** Core runtime.
- **`dataclasses`:** For lightweight entity modeling with default values and type enforcement.
- **`typing`:** `Optional`, `List`, `Dict`, `Any`, `Literal`, `Union` for static type safety.
- **`datetime` (UTC):** Standardized timestamp management across all models (`datetime.now(timezone.utc)`).
- **`mypy --strict`:** Automated verification to guarantee zero type errors.

---

## 6. Maintenance & Evolution Mandate

Whenever a new domain concept, entity, rule, or exception is introduced, or an existing one is modified:
- Ensure it resides in its dedicated file under `masar/domain/models/` or `masar/domain/exceptions/`.
- Verify zero imports from outer layers.
- Update `masar/domain/models/__init__.py` or `masar/domain/exceptions/__init__.py`.
- **Update this `AGENTS.md` file** to reflect any new invariants, rules, or architectural evolutions.
