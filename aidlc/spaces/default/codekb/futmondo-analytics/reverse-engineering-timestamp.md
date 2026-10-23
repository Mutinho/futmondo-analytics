# Reverse Engineering Timestamp

## Run Record

- Date: 2026-10-23
- Commit: 1d5ce759785dd09c4e24759005e9089d00288d45

## Alcance del escaneo

Refresco incremental **enfocado en latencia** (focused scan, NO reconstrucción
desde cero) para la etapa reverse-engineering del intent
`261023-latencia-market-favorito`. Proyecto brownfield `futmondo-analytics`
(repo raíz). Profundidad: Minimal.

El store previo (`261020-mercado-pujas`, `kind: partial`, fingerprint
`91bea54f4c5fef127edfff7c22d82934d8951bb1`) es CURRENT y cubre en profundidad la
vista de Mercado del frontend y sus endpoints `market.py`/`sofascore_detail.py`.
Regla de merge aplicada (store CURRENT/partial + run enfocado): se **preserva**
la prosa de los 9 artefactos previos y se **extiende** con la caracterización de
rendimiento de la ruta de petición de `/market/today`, `/favorites/my` y
`/analytics/balances` y el inventario de datos pre-sincronizados por
`data_sync_service`. `analyzed.paths`/`analyzed.components` son la **UNIÓN** del
store y de este run. `kind: partial` (sin `./`).

### Analizado en profundidad este run

- `backend/app/api/v1/endpoints/market.py` — `get_market_today`,
  `_build_market_response`; caché `market_today` + 1 llamada en vivo de pujas.
- `backend/app/api/v1/endpoints/favorites.py` — `get_my_favorites`; 2-3 llamadas
  en vivo (`get_championship_players`, `get_matchday_standings`,
  `get_userteam_roster`).
- `backend/app/api/v1/endpoints/balances.py` — `get_balances`; patrón rápido
  (1 llamada en vivo + reads sincronizados).
- `backend/app/api/v1/endpoints/roster.py`, `sync.py` — mismos patrones de
  llamadas en vivo.
- `backend/app/services/` — `data_sync_service.py` (god-file, orquestadores
  `services/sync/*`), `futmondo_client.py` (`_make_request`, timeout 15 s),
  `db_connection.py` (pool Neon).
- `backend/app/stores/` — `task_repository.py`, `session_repository.py` (ojeados
  por responsabilidad).
- `angular-app/src/app/features/market/` — preservado del store, re-confirmado
  por contrato.

### Solo ojeado

- Orquestadores `services/sync/*`, `photo_service.py`, `assistant_service.py`,
  `sofascore_client.py`, `data_manager/` — por firma/import, no fichero a
  fichero (Minimal).

### Dejado fuera

- Resto de `backend/` fuera de la ruta de latencia; resto de `angular-app/`
  fuera de `features/market/`.
- Instalación de AI-DLC (`.kiro/`, `.claude/`, `.codex/`, `.cursor/`, `.aidlc/`,
  `aidlc/`).
- Build outputs / deps / caches (`node_modules/`, `.angular/`, `dist/`,
  `coverage/`, `__pycache__/`, `.pytest_cache/`, `ios/.build/`).
- `.github/workflows/`, `docs/`, `cron/`, `proxy/`, `spikes/`, `scripts/`.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261023-latencia-market-favorito
fingerprint: e5c67fd00a2ad3d97077cc4241cd239876f17cc5
analyzed:
  paths:
    - angular-app/src/app/features/market/
    - backend/app/api/v1/endpoints/market.py
    - backend/app/api/v1/endpoints/sofascore_detail.py
    - backend/app/api/v1/endpoints/favorites.py
    - backend/app/api/v1/endpoints/balances.py
    - backend/app/api/v1/endpoints/roster.py
    - backend/app/api/v1/endpoints/sync.py
    - backend/app/services/
    - backend/app/stores/
  components:
    - MarketComponent
    - BidDialogComponent
    - ConfirmDialogComponent
    - SofascoreDetailDialogComponent
    - Market router
    - Sofascore detail router
    - Favorites router
    - Balances router
    - Roster router
    - Sync router
    - Data sync service
    - Data manager
    - Futmondo client
    - Sofascore client
    - Endpoint helpers
    - Sofascore helpers
    - DB connection
    - Task store / repo
    - Session store / repo
shallow:
  paths:
    - backend/app/services/sync/
    - backend/app/services/data_manager/
    - backend/app/services/photo_service.py
    - backend/app/services/assistant_service.py
    - backend/app/services/sofascore_client.py
```

## Sources

- Herramientas de lectura/listado sobre el repo `/home/javi/futmondo-analytics`.
- `aidlc engine workspace codekb-scope-diff --repo futmondo-analytics --mint
  --paths angular-app/src/app/features/market/,backend/app/api/v1/endpoints/market.py,backend/app/api/v1/endpoints/sofascore_detail.py,backend/app/api/v1/endpoints/favorites.py,backend/app/api/v1/endpoints/balances.py,backend/app/api/v1/endpoints/roster.py,backend/app/api/v1/endpoints/sync.py,backend/app/services/,backend/app/stores/`
  (fingerprint `e5c67fd00a2ad3d97077cc4241cd239876f17cc5`) y
  `git rev-parse HEAD` (commit `1d5ce759785dd09c4e24759005e9089d00288d45`).

## Assumptions & Open Questions

- Store previo `261020-mercado-pujas` (CURRENT, `partial`, fingerprint
  `91bea54f…`): merge CURRENT, `analyzed.paths`/`analyzed.components` son la
  UNIÓN del store (3 paths de Mercado) y este run (ruta de latencia); la prosa
  previa se preservó y se extendió.
- `kind: partial`: `analyzed.paths` NO incluye `./`.
- `fingerprint` minteado sobre la UNIÓN de `analyzed.paths` con
  `codekb-scope-diff --mint` y pegado verbatim.
- Nombres de tablas de Neon inferidos del SQL de los endpoints y las firmas de
  los orquestadores de sync; el DDL no se abrió.
