# Functional Design — Preguntas (refactor data_manager_v2)

Intent: `261005-data-manager-god-file`. Profundidad: Minimal. Las decisiones
estratégicas ya están cerradas en `requirements.md` (patrón DDD fijado,
characterization-first, equivalencia estricta, deuda diferida). Aquí sólo queda
la decisión de diseño que el `functional-spec.md` materializa: el **inventario
de responsabilidades y su agrupación/orden**. El inventario y el orden EXACTOS
se confirman formalmente en Plan Approval (FR5.1); esta pregunta fija la
granularidad y el criterio de orden que el diseño funcional documenta como
punto de partida.

Superficie pública real enumerada del god-file (contrato a preservar byte a
byte — resuelve R-01 del reviewer de requisitos): **57 métodos** = **51
públicos + 6 privados** (`__init__(db_path=None, skip_init=True)`,
`_init_database`, `_ensure_user`, `_get_or_create_user_id`,
`_ensure_championship_in_transaction`, `_ensure_schema_updates`).

## Q1 — Agrupación de responsabilidades y criterio de orden de extracción

El escaneo propuso ~14 responsabilidades. Mapeando los 57 métodos reales por su
tabla/dominio, propongo esta agrupación como punto de partida del diseño (el
cierre exacto es en Plan Approval). ¿Qué granularidad y criterio de orden fija
el functional-spec?

Agrupación propuesta (nombre → métodos):
- schema/lifecycle: `_init_database`, `reset_database`, `_ensure_schema_updates`, `ensure_championship_exists`, `_ensure_championship_in_transaction`, `_ensure_user`, `_get_or_create_user_id`
- players: `save_player`, `save_players_batch`, `save_players`, `delete_orphan_players`, `get_player_by_id`, `get_all_players_with_points`, `get_free_agent_candidates`, `get_player_streak_data`
- teams/standings: `save_team`, `save_team_standing`, `save_round_ranking`, `get_team_by_id`, `get_team_standings_history`, `get_latest_matchday`
- performance: `save_player_performance`, `save_player_performance_batch`, `save_player_championship_stats`, `get_player_performance_history`, `get_clausulable_player_stats`
- transactions: `save_player_transactions`, `save_pressroom_transactions`, `get_all_player_transactions`, `get_user_transactions`, `get_transactions_raw`
- clauses: `parse_clause_text`, `save_clauses`, `get_user_clauses_stats`, `get_clauses_raw`
- punishments/bonuses: `save_punishments_bonuses`, `get_user_punishments_bonuses`
- dream-teams/MVP: `save_dream_team_mvp`, `get_dream_team_bonus_stats`
- prizes: `get_prizes_by_team`
- market/roster: `save_market_players`, `save_team_roster`
- match-odds: `save_match_odds`, `get_match_odds`
- news/articles: `save_matchday_article`, `get_matchday_article`, `save_pressroom_news`, `get_matchday_data_for_news`
- users/stats/evolution: `get_user_id_by_name`, `get_users_unique_players_stats`, `get_all_users_with_points`, `get_evolution_data_from_db`
- sync-metadata/cache: `get_last_sync_metadata`, `update_sync_metadata`, `should_update_cache`
- (`get_user_by_id` se asigna a users/stats o a schema/lifecycle según acoplamiento, a cerrar en Plan Approval)

- A. **Un módulo DDD por responsabilidad (~14), orden de menor a mayor
  acoplamiento** (p. ej. empezar por los dominios con menos métodos y menos
  dependencias cruzadas — prizes, match-odds, punishments/bonuses — y terminar
  por schema/lifecycle y players, los más acoplados). El functional-spec
  documenta esta agrupación como entidades-objetivo del refactor y el criterio
  de orden; el inventario y orden exactos se cierran en Plan Approval.
  (Recomendada: granularidad fina = rollback quirúrgico, igual que sync.)
- B. Misma agrupación, pero fijar el orden EXACTO ya aquí (no diferirlo a Plan
  Approval).
- C. Otra agrupación (menos/más módulos).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de la decisión de diseño (modo guiado):

- Q1 — **Un módulo DDD por responsabilidad (~14), orden de menor a mayor
  acoplamiento**; el functional-spec documenta la agrupación de los 57 métodos
  y el criterio de orden como punto de partida, y el inventario y orden EXACTOS
  se cierran en Plan Approval (FR5.1). (A)

Esto, junto con lo ya decidido en `requirements.md` (patrón DDD fijado,
characterization-first, equivalencia estricta, superficie pública de 57 métodos
preservada byte a byte, deuda de errores/corrupción/SQL-en-router diferida),
es la base de los artefactos de diseño funcional (entities.md como inventario de
módulos-objetivo, rules.md como invariantes del refactor, functional-spec.md con
el workflow de extracción por responsabilidad).

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
