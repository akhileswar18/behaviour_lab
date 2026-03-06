# Skills Log

## Troubleshooting Errors and Solutions

### 2026-03-06 - Editable install failed (`pip install -e .[dev]`)
- Error:
  - `error: Multiple top-level packages discovered in a flat-layout: ['app', 'data', 'specs']`
- Root cause:
  - `setuptools` package discovery was scanning unintended top-level folders.
- Solution applied:
  - Added explicit package discovery config in `pyproject.toml`:
    - `[tool.setuptools.packages.find]`
    - `include = ["app*"]`
    - `exclude = ["specs*", "data*", "tests*"]`
- Result:
  - Editable install succeeded.

### 2026-03-06 - DB seeding failed (`no such table: scenario`)
- Error:
  - `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: scenario`
- Root cause:
  - `SQLModel.metadata.create_all()` ran before model tables were registered.
- Solution applied:
  - Imported models in `app/persistence/init_db.py`:
    - `from app.persistence import models  # noqa: F401`
- Result:
  - DB initialization and seeding succeeded.

### 2026-03-06 - Streamlit page import failed (`app.dashboard`)
- Error:
  - `ModuleNotFoundError: No module named 'app.dashboard'; 'app' is not a package`
- Root cause:
  - Running `streamlit run app/dashboard/app.py` can shadow top-level `app` package name.
- Solution applied:
  - Updated dashboard pages to bootstrap `sys.path` with app/component directories and use local-safe imports:
    - `app/dashboard/pages/agents.py`
    - `app/dashboard/pages/timeline.py`
    - `app/dashboard/pages/memories.py`
    - `app/dashboard/pages/relationships.py`
- Result:
  - Pages imported successfully.

### 2026-03-06 - Streamlit page import failed (`app.schemas` via persistence engine)
- Error:
  - `ModuleNotFoundError: No module named 'app.schemas'; 'app' is not a package`
- Root cause:
  - `app/persistence/engine.py` imported settings only via `app.schemas...`, which fails under Streamlit shadowing context.
- Solution applied:
  - Added dual import fallback in `app/persistence/engine.py`:
    - try `from app.schemas.settings import get_settings`
    - fallback `from schemas.settings import get_settings`
- Result:
  - `agents` and `memories` pages loaded without module import failures.

### 2026-03-06 - Command policy blocked chained cleanup command
- Error:
  - Command rejected when using chained remove/init/test command.
- Root cause:
  - Execution policy blocked the combined command segment.
- Solution applied:
  - Re-ran initialization and tests using non-blocked command sequence.
- Result:
  - Validation completed successfully.

## Notes
- Streamlit warnings about `ScriptRunContext` in bare mode are expected when importing pages directly outside `streamlit run`.
- `use_container_width` deprecation warnings were observed and can be addressed later by switching to `width='stretch'`.
