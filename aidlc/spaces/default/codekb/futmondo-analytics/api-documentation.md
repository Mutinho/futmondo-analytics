# API Documentation

## Superficies externas (HTTP)

### Auth (`backend/app/auth/routes.py`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/auth/login` | POST | Login con credenciales Futmondo → JWT access + refresh cookie |
| `/auth/refresh` | POST | Renovar access token desde la cookie HttpOnly |
| `/auth/logout` | POST | Revocar sesión |

### REST FastAPI v1 (`backend/app/api/v1/endpoints/`, 23 routers)

Todos los endpoints `/api/v1/*` requieren Bearer token. Esta pasada focaliza los
**8 routers que consumen `DataManagerV2` directamente** (contrato del objetivo):

| Router | Consumo de `DataManagerV2` |
|--------|-----------------------------|
| `statistics.py` | limpio vía facade: `dm.get_users_unique_players_stats` |
| `player_finances.py` | mixto: facade + `cursor.execute` inline (L38) |
| `clausulable_players.py` | mixto: facade + SQL inline (L75–79, L170–179) |
| `user_stats.py` | mixto: facade + SQL inline |
| `sync.py` | vía `DataSyncService.dm` + `get_last_sync_metadata`/`update_sync_metadata` |
| `initialize.py` | directo |
| `matchdays.py` | directo |
| `reset_db.py` | directo (`reset_database`) |

Los demás endpoints (market, balances, analytics, transactions, roster,
sofascore_*, user, championships, favorites, phantoms) y el detalle del dominio
sync quedan como prosa preservada del store previo. La deuda de SQL-en-router (17
de 23 routers con SQL inline) se detalla en `code-quality-assessment.md`.

## Superficie interna — `DataManagerV2` (contrato a PRESERVAR exacto)

Clase `DataManagerV2` en `backend/app/services/data_manager_v2.py`. **Constructor**:
`DataManagerV2(db_path=None, skip_init=True)`. Los 57 métodos y sus firmas se
preservan byte-a-byte en el refactor (equivalencia observable estricta): 8 routers
+ los adapters de `analytics`/`assistant`/`sync` + `data_sync_service` +
`data_initializer_v2` + `futmondo_service` la envuelven verbatim. Agrupación
observada por responsabilidad candidata (a confirmar en Plan Approval), con línea
de referencia:

### 1. schema/lifecycle
`_init_database` (L38), `reset_database` (L368), `_ensure_schema_updates` (L3009),
`_ensure_user` (L835), `_get_or_create_user_id` (L1803),
`_ensure_championship_in_transaction` (L2014), `ensure_championship_exists` (L1990).

### 2. players
`save_player` (L418), `save_players_batch` (L467), `save_players` (L733),
`delete_orphan_players` (L549), `get_all_players_with_points` (L2369),
`get_player_by_id` (L3611), `get_free_agent_candidates` (L3638),
`get_player_streak_data` (L3665).

### 3. teams/standings
`save_team` (L799), `save_team_standing` (L595), `save_round_ranking` (L864),
`get_team_by_id` (L3572), `get_team_standings_history` (L3386),
`get_latest_matchday` (L3374).

### 4. performance
`save_player_performance` (L675), `save_player_performance_batch` (L688),
`save_player_championship_stats` (L3089), `get_player_performance_history` (L3461),
`get_clausulable_player_stats` (L3174).

### 5. transactions
`save_player_transactions` (L940), `save_pressroom_transactions` (L945),
`get_all_player_transactions` (L2416), `get_user_transactions` (L2523),
`get_transactions_raw` (L3504).

### 6. clauses
`parse_clause_text` (L1508), `save_clauses` (L1551), `get_user_clauses_stats`
(L1705), `get_clauses_raw` (L3539).

### 7. punishments/bonuses
`save_punishments_bonuses` (L1330), `get_user_punishments_bonuses` (L1432).

### 8. dream teams / MVP
`save_dream_team_mvp` (L2132), `get_dream_team_bonus_stats` (L2959).

### 9. prizes
`get_prizes_by_team` (L3420).

### 10. market/roster
`save_market_players` (L1831), `save_team_roster` (L1892).

### 11. match odds
`save_match_odds` (L3215), `get_match_odds` (L3320).

### 12. news/articles
`save_matchday_article` (L1118), `get_matchday_article` (L1170),
`save_pressroom_news` (L2256), `get_matchday_data_for_news` (L2794).

### 13. users/stats/evolution
`get_user_id_by_name` (L1204), `get_users_unique_players_stats` (L2266),
`get_all_users_with_points` (L2464), `get_evolution_data_from_db` (L2695).

### 14. sync-metadata/cache
`get_last_sync_metadata` (L2040), `update_sync_metadata` (L2069),
`should_update_cache` (L2262).

> Nota de contrato: los adapters DDD reenvían **sólo** los kwargs que la llamada
> original suministraba y no añaden métodos a `DataManagerV2`. Varios `get_*_by_id`
> devuelven `Optional[...]` (`None` = "no encontrado", contrato legítimo); hay que
> distinguirlos del `None` "fallo tragado" en characterization (ver
> `code-quality-assessment.md`).

## Integraciones externas (clientes salientes)

Prosa preservada del store previo: **API Futmondo** (`futmondo_client.py`,
excepciones tipadas `IntegrationBanError` fatal /
`IntegrationTimeoutError`/`IntegrationUnparseableError`/`IntegrationRequestError`
recuperables; mantiene credenciales fuera de sus errores) y **API Sofascore**
(`sofascore_client.py` vía `curl_cffi`). `DataManagerV2` no habla con estas APIs:
recibe los datos ya ingeridos y los persiste.
