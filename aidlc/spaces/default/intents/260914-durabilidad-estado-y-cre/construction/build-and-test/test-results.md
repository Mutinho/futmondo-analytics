# Test Results — Durabilidad del estado

> Etapa Build and Test (Construction), Step 9. Resultado real de ejecutar el build y los tests del
> backend `futmondo-api` tras la durabilidad de sesión (u1) y de tareas de sync (u2). Ejecutado en un
> venv efímero (coste 0) con Python 3.14, excluyendo `libsql-experimental` (no compila en 3.14, no
> ejercitado — los tests usan el fake SQLite). CI usa Python 3.12 con el `requirements.txt` completo.

## Estado del build

- **Build (instalación + importabilidad)**: SUCCESS. Dependencias instaladas sin error (excluyendo
  `libsql-experimental` en 3.14); `import app.main` OK con `JWT_SECRET` de arranque efímero.

## Resultados de tests

| Alcance | Comando | Resultado |
|---------|---------|-----------|
| Suite completa (NFR4) | `pytest -q` (desde `backend/`, con `JWT_SECRET` efímero) | **125 passed, 1 warning** |
| u1-durable-session (scoped) | `pytest tests/test_durable_session_*.py -q` | **36 passed** |
| u2-durable-sync-tasks (scoped) | `pytest tests/test_durable_task_*.py -q` | **35 passed** |

- **Total**: 125 passed, 0 failed, 0 skipped, 1 warning.
- **Regresiones**: 0. Baseline previo 54 tests no-durabilidad + 71 nuevos (36 u1 + 35 u2) = 125.
- **Warning**: `StarletteDeprecationWarning` (httpx en `starlette.testclient.TestClient`); no
  relacionado con la durabilidad, no rompe la suite.

## Detalles de fallos

Ninguno.

## Cobertura (informativa, sin piso bloqueante — decisión Q3)

Módulos de durabilidad (comando `--cov` sobre los tests de service+repository de ambas unidades):

| Módulo | Cobertura |
|--------|-----------|
| `app/security/credential_protection.py` | 97% |
| `app/services/session_service.py` | 80% |
| `app/services/task_service.py` | 89% |
| `app/stores/session_repository.py` | 83% |
| `app/stores/task_repository.py` | 90% |
| **TOTAL (piezas de durabilidad)** | **88%** |

No existe `cov-fail-under` en el repo (ratcheting diferido); la cobertura es referencia consciente.

## Checks diferidos (no ejecutables localmente en esta etapa)

- **gitleaks** (escaneo de secretos): gate bloqueante en CI (`ci.yml`, gate de MR). No instalado en
  el entorno de desarrollo local; **diferido a CI**. Owning stage: CI Pipeline / gate de MR.
- **ruff check / ESLint / ng test**: advisory/gate en CI; no ejecutados localmente en esta etapa.
  `ng test` (frontend) sin cambios funcionales de frontend en este intent.

## Loop-Back Log

<!-- Vacío: no se disparó ningún loop-back (rung 3/4). Build y tests en verde a la primera. -->
