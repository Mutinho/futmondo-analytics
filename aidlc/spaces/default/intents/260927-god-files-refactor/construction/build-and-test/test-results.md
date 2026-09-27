# Resultados de Build and Test — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, test strategy Minimal. Conversation language: Spanish.
> Ejecutado desde `backend/` con venv efímero (Python 3.14) y `JWT_SECRET` efímero. Coste 0 €.

## Estado de build

**Éxito.** `python -c "import app.main"` resuelve sin errores (el shim `analytics_service.py` re-exporta desde `app.services.analytics.facade`; path histórico intacto). No hay paso de compilación en Python.

## Resultados de tests

Comando (gate de CI): `cd backend && python -m pytest --cov=app -q`

| Métrica | Valor |
|---------|-------|
| Total | 221 |
| Passed | 218 |
| Failed | 0 |
| xfailed | 3 (preexistentes: `test_futmondo_client_characterization` LEGACY; documentan la migración FR4.2 de un intent previo) |
| Skipped | 0 |
| Duración | ~22 s |

Comando unit-scoped de la oleada: `cd backend && python -m pytest tests/test_analytics_service.py -v` → **16 passed** (6 preexistentes + 5 caracterización + 4 contrato del adaptador + 1 ctor/import-path).

### Detalles de fallos

Ninguno. Los 3 `xfailed` son esperados y preexistentes (no introducidos por esta oleada).

## Cobertura

- **Total: 29.75%** ≥ piso bloqueante **27%** (`--cov-fail-under=27` en `pytest.ini`). Línea de pytest: `Required test coverage of 27% reached. Total coverage: 29.75%`.
- Paquete nuevo `analytics/`: `facade.py` 100%, `domain/ports.py` 100%, `domain/__init__.py` 100%, `infrastructure/data_manager_adapter.py` 75%, `analytics_service.py` (shim) 100%.
- El piso NO se tocó (el ratchet solo sube).

## Lint (módulos nuevos)

`ruff check --config ruff.toml app/services/analytics/` → `All checks passed!`. No se reformateó ningún fichero brownfield (BR5.2).

## Matriz de Verificación de Objetivos

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| COV-FLOOR | `pytest.ini` `--cov-fail-under` | ≥ 27% line coverage | 29.75% | `Required test coverage of 27% reached. Total coverage: 29.75%` | build-and-test | Met |
| SUITE-GREEN | `team.md` gate de CI / NFR2 | suite existente verde | 218 passed, 0 failed, 3 xfailed | ejecución `pytest --cov=app` | build-and-test | Met |
| BR1.1 | `rules.md` | firma/payload público preservado | 11 tests de caracterización verdes | `tests/test_analytics_service.py` | build-and-test | Met |
| BR1.2 | `rules.md` | repositorio ≡ SQL inline previo | 2 tests de contrato del adaptador verdes | `test_adapter_fetch_all_teams_row_shape` / `..._players_by_ids...` | build-and-test | Met |
| NFR4/BR5.1 | `requirements.md` | sin dependencias nuevas | `requirements.txt` sin cambios | inspección git | build-and-test | Met |
| BR5.2 | `rules.md` | sin reformateo masivo brownfield | ruff solo sobre `analytics/` | `ruff check` output | build-and-test | Met |

No hay objetivos NFR de rendimiento/seguridad diferidos: la estrategia Minimal y el refactor no fijan umbrales que requieran un entorno desplegado. No queda ningún verdict `Pending` ni `Unverified`.

## Estado

**Build-ready y test-ready.** Gate de CI verde en local; se re-ejecutará en CI (gitleaks + `pytest` + `ng test`) antes de merge a `main`.
