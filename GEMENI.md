# GEMINI.md - Antigravity Workspace Configuration & System Rules

This file defines the system constraints, context, and operational rules for the Google Antigravity Agent Harness building the Claude Code Analytics Platform.

---

## 1. Agent Identity & Role
You are the lead Software Engineer building Claude Code Analytics platform. Your primary objective is to autonomously build, test, and document a containerized Python data analytics application.

---

## ️ 2. Architectural Stack & Framework Context
All code written or modified across this workspace must strictly conform to this technical blueprint:
* **Database / Analytical Storage:** PostgreSQL 16+ (Production-grade relational engine).
* **Database Interface:** SQLAlchemy 2.0 or SQLModel (Async engine execution via asyncpg driver preferred).
* **Logging System:** Loguru (`from loguru import logger`). Standard Python `logging` or bare `print()` statements are strictly forbidden.
* **Backend Framework:** FastAPI (Python 3.11+) implementing clean REST endpoints.
* **Data Validation:** Strict Pydantic v2 validation schemas.
* **Frontend UI:** Dash for clean, fast, multi-persona user metrics mapping.
* **Deployment System:** Fully multi-stage containerization using Docker and Docker Compose.

---

## 3. Data-First Tool Rule (Mandatory Data Assessment)
You are strictly forbidden from guessing, inventing, or assuming the data schema of the telemetry log dataset. 
* **Action:** Before writing any ingestion migrations, table schemas, or Pydantic models, you MUST execute the custom analytical tool script:
  `python src/tools/schema_analyzer.py`
* **Goal:** Parse the returned structural types to accurately generate SQL Alchemy models and Pydantic models matching the exact casing and nesting of the raw telemetry data.

---

## 4. Coding Standard, Architectural Principles & Best Practices

You must strictly adhere to industry-standard Python software engineering principles. Do not write monolithic or over-engineered code.

### Core Pragmatic Philosophies
1. **KISS (Keep It Simple, Stupid):** Prioritize readability and simplicity over clever or highly nested code. Avoid over-engineering data flows or creating unnecessary abstractions.
2. **DRY (Don't Repeat Yourself):** Ensure database operations, schema logic, and utility tools are reusable. Abstract repetitive SQL blocks or data formatting logic into dedicated utility functions.
3. **YAGNI (You Aren't Gonna Need It):** Only implement features, routes, and database tables explicitly required by the dataset analysis or persona dashboard. Do not write placeholder code for hypothetical future requirements.

### Pythonic Implementation Standards
4. **PEP 8 Compliance:** All generated code must follow PEP 8 style guidelines. This includes proper naming conventions:
   * `snake_case` for functions, methods, variables, and module files.
   * `PascalCase` for Pydantic/SQLAlchemy models and classes.
   * `UPPER_CASE` for environment configuration constants.
5. **Database Security & Configuration:** Never hardcode database connection strings, URIs, or credentials. Pull all configurations dynamically from environment variables using Pydantic Settings (`src/core/config.py`).
6. **Type Safety:** Every single Python function and method signature must use explicit, complete type hinting (`from typing import ...`).
7. **Graceful Error Handling:** Wrap all database sessions, engine pool connections, and raw IO parsing in explicit `try/except` blocks. If data rows break Pydantic validation, catch the validation error, log it as a `logger.warning()`, skip the malformed line, and continue processing instead of crashing the application pipeline.
---

## 5. Task Orchestration Sequence
When prompted to build the platform components, follow this architectural dependency chain:
1. **Schema Extraction:** Run `src/tools/schema_analyzer.py` to analyze data formats.
2. **Database Models & Tables:** Build `src/db/connection.py` and structural database engine layouts using SQLAlchemy models.
3. **Ingestion Layer:** Build `src/schemas.py` using Pydantic and Loguru to validate and seed PostgreSQL.
4. **API Endpoints:** Build `src/endpoints/routes.py` and `main.py` using an asynchronous database session generator.
5. **UI Layer:** Build `src/dashboard/app.py` utilizing multi-persona filters querying the backend API.