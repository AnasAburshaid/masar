# AGENTS.md

## Project Identity

**Project Name:** Masar

**Project Description:** Developer Learning Tracker

Masar is a learning management application that evolves from a Python CLI application into a full-stack AI-powered platform.

The goal is to build a clean, maintainable, scalable, and professionally structured software project.

## 1. Architecture and Project Structure

Architecture is a major priority.

The project must follow a well-organized, layered architecture inspired by professional software engineering practices, including the separation of concerns used in traditional three-tier and clean architecture approaches.

### Architectural Principles

- Separate application responsibilities into clear layers.
- Keep business logic independent of user interface and persistence details.
- Avoid putting all functionality in one file or module.
- Group related functionality into meaningful packages.
- Use clear naming conventions for folders, files, classes, and functions.
- Avoid unnecessary dependencies between layers.
- Make the architecture easy to extend as the project evolves.
- Prefer maintainability and readability over shortcuts.

### Initial Architectural Direction

Use the following conceptual layers and directory organization, each governed by its own detailed `AGENTS.md` specification:

1. **Domain Layer (`masar/domain/`)** — See [masar/domain/AGENTS.md](masar/domain/AGENTS.md)
   - Core business entities, models, and domain rules.
   - Domain models are separated into individual files (`domain/models/journey.py`, `domain/models/section.py`, `domain/models/topic.py`, `domain/models/note.py`, `domain/models/progress.py`, `domain/models/user.py`, `domain/models/ai.py`, `domain/models/conversation.py`, `domain/models/action.py`, `domain/models/document.py`, `domain/models/profile.py`, `domain/models/recommendation.py`).
   - Domain exceptions are organized separately under `domain/exceptions/` (`base.py`, `journey.py`, `section.py`, `topic.py`, `note.py`, `user.py`, `ai.py`, `conversation.py`, `action.py`, `document.py`, `profile.py`, `recommendation.py`, `storage.py`).
   - **Rule:** Domain must not depend on Application, Infrastructure, Presentation, or Frontend.

2. **Application Layer (`masar/application/`)** — See [masar/application/AGENTS.md](masar/application/AGENTS.md)
   - Application services and use cases organized into individual files (`journey_service.py`, `section_service.py`, `topic_service.py`, `note_service.py`, `progress_service.py`, `user_service.py`, `ai_service.py`, `conversation_service.py`, `action_service.py`, `tool_registry.py`, `document_extractor.py`, `document_service.py`, `profile_service.py`, `recommendation_service.py`).
   - Repository abstractions defined in `application/interfaces/repositories/`, security in `application/interfaces/security/`, and AI provider in `application/interfaces/ai/`.
   - Pydantic v2 DTO validation schemas defined in `application/schemas/`.
   - **Rule:** Application depends on Domain and abstract interfaces. Application must NOT import or depend on concrete Infrastructure or Presentation implementations.

3. **Infrastructure Layer (`masar/infrastructure/`)** — See [masar/infrastructure/AGENTS.md](masar/infrastructure/AGENTS.md)
   - Implements repository, security, and AI abstractions defined in the Application layer.
   - Implementations are organized by technology:
     - Relational Database & SQLAlchemy 2.0 ORM (`infrastructure/database/`, `infrastructure/repositories/database/`).
     - Cryptography & Auth (`infrastructure/security/password.py` for PBKDF2, `infrastructure/security/jwt_token.py` for PyJWT).
     - AI Providers (`infrastructure/ai/openrouter_provider.py` for OpenRouter HTTP, `infrastructure/ai/mock_provider.py` for zero-network testing).
     - File storage adapters (`infrastructure/storage/json_storage.py`, `infrastructure/repositories/json/`).
     - In-memory testing adapters (`infrastructure/repositories/in_memory/`).
   - **Rule:** Infrastructure may depend on Application interfaces and Domain models, but never on Presentation or Frontend.

4. **Presentation Layer (`masar/presentation/`)** — See [masar/presentation/AGENTS.md](masar/presentation/AGENTS.md)
   - Handles REST API delivery (`presentation/api/`) via FastAPI and CLI terminal interaction (`presentation/cli.py`).
   - Centralized exception handlers map Domain exceptions to standardized HTTP status codes and detail payloads.
   - Route handlers are thin controllers delegating to Application services with `Depends(get_current_user)`.
   - **Rule:** Presentation depends on Application services/schemas and Domain models/exceptions.

5. **Frontend Layer (`frontend/`)** — See [frontend/AGENTS.md](frontend/AGENTS.md)
   - Next.js 16 (App Router with Turbopack), React 19, and Tailwind CSS v4 web application.
   - Dual-theme system (Light & Dark mode) with `ThemeContext` and `localStorage` persistence.
   - Typed API client services consuming the FastAPI backend with Bearer token authentication.
   - Interactive AI action proposals (`ActionProposalCard`) allowing users to review, approve, or reject AI-recommended changes before execution.
   - **Rule:** Backend REST API is the single source of truth. UI never bypasses backend business rules or validation.

6. **Composition Root & Dependency Injection (`masar/container.py`, `masar/presentation/api/dependencies.py`)**
   - Instantiates concrete Infrastructure repositories and wires them into Application services.
   - Injects wired services into API route handlers and CLI controllers.
   - Keeps layer boundaries decoupled without hardcoded infrastructure dependencies inside Application or Presentation.

These layers must maintain strict inward dependency direction.

The architecture evolves gracefully as the application grows without unnecessary rewrites.

Do not force abstractions that are not currently justified.

### Multi-Layer AGENTS.md Maintenance Rule

Each layer has its own dedicated `AGENTS.md` specification detailing its directory organization, implementation rules, architectural approach, and tooling:
- [masar/domain/AGENTS.md](masar/domain/AGENTS.md)
- [masar/application/AGENTS.md](masar/application/AGENTS.md)
- [masar/infrastructure/AGENTS.md](masar/infrastructure/AGENTS.md)
- [masar/presentation/AGENTS.md](masar/presentation/AGENTS.md)
- [frontend/AGENTS.md](frontend/AGENTS.md)

**Mandate:** In all future implementations, whenever a layer's structure, rules, patterns, dependencies, or tools change, or whenever the developer provides feedback affecting a layer, the corresponding layer's `AGENTS.md` file (and this root `AGENTS.md` if cross-cutting) MUST be updated to document the new reality.

## 2. Development Execution

The developer will provide implementation tasks based on the milestones in PLAN.md.

Your responsibility is to execute the assigned tasks efficiently and professionally.

- Implement the assigned task completely.
- Work step by step within the defined milestone.
- Do not stop unnecessarily to request approval for ordinary implementation decisions.
- Make reasonable technical decisions and explain significant ones.
- Do not implement unrelated features or future milestones.
- Do not skip requirements defined in the task.

If requirements are genuinely ambiguous or a decision could significantly affect the architecture, explain the issue before proceeding.

## 3. Code Quality

- Follow Python conventions (PEP 8).
- Use meaningful names.
- Write readable, maintainable code.
- Use type hints appropriately.
- Avoid duplicated logic.
- Keep functions and classes focused.
- Handle exceptions properly.
- Avoid unnecessary complexity and dependencies.
- Follow established patterns consistently throughout the project.

## 4. Testing and Verification

Testing is an essential part of every implementation task.

After implementing a feature:

1. Run relevant automated tests.
2. Perform additional checks where appropriate.
3. Verify that existing functionality still works.
4. Identify and fix implementation errors.
5. Report test results accurately.

Never claim that tests passed without actually running them.

If a test fails, investigate the root cause instead of hiding or bypassing the failure.

Add automated tests as the project architecture and milestones require.

## 5. Project Planning

PLAN.md is the source of truth for development progress.

- Follow milestones sequentially.
- Work only on the tasks assigned by the developer.
- Update PLAN.md when tasks or milestones are completed and verified.
- Never mark unfinished work as completed.
- Do not skip milestones without explicit instructions.

## 6. Technology Management

Follow the technology roadmap defined in README.md and PLAN.md.

- Use Python standard libraries during the initial stage where appropriate.
- Introduce FastAPI, Pydantic, SQLAlchemy, PostgreSQL, and other technologies at their designated stages.
- Avoid introducing unnecessary frameworks or dependencies.
- Keep the application compatible with its planned evolution.

## 7. Git and Project Safety

- Preserve existing implementation and project history.
- Do not automatically commit or push changes.
- Avoid destructive commands and operations.
- Do not overwrite existing work without justification.
- Keep changes focused on the assigned task.

## 8. Communication and Reporting

After each assigned task, provide:

1. Summary of what was implemented.
2. Files and folders created or modified.
3. Important architectural or technical decisions.
4. Tests executed and their actual results.
5. Any remaining issues or limitations.
6. Suggested next task from PLAN.md.

Keep explanations direct, practical, and technically accurate.

## Pull Request and Merge Workflow

After completing an issue:

1. Create a dedicated feature branch.
2. Implement the issue and run relevant tests.
3. Commit and push the feature branch to GitHub.
4. Create a Pull Request targeting `main`.
5. Link the related issue and provide a clear summary of the implementation and test results.
6. Stop and wait for the developer to review the Pull Request.

### Merge Authorization

- Never merge a Pull Request without explicit approval from the developer.
- Once the developer approves and requests the merge, merge the Pull Request using GitHub.
- Prefer Squash and Merge for individual feature issues.
- After merging, synchronize the local `main` branch with the remote `main`.
- Delete the feature branch after successful merging, if appropriate.
- Verify that the local repository is clean and up to date before starting another issue.

Never push feature implementation directly to `main`.

## Core Principle

Build Masar as a professionally structured software product.

Prioritize architecture, separation of concerns, maintainability, reliability, and clean implementation.

The developer will review the implementation, execute tests, and evaluate the results after each assigned task.