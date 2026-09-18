# Build Instructions — matchday-prizes-calc

## Backend (Python 3.12)

- Ejecutar desde `backend/`. `pytest.ini`: `testpaths = tests`, `pythonpath = .`.
- Comando de test del área (unit-scoped):
  ```bash
  cd backend && python -m pytest tests/test_prizes_characterization.py tests/test_prizes_calculator.py -q
  ```
- Suite completa: `cd backend && python -m pytest -q` (con `--cov=app` en el gate de PR).
- Local a coste 0 € (Python del sistema más nuevo que CI): venv efímero excluyendo `libsql-experimental` (no compila fuera de 3.12 y no lo ejercitan los tests, que usan el fake SQLite) y `JWT_SECRET` de arranque efímero.

## Build/CI

- El gate de CI (`.github/workflows/ci.yml`, PR→`main`) corre gitleaks + `pytest --cov=app` + `ng test` como **bloqueantes**. No hay cambios de configuración de build en este intent.
- No hay artefactos de despliegue nuevos (el cálculo vive dentro del backend `futmondo-api` existente; se ejercita en el cron de sync).
