# Code Summary — Oleada 1: extracción DDD de `analytics_service.py`

Intent `260927-god-files-refactor`, scope `refactor`, depth Minimal, unidad única
(zero-Unit). Metodología `test-after` con `characterization-first` (BR1.3).

## Ficheros creados

- `backend/app/services/analytics/__init__.py` — re-exporta `AnalyticsService` (fachada); documenta el layering.
- `backend/app/services/analytics/domain/__init__.py` — package init de dominio; re-exporta `AnalyticsDataPort`.
- `backend/app/services/analytics/domain/ports.py` — `AnalyticsDataPort` (`typing.Protocol`): SOLO los datos que analytics consume + `fetch_all_teams()` / `fetch_players_by_ids()`. Sin infra, sin framework, sin SQL (BR2.1).
- `backend/app/services/analytics/application/__init__.py` — package init; re-exporta `AnalyticsCalculations`.
- `backend/app/services/analytics/application/calculations.py` — los 11 cálculos `get_*` + helpers de resolución (`_safe_team_info`, `_resolve_real_team_name`, `_safe_player_info`, `_build_team_lookup`, `_resolve_team`) movidos verbatim, operando sobre el puerto (BR2.3).
- `backend/app/services/analytics/infrastructure/__init__.py` — package init; re-exporta `DataManagerAnalyticsAdapter`.
- `backend/app/services/analytics/infrastructure/data_manager_adapter.py` — `DataManagerAnalyticsAdapter`: implementa el puerto sobre `DataManagerV2`; ÚNICO sitio con SQL crudo — los 2 `SELECT` movidos verbatim (BR2.2, BR1.2).
- `backend/app/services/analytics/facade.py` — `AnalyticsService`: fachada delgada, 11 métodos públicos, solo delega (BR2.5); ctor `__init__(self, data: AnalyticsDataPort | None = None)` con default `DataManagerAnalyticsAdapter()` (BR2.6).

## Ficheros modificados

- `backend/app/services/analytics_service.py` — reducido a **shim de re-export** (`from app.services.analytics.facade import AnalyticsService`). Preserva el import path histórico usado por el endpoint (FR2.1).
- `backend/tests/test_analytics_service.py` — extendido: +5 tests de caracterización (los `get_*` sin cobertura), +4 tests de contrato del adaptador, +1 test de ctor sin-args/import-path; fixture migrado de monkeypatch de `__init__` a inyección por el nuevo constructor (`AnalyticsService(data=StubPort())`).
- `aidlc/.../construction/code-generation/code-generation-plan.md` — checkboxes [ ]→[x] (única edición permitida).

## Ficheros NO tocados (preservados)

- `backend/app/api/v1/endpoints/analytics.py` y su `get_service()` — consumidor intacto (FR2.1). El `SELECT` inline del endpoint `championship/classification-full` (SQL-en-router **preexistente**) queda como deuda registrada, fuera de alcance.
- Otros god-files (`data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`) — no ampliados ni reescritos.

## Decisiones clave

- **`db.adapt_params()` en los 2 SELECT movidos**: se escriben con placeholders `?` y se adaptan a `%s` vía `adapt_params` (idéntico idiom que `prizes/team_prizes_writer.py`). En producción el resultado es idéntico al `%s` inline anterior; contra el fake SQLite de `conftest.py` funciona sin cambiar el resultado (BR1.2 preservado).
- **`fetch_players_by_ids`** siempre consulta vía el puerto; el guard histórico `hasattr(self.dm, 'db')` desaparece del cálculo. En producción `DataManagerV2` tiene `db`, así que el payload es idéntico. Bajo el stub de test, `fetch_players_by_ids` devuelve `{}` (reproduce la rama sin-DB anterior).
- **Semántica de cachés preservada (FR2.3)**: `_team_cache` sigue mezclando claves por `team_id` (de `_safe_team_info`) y por `championship_id` (de `_build_team_lookup`), y `_player_cache['__teams_loaded__']` guarda la carga one-shot; la fachada expone `_team_cache`/`_player_cache` como los MISMOS dicts que muta la capa de cálculo.
- **Compat de `self.dm`**: la fachada expone `self.dm = getattr(port, "dm", port)` para callers que inspeccionaban el atributo histórico.
- **Entorno**: Python del sistema es 3.14 (no 3.12); se creó venv efímero y se instaló `requirements.txt` (que ya NO incluye `libsql-experimental`, retirado como dead code). `JWT_SECRET` efímero de arranque. Práctica aprendida aplicada.

## Deviations respecto al plan

- Ninguna material. La única precisión: el `conftest.py` con `fake_db`/`_FakeInMemoryDB` SÍ existe, pero en `backend/conftest.py` (no en `backend/tests/`); se reutilizó su fixture `fake_db` para el test de contrato del adaptador (el plan preveía un doble in-memory ad-hoc; se prefirió la fixture compartida existente, mismo contrato `get_connection`/`get_cursor`/`adapt_params`).

## Verificación

- Unit-scoped: `cd backend && python -m pytest tests/test_analytics_service.py -v` → **16 passed**.
- Regresión completa: `cd backend && python -m pytest --cov=app` → **218 passed, 3 xfailed**, cobertura total **29.75%** ≥ piso **27** (no se tocó el piso).
- `ruff format` + `ruff check --config ruff.toml` SOLO sobre `app/services/analytics/` → 3 ficheros formateados, **All checks passed!**. No se reformateó ningún brownfield.
