# behaviour_lab Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-05

## Active Technologies
- SQLite (local single-file persistent state) (001-behavior-lab-simulation)
- Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest, PyYAML (001-behavior-lab-simulation)
- SQLite local file database with SQLModel tables for world, planning, and resource state (001-behavior-lab-simulation)
- Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pandas, pytest, lightweight charting support for gauges/graphs/maps (001-behavior-observatory)
- SQLite single-file persisted simulation state (001-behavior-observatory)
- Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest, httpx/openai-compatible client abstraction (001-behavior-observatory)

- Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest (001-behavior-lab-simulation)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 001-behavior-observatory: Added Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest, httpx/openai-compatible client abstraction
- 001-behavior-observatory: Added Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pandas, pytest
- 001-behavior-observatory: Added Python 3.11+ + FastAPI, Streamlit, SQLModel, Pydantic, pandas, pytest, lightweight charting support for gauges/graphs/maps


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
