# masar (Developer Learning Tracker)

## Overview

masar is a personal learning management application designed to help developers organize technical learning journeys, track progress, save notes, and manage practical projects.

The application will initially be a Python command-line application and will gradually evolve into a full-stack web application with AI-powered capabilities.

## Main Goals

- Organize multiple learning journeys.
- Divide journeys into sections and topics.
- Track learning progress.
- Save notes and learning resources.
- Associate practical projects with learning topics.
- Eventually provide AI-powered learning assistance.

## Initial Features

1. Create, view, update, and delete learning journeys.
2. Create and manage sections within journeys.
3. Add, edit, delete, and complete topics.
4. Attach notes to topics.
5. Calculate progress for individual sections and entire journeys.
6. Persist application data using JSON files.

## Technology Roadmap

### Initial Stage
- Python
- JSON
- Standard Python libraries

### Backend Stage
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

### Advanced Stage
- Authentication
- Automated testing
- Web frontend
- LLM integration
- AI agents

## Development Philosophy

The application must evolve gradually as new programming concepts are learned.

Avoid introducing technologies before they are needed.

Prioritize simplicity, readability, maintainability, and understanding over unnecessary complexity.

## Project Structure

Masar follows a layered Clean Architecture structure:

```
masar/
├── __init__.py
├── __main__.py                         # CLI entry point
├── container.py                        # Composition root & DI wiring
├── domain/                             # Core business entities & rules
│   ├── __init__.py
│   ├── models/                         # Domain models in individual files
│   │   ├── __init__.py
│   │   ├── journey.py
│   │   ├── note.py
│   │   ├── progress.py
│   │   ├── section.py
│   │   └── topic.py
│   └── exceptions/                     # Domain exceptions
│       ├── __init__.py
│       ├── base.py
│       ├── journey.py
│       ├── note.py
│       ├── section.py
│       ├── storage.py
│       └── topic.py
├── application/                        # Use cases & workflow coordination
│   ├── __init__.py
│   ├── interfaces/                     # Abstractions (e.g., repository interfaces)
│   │   ├── __init__.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── journey_repository.py
│   │       ├── note_repository.py
│   │       ├── section_repository.py
│   │       └── topic_repository.py
│   └── services/                       # Application services
│       ├── __init__.py
│       ├── journey_service.py
│       ├── note_service.py
│       ├── progress_service.py
│       ├── section_service.py
│       └── topic_service.py
├── infrastructure/                     # Persistence & external adapters
│   ├── __init__.py
│   ├── exceptions.py
│   ├── storage/                        # Persistence storage engines
│   │   ├── __init__.py
│   │   └── json_storage.py
│   └── repositories/
│       ├── __init__.py
│       ├── in_memory/                  # Concrete in-memory implementations
│       │   ├── __init__.py
│       │   ├── journey_repository.py
│       │   ├── note_repository.py
│       │   ├── section_repository.py
│       │   └── topic_repository.py
│       └── json/                       # Concrete JSON file implementations
│           ├── __init__.py
│           ├── journey_repository.py
│           ├── note_repository.py
│           ├── section_repository.py
│           └── topic_repository.py
└── presentation/                       # Presentation & CLI interaction
    ├── __init__.py
    └── cli.py
tests/                                  # Automated tests suite
pyproject.toml                          # Packaging and build configuration
```

## Getting Started

### Prerequisites

- Python 3.10 or higher

### 1. Setup Virtual Environment

Create and activate a virtual environment:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the Project

Install Masar in editable development mode:

```bash
pip install -e .
```

### 3. Run the Application

You can run the application directly as a module:

```bash
python -m masar
```

Or using the CLI entry point installed by the package:

```bash
masar
```

### 4. Run Automated Tests

Run the test suite using Python's built-in `unittest`:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### 5. Run the FastAPI REST API Server

```bash
uvicorn masar.presentation.api.app:app --reload --port 8000
```

The interactive API documentation is accessible at `http://localhost:8000/docs`.

### 6. AI Integration Foundation

Masar provides an extensible AI abstraction layer supporting LLM integrations. The foundation integrates with OpenRouter (OpenAI-compatible) and includes an offline mock provider for automated testing.

#### Configuration (`.env`)

Configure the following variables in your `.env` file:

```env
# AI Provider Configuration
MASAR_AI_PROVIDER=openrouter               # Options: "openrouter", "mock"
OPENROUTER_API_KEY=your-openrouter-api-key # Or OPENROUTER_API-KEY
MASAR_AI_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
MASAR_AI_BASE_URL=https://openrouter.ai/api/v1
MASAR_AI_TIMEOUT_SECONDS=30.0
MASAR_AI_TEMPERATURE=0.7
```

#### Architecture Components:
- **Domain Layer (`masar.domain.models.ai`, `masar.domain.exceptions.ai`)**: Core dataclasses (`ChatMessage`, `AIUsage`, `AIResponse`) and structured domain exceptions (`AIAuthenticationError`, `AIRateLimitError`, `AITimeoutError`, `AIProviderError`, `AIConfigurationError`).
- **Application Layer (`masar.application.interfaces.ai`, `masar.application.services.ai_service`)**: `AIProvider` interface contract and `AIService` orchestrator validating prompts and message roles.
- **Infrastructure Layer (`masar.infrastructure.ai`)**:
  - `OpenRouterProvider`: Production-grade HTTP client with error mapping and retry/timeout handling.
  - `MockAIProvider`: Zero-network test provider supporting queued mock responses, call recording, and error injection.


---

## Frontend Setup (Next.js & TypeScript)

The frontend application is built with Next.js (App Router), TypeScript, and Tailwind CSS.

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.local.example` to `.env.local`:

```bash
cp .env.local.example .env.local
```

Default settings point to `NEXT_PUBLIC_API_URL=http://localhost:8000`.

### 3. Run Development Server

```bash
npm run dev
```

The frontend will start at `http://localhost:3000`.

### 4. Run Frontend Tests & Lint

```bash
npm test        # Run unit tests
npm run lint    # Run ESLint
npm run build   # Production build check
```
