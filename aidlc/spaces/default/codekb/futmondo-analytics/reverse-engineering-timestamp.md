# Reverse Engineering Timestamp

## Run Record

- Date: 2026-10-23
- Commit: 9f38a43d6f60e7c5caf8cad4077ef44e57d14efd

## Alcance del escaneo

Refresco incremental **enfocado en el sync completo de jugadores** (focused
scan, NO reconstrucción desde cero) para la etapa reverse-engineering del intent
`261023-sync-jugador-completo`. Proyecto brownfield `futmondo-analytics` (repo
raíz). Profundidad: Minimal.

El store previo (`261023-latencia-market-favorito`, `kind: partial`, fingerprint
`e5c67fd00a2ad3d97077cc4241cd239876f17cc5`) se trata como **STALE** respecto a
este intent (su foco fue latencia, no la escritura del sync de jugadores).
Regla de merge aplicada (store STALE + run enfocado): se **preserva** la prosa de
los 9 artefactos previos y se **extiende** con el flujo player-sync (escritura
`sync_players_full` → `players`/`player_championship_stats`; el gap de campos
points/change/medias-detalle/logo; `player_performance` y `market_today` como
únicas fuentes actuales) y la capa `services/sync_read/`. Para la regla STALE,
`analyzed.paths`/`analyzed.components` registran **solo este run**, se preserva la
prosa previa, y las rutas analizadas del store previo se **degradan a
`shallow.paths`**. `kind: partial` (sin `./`).

### Analizado en profundidad este run

- `backend/app/services/sync/players_full/orchestrator.py` —
  `PlayersFullSyncOrchestrator.sync()`.
- `backend/app/services/sync/players_full/infrastructure/players_full_adapter.py`
  — `DataManagerPlayersFullAdapter`.
- `backend/app/services/sync/players_full/domain/ports.py` —
  `PlayersFullSyncDataPort`.
- `backend/app/services/data_manager/players/` — adapter/service/port.
- `backend/app/services/data_manager/performance/` — adapter/port
  (`player_performance`, única fuente de `points`).
- `backend/app/services/data_manager/schema_lifecycle/` — adapter/service/port
  (DDL de `players`/`player_performance`/`player_championship_stats`).
- `backend/app/services/sync_read/` — `favorites_read.py`, `market_read.py`,
  `__init__.py`.
- `backend/app/services/futmondo_client.py` — `FutmondoClient`
  (`get_championship_players`, `_make_request`, candidatos por jugador).
- `backend/app/api/v1/endpoints/favorites.py` — `get_my_favorites`,
  `_get_favorites_live`, `mark`, `unfollow`.

### Solo ojeado

- Resto de responsabilidades `data_manager/` (`prizes`, `clauses`,
  `transactions`, `teams_standings`, `dream_teams_mvp`, `market_roster`,
  `punishments_bonuses`, `users_stats_evolution`, `sync_metadata_cache`,
  `news_articles`, `match_odds`) — por estructura DDD.
- `data_sync_service.py` / `data_manager_v2.py` (god-files) — por rol de facade.
- `assistant_service.py` (puebla `market_today`), `_sofascore_helpers.py`.
- Rutas de latencia del store previo (`market.py`/`balances.py`/`roster.py`/
  `sync.py`/`stores/`), degradadas a `shallow.paths` bajo la regla STALE.

### Dejado fuera

- Resto de `backend/` fuera del flujo player-sync; todo `angular-app/`.
- Instalación de AI-DLC (`.kiro/`, `.claude/`, `.codex/`, `.cursor/`, `.aidlc/`,
  `aidlc/` workspace).
- Build outputs / deps / caches (`node_modules/`, `.angular/`, `dist/`,
  `coverage/`, `__pycache__/`, `.pytest_cache/`).
- `.github/workflows/`, `docs/`, `cron/`, `proxy/`, `spikes/`, `scripts/`.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261023-sync-jugador-completo
fingerprint: unknown
analyzed:
  paths:
    - backend/app/services/sync/players_full/
    - backend/app/services/data_manager/players/
    - backend/app/services/data_manager/performance/
    - backend/app/services/data_manager/schema_lifecycle/
    - backend/app/services/sync_read/
    - backend/app/services/futmondo_client.py
    - backend/app/api/v1/endpoints/favorites.py
  components:
    - Players full sync orchestrator
    - Players full sync adapter
    - Players full sync port
    - Players data adapter
    - Players service
    - Players data port
    - Performance data adapter
    - Performance data port
    - Schema lifecycle adapter
    - Schema lifecycle service
    - Favorites read-from-sync
    - Market read-from-sync
    - Favorites router
    - Futmondo client
shallow:
  paths:
    - angular-app/src/app/features/market/
    - backend/app/api/v1/endpoints/market.py
    - backend/app/api/v1/endpoints/sofascore_detail.py
    - backend/app/api/v1/endpoints/balances.py
    - backend/app/api/v1/endpoints/roster.py
    - backend/app/api/v1/endpoints/sync.py
    - backend/app/services/data_manager/
    - backend/app/services/data_sync_service.py
    - backend/app/services/data_manager_v2.py
    - backend/app/services/assistant_service.py
    - backend/app/services/sofascore_client.py
    - backend/app/stores/
```

## Sources

- Herramientas de lectura/listado sobre el repo `/home/javi/futmondo-analytics`.
- `git rev-parse HEAD` → commit `9f38a43d6f60e7c5caf8cad4077ef44e57d14efd`.
- Hallazgos verificados previos en
  `aidlc/spaces/default/knowledge/aidlc-shared/sync-jugador-campos.md`
  (flujo, gap de campos, evidencia de producción con token fresco 2026-10-23).

## Assumptions & Open Questions

- Store previo `261023-latencia-market-favorito` tratado como **STALE** para
  este intent: solo este run entra en `analyzed.paths`/`analyzed.components`; la
  prosa previa se preserva y las rutas de latencia previas se degradan a
  `shallow.paths`.
- `kind: partial`: `analyzed.paths` NO incluye `./`.
- **`fingerprint: unknown`**: este scan corrió en un sub-agente sin acceso a
  `aidlc engine workspace codekb-scope-diff --mint` (no se ejecutan comandos
  `aidlc engine`/lifecycle en esta tarea). El fingerprint debe minarse sobre la
  `analyzed.paths` final y pegarse verbatim en la publicación, y el bloque
  validarse con `codekb-scope-diff --check` antes de publicar desde staging.
- La DDL de `market_today` no está en `schema_lifecycle` (la crea/pobla
  `assistant_service`); se infiere de los SELECT de `favorites_read`/`market_read`.
- **INCÓGNITA CRÍTICA (Functional Design)**: ¿trae `/5/league/championshipplayers`
  los campos que faltan (points/change/medias-detalle/logo) por jugador?
  Verificar con llamada cruda (token server-side) antes de diseñar el
  enriquecimiento.
