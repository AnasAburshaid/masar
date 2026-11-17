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

Use the following conceptual layers:

1. **Presentation Layer**
   - Handles CLI interaction.
   - Displays information to users.
   - Collects user input.

2. **Application Layer**
   - Contains application use cases.
   - Coordinates operations between the presentation, domain, and infrastructure layers.
   - Handles application workflows.

3. **Domain Layer**
   - Contains core business entities and business rules.
   - Remains independent of external technologies.

4. **Infrastructure Layer**
   - Handles data persistence.
   - Implements repositories and external integrations.
   - Initially uses JSON file storage.

These layers must have clear responsibilities and appropriate dependency direction.

The architecture should evolve when the application moves to FastAPI, PostgreSQL, and AI integration without unnecessary rewrites.

Do not force abstractions that are not currently justified.

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