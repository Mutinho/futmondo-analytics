# Code Summary — Optimización de latencia (read-from-sync)

## Ficheros creados (código de aplicación)

- `backend/app/services/sync_read/__init__.py` — paquete de la capa estrecha (BR1.1).
- `backend/app/services/sync_read/favorites_read.py` — `read_favorites(db, championship_id, user_id) -> (players, has_synced)`. Lee favoritos de `player_favorites`; conjunto free-agent desde `players` JOIN `player_championship_stats` (`owner_team_id IS NULL`) filtrado a los fav_ids; lookup por `player_id` contra `market_today` (hoy) para value/change/averages/matches/points/team/logo/posición; sofascore vía `_sofascore_helpers`; claves de contrato exactas + defaults de la ruta viva cuando el favorito no está en `market_today`; orden `position_order` asc, `value` desc. Favoritos vacíos → `([], True)` (vacío correcto, no sync-miss); 0 filas sincronizadas → `([], False)` (señal de fallback). SQL parametrizado (`db.adapt_params`).
- `backend/app/services/sync_read/market_read.py` — `read_market_catalog(db, championship_id) -> list|None` (catálogo desde `market_today.raw_json`; `None` si 0 filas) + función pura `available_for_bids(max_bid, active_bids_total)`.

## Ficheros creados (tests, `backend/tests/`)

- `test_favorites_read_characterization.py` (3) — Step 3: congela el shape/orden/defaults actuales de `favorites/my` y el `user_info` de `market/today`; verdes contra el código SIN tocar, antes de cambiar la fuente.
- `test_favorites_read.py` (6) — mapeo free-agent, orden preservado, 0 filas → señal de fallback, lookup `market_today` para change/averages, defaults cuando no está en `market_today`, exclusión de no-favoritos y de owned.
- `test_market_read.py` (4) — catálogo desde caché, 0 filas → señal de fallback, cálculo `available_for_bids` incl. degradación de pujas a cero.
- `test_sync_read_endpoints.py` (5) — sirve desde sync sin llamada viva; fallback vivo en sync-miss + log; market desde caché + pujas vivas; pujas degradadas a cero + warning; logs sin credenciales.

## Ficheros modificados (in-place; routers delegan)

- `backend/app/api/v1/endpoints/favorites.py` — `/my` delega en `read_favorites`; sirve desde sync cuando `has_synced`, si no cae a `_get_favorites_live()` (lógica viva preservada verbatim) + `logger.info` sync-miss. Contrato byte-identical.
- `backend/app/api/v1/endpoints/market.py` — catálogo vía `read_market_catalog` (SELECT inline eliminado); se mantiene la llamada viva de pujas (irreducible); degradación a cero + `logger.warning` (BR3.2) sin credencial; `user_info` usa la función pura `available_for_bids()`. Eliminado el import `json_mod` ya no usado. Contrato intacto.

## Decisiones clave de implementación

- Los god-files (`data_sync_service.py`, `data_manager_v2.py`) y el patrón SQL-en-router quedan **intactos**; todo el SQL nuevo vive en `sync_read/` (BR1.1).
- `favorites/my` elimina la descarga viva `get_championship_players` en la ruta normal; la gran ganancia de latencia (NFR1.1).
- `market/today` mantiene su única llamada viva (`POST /1/market/players`) para las pujas del usuario — irreducible sin cambio de esquema; solo el catálogo pasa a leerse de `market_today` (NFR1.2).
- Contrato preservado byte-a-byte, congelado por los tests de caracterización (BR6.1).

## Cobertura de tests

- Unit-scoped (4 ficheros nuevos): **18 passed, 0 failed**. Orden test-after: caracterización verde contra el código sin tocar ANTES de cambiar la fuente; cada capa con sus tests verdes tras implementarla.
- Suite completa final: **440 passed, 3 xfailed (legacy), 0 failed** (eran 422 antes; +18).
- Cobertura total 60,76% (baseline 58,30%); piso `--cov-fail-under=27` intacto (el trinquete solo sube; no se bajó ningún umbral).

## Desviaciones del plan

- Ninguna funcional. Notas de entorno: se usó `backend/.venv-verify` (Python 3.14, learning del proyecto); `ruff` no está instalado en ese venv, así que `ruff check` no se corrió localmente (el gate de CI lo corre en el PR) — el código nuevo sigue las convenciones E/F/I del repo y `py_compile` pasa. Step 13 (code-summary/traceability) lo escribe el orquestador.
