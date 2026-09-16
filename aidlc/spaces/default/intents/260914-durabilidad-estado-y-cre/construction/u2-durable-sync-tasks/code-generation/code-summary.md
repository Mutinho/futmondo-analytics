# Code Summary — u2-durable-sync-tasks

> Etapa Code Generation (Construction), unidad `u2-durable-sync-tasks`. Resumen de la implementación
> de la durabilidad del estado de las tareas de sync sobre el backend existente `futmondo-api`
> (FastAPI, Python 3.12, Neon vía `db_connection`). Metodología test-after con caracterización primero.
> Coste 0€. Las etapas de diseño per-unit quedaron saltadas por el reinicio; el diseño se incorporó al
> plan de code-generation aprobado.

## Archivos creados

| Ruta | Contenido |
|------|-----------|
| `backend/app/stores/task_repository.py` | `TaskRepository`, `TaskRecord`, `DurableTaskStatus`, `ensure_durable_task_schema(db)`; insert, update_status/progress/result/error, `get(task_id)`, `get_active(championship_id)` (FR1.6), `mark_interrupted_on_startup()` (FR1.5); SQL parametrizado (ramas PG/SQLite `ON CONFLICT`), JSON como TEXT portable, DB inyectable; sigue el patrón de `session_repository.py` (u1) |
| `backend/app/services/task_service.py` | `TaskService` (create persiste + puebla caché; update BD autoridad + caché best-effort; get caché → BD, FR1.4; `get_active_or_conflict`, FR1.6; `mark_interrupted_on_startup`, FR1.5; no reanuda); errores tipados `TaskConflictError`/`TaskPersistenceError`, sin `except: pass`; provider `get_task_service()` |
| `backend/tests/test_durable_task_characterization.py` | 7 tests: congelan el comportamiento in-memory ACTUAL de `TaskManager` (pasan contra el código previo) |
| `backend/tests/test_durable_task_repository.py` | 11 tests: persistencia/lectura, `get_active` contra BD, marcado interrumpida-por-reinicio, idempotencia del esquema |
| `backend/tests/test_durable_task_service.py` | 11 tests: consultable tras reinicio (FR1.4), 409 contra BD (FR1.6), relanzable si interrumpida, marcado al arranque (FR1.5), BD autoridad |
| `backend/tests/test_durable_task_api.py` | 6 tests: `/task/{id}` tras reinicio (FR1.4), `/trigger` 409 contra estado persistido y relanzar si interrumpida (FR1.6) |

## Archivos modificados (en su sitio, aditivo)

| Ruta | Cambio |
|------|--------|
| `backend/app/services/task_manager.py` | Añadido estado `INTERRUPTED_BY_RESTART` y métodos best-effort `put()`/`clear()`; API pública preservada (degradado a caché) |
| `backend/app/api/v1/endpoints/sync.py` | `/trigger`: unicidad 409 contra BD vía `TaskService` (FR1.6) + creación durable; `/task/{id}`: lee caché → BD (FR1.4); el worker persiste transiciones vía `TaskService`; sin endpoints nuevos; `detail` en castellano |
| `backend/app/main.py` | Arranque llama `ensure_durable_task_schema()` + `TaskService.mark_interrupted_on_startup()` (FR1.5), junto al de u1 |
| `backend/app/stores/__init__.py` | Exporta los símbolos de `TaskRepository` |

## Decisiones clave de implementación

- **JSON como TEXT portable** (`progress`/`result` con `json.dumps`/`loads`), no JSONB, para reutilizar
  el fake SQLite sin coste (0€, sin dependencias nuevas) y mantener portabilidad PG/SQLite.
- **Sweep de arranque invalida la caché** (`clear()`) para que una lectura no enmascare el estado
  autoritativo `interrupted_by_restart` (bug real detectado por un test y corregido).
- **BD autoridad, caché best-effort (NFR5):** `TaskManager` degradado; la unicidad y el polling se
  resuelven contra BD.
- **No se reanudan tareas automáticamente** (out of scope): solo se persiste y se marca el estado.
- Idiomas: identificadores/docstrings/comentarios en inglés; `detail` de `HTTPException` en castellano.
- `ruff format` aplicado SOLO a los 6 archivos nuevos (binding de revisión estable); brownfield tracked
  NO reformateado (sin scope creep).

## Resumen de cobertura de tests

- **Comando por-unidad** (desde `backend/`):
  `pytest tests/test_durable_task_characterization.py tests/test_durable_task_repository.py tests/test_durable_task_service.py tests/test_durable_task_api.py -q`
- **Resultado**: **35 passed** (caracterización 7, repository 11, service 11, api 6).
- **Suite completa del backend**: **125 passed, 1 warning** (baseline 90 → +35, **0 regresiones**, NFR4).
- **Cobertura (informativa)**: `task_service.py` 91%, `task_repository.py` 91%.
- **Lint**: `ruff check` + `ruff format --check` limpios en los 6 archivos nuevos.

## Desviaciones respecto al plan

- **Etapas de diseño per-unit saltadas:** functional-design / nfr-requirements / nfr-design /
  infrastructure-design de u2 quedaron `[S] skipped` al reiniciar la etapa Code Generation (jump
  forward). El diseño de la durabilidad de tareas se incorporó al plan de code-generation aprobado por
  el humano, fundamentado en requirements (FR1.4/1.5/1.6), unit-of-work (U2), contract-summary (sin
  contrato inter-unidad) y el código brownfield. Aprobado explícitamente en el gate de Plan Approval.
- **Nota de entorno (no bloqueante):** runtime local Python 3.14; `libsql-experimental` (pin) no
  compila en 3.14 pero solo se usa en el backend Turso, no ejercitado por estos tests (fake SQLite).
  CI usa 3.12.
- **Nota heredada (no bloquea u2):** el job `verify` de `fly-deploy.yml` (push→`main`) corre pytest sin
  gitleaks; formalizar en diseño de pipeline.
