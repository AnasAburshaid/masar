# AGENTS.md — Presentation Layer (`masar/presentation/`)

## 1. Role and Purpose

The **Presentation Layer** serves as the user-facing entry point to the Masar backend application. It handles user requests, coordinates with application services, enforces transport protocols, and serializes responses. It includes both the **FastAPI REST API** for web and mobile clients and the **Interactive Python CLI**.

---

## 2. Directory and Package Organization

```
masar/presentation/
├── api/                        # FastAPI REST API implementation
│   ├── routes/                 # Endpoint routers organized by business domain
│   │   ├── auth.py             # /auth/register, /auth/login, /auth/me
│   │   ├── journeys.py         # /journeys (CRUD for user-owned roadmaps)
│   │   ├── sections.py         # /sections & /journeys/{journey_id}/sections
│   │   ├── topics.py           # /topics & status toggles (/complete, /pending)
│   │   ├── notes.py            # /notes & /topics/{topic_id}/notes
│   │   ├── conversations.py    # /conversations (CRUD & multi-turn /messages chat)
│   │   ├── progress.py         # /journeys/{journey_id}/progress & /sections/{id}/progress
│   │   ├── root.py             # / (API metadata) & /health (health check)
│   │   └── __init__.py
│   ├── app.py                  # FastAPI factory (CORS, router registration, exception handlers)
│   ├── dependencies.py         # FastAPI dependency injection (services, repositories, get_current_user)
│   └── __init__.py
├── cli.py                      # Interactive Command-Line Interface (terminal UX)
├── __init__.py                 # Top-level presentation re-exports
└── AGENTS.md                   # This specification file
```

---

## 3. Architectural Rules & Constraints

1. **Dependency Direction (Inward Only):**
   - Presentation depends on the **Application Layer** (`masar.application.services.*`, `masar.application.schemas.*`) and **Domain Layer** (`masar.domain.models.*`, `masar.domain.exceptions.*`).
   - Presentation must **NEVER** import directly from concrete `masar.infrastructure.repositories` inside route handlers. Repositories and infrastructure adapters are injected solely via `dependencies.py` or the composition root.
2. **Thin Controllers (No Business Logic in Routes):**
   - Route functions must remain lightweight. They extract request parameters, validate input shapes using Pydantic schemas, pass execution to the appropriate Application Service, and return response DTOs.
   - Business calculations, database transactions, or cascading ownership logic must **never** be written directly inside API endpoints.
3. **Centralized Exception Handling:**
   - Handlers in `app.py` catch domain exceptions and map them to standard HTTP status codes:
     - `EntityNotFoundError` ➔ `404 Not Found`
     - `ValidationError` ➔ `400 Bad Request` / `422 Unprocessable Entity`
     - `UnauthorizedError` / `AuthenticationError` / `AIAuthenticationError` ➔ `401 Unauthorized`
     - `ForbiddenError` / `AccessDeniedError` ➔ `403 Forbidden`
     - `ConflictError` / `UserAlreadyExistsError` ➔ `409 Conflict`
     - `AIRateLimitError` ➔ `429 Too Many Requests`
     - `AITimeoutError` ➔ `504 Gateway Timeout`
     - `AIProviderError` ➔ `502 Bad Gateway`
     - `AIConfigurationError` / `AIError` / `StorageError` ➔ `500 Internal Server Error`
4. **Security & Authentication Enforcement:**
   - Protected routes must depend on `Annotated[User, Depends(get_current_user)]`.
   - The `current_user.id` is explicitly passed to Application Services to guarantee data ownership isolation.
5. **Decoupled Delivery Channels:**
   - Changes to the REST API must not break the CLI, and vice versa. Each delivery channel consumes shared Application Services independently.

---

## 4. Implementation Approach & Design Patterns

- **FastAPI Dependency Injection (Inversion of Control):**
  - `dependencies.py` dynamically wires repositories and services for each incoming HTTP request, ensuring thread-safe database sessions and proper resource cleanup.
- **RESTful Resource Modeling:**
  - Resource URLs follow clear REST conventions with hierarchical sub-resources (e.g., `GET /journeys/{journey_id}/sections`, `POST /topics/{id}/complete`).
- **Standardized Response Envelopes:**
  - Output data is strictly serialized using Application Pydantic schemas (`response_model=...`), ensuring no sensitive domain or ORM fields (such as password hashes) leak to the client.

---

## 5. Tools & Technologies

- **Python 3.12+:** Core language runtime.
- **FastAPI:** High-performance, asynchronous-ready REST framework with automatic OpenAPI documentation.
- **Uvicorn:** Production ASGI server (`uvicorn masar.presentation.api.app:app`).
- **Pydantic v2:** Input validation and response serialization.
- **Swagger UI & ReDoc:** Automatically generated documentation available at `/docs` and `/redoc`.

---

## 6. Maintenance & Evolution Mandate

Whenever new endpoints, routers, or CLI commands are added:
- Ensure the route handler delegates business operations to an Application Service.
- Protect user-scoped endpoints with `Depends(get_current_user)`.
- Use Pydantic response models to serialize outputs.
- Verify both positive and error-handling scenarios with automated tests under `tests/presentation/`.
- **Update this `AGENTS.md` file** whenever routing policies, middleware, or delivery mechanisms change.
