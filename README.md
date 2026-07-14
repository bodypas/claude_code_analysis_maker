# Claude Code Analytics Platform

An analytics platform that ingests Claude Code telemetry and employee data, stores it in PostgreSQL, and surfaces usage insights through interactive dashboards — including an AI-generated narrative summary of the data.

## Quick Start

```bash
cp .env.example .env
docker compose up
```

That's it. On first startup, the app automatically:
*   Creates the database schema.
*   Seeds employee and telemetry data.
*   Parses raw telemetry into typed, queryable tables.

Once running:
*   **Dashboard:** http://localhost:8501
*   **API docs:** http://localhost:8000/docs

> **Note:** To use the AI Report feature, add your Gemini API key to `.env` before starting (see `.env.example`).

---

## Architecture

```
employees.csv, telemetry_logs.jsonl
        ↓
  Seed script (runs on container start)
        ↓
PostgreSQL
  ├── employees              (direct load from CSV)
  ├── telemetry_logs         (raw JSONB, one row per event — safety net for reprocessing)
  └── typed event tables     (parsed from telemetry_logs, one per event type):
        ├── user_prompt_events
        ├── tool_decision_events
        ├── tool_result_events
        ├── api_request_events
        └── api_error_events
        ↓
FastAPI (async SQLAlchemy) — aggregation endpoints, one per dashboard chart
        ↓
Dash (frontend) — calls FastAPI via httpx, renders dashboards
                   (Employees, Telemetry, AI Report). Dash is presentation-only:
                   no direct DB access, all data comes through the API.
        ↓
Gemini API — generates a narrative summary from the same aggregated
              JSON the dashboards use (not raw logs)
```

---

## Why this shape?

*   **Raw + Typed Tables:** Claude Code's telemetry is OpenTelemetry-style. We avoid JSONB-only (slow/error-prone) and wide-flattened tables (sparse/NULL-heavy) by parsing into domain-specific tables while keeping the raw JSONB for auditability.
*   **Decoupled Datasets:** `employee_email` is an indexed string, not a foreign key, allowing flexibility between independent datasets.
*   **Optimized Ingestion:** Uses batched `INSERT ... RETURNING` for near-instant seeding.
*   **Aggregated AI:** The AI summary operates on aggregated metrics, not raw logs, ensuring low cost/latency and higher accuracy.

---

## Data Model

| Table | Source | Purpose |
| :--- | :--- | :--- |
| `employees` | `employees.csv` | Directory: email, name, practice, etc. |
| `telemetry_logs` | `telemetry_logs.jsonl` | Raw event log (JSONB payload) |
| `user_prompt_events` | Parsed | Prompt activity (length, session) |
| `tool_decision_events` | Parsed | Decisions (accept/reject) |
| `tool_result_events` | Parsed | Outcomes (success, duration) |
| `api_request_events` | Parsed | Model calls (tokens, cost) |
| `api_error_events` | Parsed | Errors (code, attempt) |

---

## Dashboards
*   **Employees:** Headcount distribution and filters.
*   **Telemetry:** Usage KPIs, cost/token trends, and error analysis.
*   **AI Report:** On-demand narrative summary.

---

## AI-Assisted Development
This project was built using Gemini CLI with a committed configuration in `AGENTS.md` and `GEMINI.md`.

### Key Components
*   **`AGENTS.md` / `GEMINI.md`**: Enforce architectural constraints and mandatory task sequences (e.g., schema inspection first).
*   **`src/tools/schema_analyzer.py`**: Custom tool that scans `telemetry_logs.jsonl` to infer structures, types, and field prevalence. This prevents guessing schemas.

### Reproducing the Setup
1.  Install Gemini CLI.
2.  The root configuration is automatically detected.
3.  Run `python src/tools/schema_analyzer.py` if the source data changes.

---

## Lessons Learned: Retrospective AGENTS.md Rules

If I were to build this application again, I would have included the following architectural constraints in `AGENTS.md` from the very beginning. These were identified as critical during development but were missing from the initial agent configuration:

*   **Enforce Stricter Layered Architecture:** Explicitly require Routers to delegate solely to Services, and Services to communicate *only* with Repositories.
*   **Database-Level Aggregation Only:** Mandate that all sum, count, and grouping operations are performed via SQLAlchemy expressions at the database level. Explicitly prohibit the use of Pandas or in-memory Python processing for analytics.
*   **Endpoint-to-Requirement Mapping:** Require that every API endpoint be defined to serve pre-aggregated data specifically tailored for a single dashboard component, preventing unnecessary data transfer or client-side processing.
*   **Mandatory Test Coverage:** Require automated tests for the ETL dispatch logic (event-type routing, type casting, malformed-row handling) to be implemented alongside the ETL logic itself.
*   **Data Integrity Rules:** Require an explicit assessment of whether referential integrity (foreign keys) is needed between datasets (e.g., telemetry and employees) at the design phase.

---

## Tech Stack
*   **Backend:** FastAPI (strict Pydantic v2 response validation), SQLAlchemy 2.0 (async), PostgreSQL 16
*   **Frontend:** Dash, httpx
*   **Infrastructure:** Docker Compose
*   **AI/LLM:** Gemini API
