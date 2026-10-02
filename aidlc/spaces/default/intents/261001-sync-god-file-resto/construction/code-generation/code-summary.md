# Code Summary — dominio `clauses` (`261001-sync-god-file-resto`)

> Primera entrega del escalón de descomposición del god-file
> `data_sync_service.py`. Refactor brownfield de equivalencia funcional ESTRICTA
> (FR5), characterization-first (FR7). Replica 1:1 el molde `sync/match_odds/`.

## Qué se hizo

Se extrajo `DataSyncService.sync_clauses` (ingesta paginada del endpoint
locker-news, filtrado `styp == 'clause'`, de-dup por `_id`, condiciones de parada
—id previamente sincronizado / 5 páginas vacías consecutivas / límite de 50
páginas—, throttling `time.sleep(0.3)`, try/except por página que loguea y
rompe, y manejo de errores) a un contexto DDD fino, dejando el método público
como delegación.

## Ficheros producidos (nuevos)

- `backend/app/services/sync/clauses/__init__.py` — re-exporta `ClausesSyncOrchestrator`.
- `backend/app/services/sync/clauses/domain/__init__.py`
- `backend/app/services/sync/clauses/domain/ports.py` — `ClausesSyncDataPort`
  (`typing.Protocol` consumer-owned con `get_last_sync_metadata`,
  `save_clauses`, `update_sync_metadata` verbatim; sin SQL ni framework).
- `backend/app/services/sync/clauses/infrastructure/__init__.py`
- `backend/app/services/sync/clauses/infrastructure/clauses_adapter.py` —
  `DataManagerClausesAdapter`, único módulo que toca `DataManagerV2`; delega 1:1;
  `__init__(self, dm=None)` → `DataManagerV2(skip_init=True)`.
- `backend/app/services/sync/clauses/orchestrator.py` — `ClausesSyncOrchestrator`
  alojando la orquestación verbatim; devuelve el `SyncResult` dict.
- `backend/tests/test_sync_clauses_characterization.py` — 8 tests de
  caracterización (happy-path success + no_new_data, de-dup entre páginas, parada
  en id previo, fallo recuperable por página, fallo fatal exterior,
  no-credenciales-en-logs, orden de claves de `sync_all`).

## Ficheros modificados

- `backend/app/services/data_sync_service.py` — `sync_clauses` adelgazado a
  delegación fina al orchestrator (import perezoso del paquete; firma y
  `SyncResult` preservados). Sin `ruff format` masivo; sin tocar otros `sync_*`.
  `data_manager_v2.py` NO se amplió ni modificó.

## SyncResult preservado (equivalencia FR5)

- Happy: `{status: 'success'|'no_new_data', records_synced, last_sync_id, duration_seconds}`
  (`success` si `total_synced > 0`, si no `no_new_data`).
- Fallo: `{status: 'error', error: str(e), duration_seconds}`.
- `last_sync_id = newest_news_id or previous_last_id`.

## Verificación

- `pytest backend/tests/test_sync_clauses_characterization.py -q` → **8 passed**
  tanto contra el código ACTUAL (antes de adelgazar) como tras la extracción.
- `pytest -q --cov=app --cov-fail-under=27` → **259 passed, 3 xfailed**;
  cobertura total **35.73% ≥ 27%** (piso no relajado).
- `ruff check` sobre los ficheros nuevos → **All checks passed** (sin `ruff format`
  masivo sobre el god-file).
- `sync_all()` mantiene sus 10 claves en orden; `clauses` en índice 2;
  `_run_sync_in_background` (sync.py) intacto (misma firma, llamada sin args).

## Dominios restantes (entregas sucesivas, mismo patrón)

`transactions` → `punishments_bonuses` → `dream_teams` → `rosters` →
`round_rankings`/`team_standings` → `player_performance` → `players_full`, y
finalmente uniformar `prizes/`.
