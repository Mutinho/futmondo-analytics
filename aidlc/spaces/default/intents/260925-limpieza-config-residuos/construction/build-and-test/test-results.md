# Test Results — Build and Test (FR14 + FR15)

Intent: `260925-limpieza-config-residuos` · Scope: `refactor` (Minimal) · zero-Unit.
Ejecutado el 2026-09-25 sobre la rama `chore/limpieza-config-residuos`.

## Entorno de ejecución

- Backend: venv efímero (Python 3.14 del sistema; CI real usa 3.12) excluyendo
  `libsql-experimental` (no compila fuera de 3.12 y no lo ejercitan los tests,
  que usan el fake SQLite in-memory), `JWT_SECRET` efímero. Learning afirmado
  (2026-09-16).
- Frontend: NO ejecutado — este intent no toca código de `angular-app/`
  (`git status angular-app/` vacío); el spec existente que ejercita matchdays
  (`evolution.service.spec.ts`) usa el prefijo canónico `/api/v1/matchdays`, no
  el retirado. `ng test` se re-ejecutará en el gate de CI real.

## Build status

- Import/arranque del backend: OK (sin `ImportError` tras retirar el dead-path;
  `DBConnection.__init__` reescrito en lockstep con `config.py`).
- Sin refs vivas a símbolos retirados (`_init_turso`, `_TursoCursorWrapper`,
  `_init_sqlite`, `_convert_params`, `TURSO_DATABASE_URL`, `DATABASE_TYPE`) en
  `backend/app` (excluyendo un comentario en el god-file `data_manager_v2.py:519`,
  deuda registrada, código duck-typed correcto).

## Resultados de tests (backend `pytest`)

```
208 passed, 3 xfailed, 1 warning in 5.65s
```

- **Total**: 211 · **Passed**: 208 · **Failed**: 0 · **xfailed**: 3 · **Skipped**: 0
- Los 3 `xfailed` son legacy esperados del intent anterior FR4
  (`test_futmondo_client_characterization.py`: los `*_LEGACY` que documentan el
  swallow de `None` ya reemplazado por excepciones tipadas). No son regresiones.
- Sin regresiones respecto a la línea base brownfield.

## Cobertura

- `--cov` observability-only, sin piso (`cov-fail-under` diferido); no se
  introduce ni relaja ningún umbral (NFR2/NFR4). Ratcheting solo sube.

## Linting (advisory)

`ruff check` sobre los ficheros tocados reporta 15 avisos (F401×4, F841×3,
I001×8), **todos preexistentes** (verificados contra `HEAD`: los `F401` de
`main.py:9/223` y `db_connection.py:40` ya existían verbatim; los `F841`/`I001`
son heredados de zonas brownfield no modificadas). Conforme a la regla afirmada,
NO se corrigen con `--fix`/`format` para no inflar el diff ni exponer avisos
ajenos a la poda; `ruff check` sigue advisory.

## Loop-Back Log

(No aplica — la ejecución pasó sin fallos; no se disparó ningún loop-back.)

## Verdicto

Build-ready y test-ready. Suite verde, sin regresiones, sin dead-path vivo.
Deployment-ready sujeto al gate de CI real (Python 3.12 + gitleaks + `ng test`).
