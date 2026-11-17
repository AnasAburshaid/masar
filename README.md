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
├── __main__.py               # Entry point for 'python -m masar'
├── presentation/             # Presentation layer (CLI, UI interaction)
│   ├── __init__.py
│   └── cli.py
├── application/              # Application layer (use cases, workflow coordination)
│   └── __init__.py
├── domain/                   # Domain layer (business entities, rules)
│   └── __init__.py
└── infrastructure/           # Infrastructure layer (persistence, external APIs)
    └── __init__.py
tests/                        # Automated tests suite
├── __init__.py
└── test_cli.py
pyproject.toml                # Project packaging and build configuration
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
