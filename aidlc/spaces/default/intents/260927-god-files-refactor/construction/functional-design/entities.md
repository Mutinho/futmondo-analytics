# Modelo de Entidades — Descomposición DDD de los god files (FR13)

> Intent `260927-god-files-refactor`, unidad única, scope `refactor`. Conversation language: Spanish.
>
> En un refactor no se crean entidades de negocio nuevas: este documento **reexpresa en lenguaje DDD (lenguaje ubicuo) los agregados de datos ya existentes** que los repositorios encapsularán al descomponer los cuatro god files. Fuente de la estructura real: `codekb/futmondo-analytics/code-structure.md` (dominios mezclados por god file) y `code-quality-assessment.md`. El objetivo de diseño es asignar cada agregado a un repositorio (SRP) dentro de su bounded context, preservando el comportamiento observable.

## Sources

- `inception/requirements-analysis/requirements.md` — FR1 (oleadas), FR2 (fachada + repositorios), FR2.1 (superficie pública), FR2.2 (aislar SQL).
- `codekb/futmondo-analytics/code-structure.md` — dominios mezclados y agregados por god file.
- `codekb/futmondo-analytics/code-quality-assessment.md` — inventario de `cursor.execute` por fichero y cobertura.
- Petición del usuario (2026-09-27): "lo más DDD posible, separación de responsabilidades, SOLID, DRY".

## Bounded contexts

Cada god file se convierte en un bounded context bajo `backend/app/services/<contexto>/`:

- `data_manager/` — persistencia central (mayor número de agregados).
- `sync/` — orquestación de sincronización (consume agregados de `data_manager`).
- `assistant/` — asistente conversacional (contexto propio + lectura de otros).
- `analytics/` — cálculos analíticos (consume agregados de `data_manager` vía interfaces).

```yaml
aggregates:
  # --- Bounded context: data_manager ---
  - name: Player
    context: data_manager
    root: Player
    description: Jugador y sus estadísticas por campeonato; raíz del agregado de jugadores.
    value_objects: [PlayerId, MarketValue, ClauseValue]
    attributes:
      - { name: player_id, type: identifier, required: true, unique: true }
      - { name: name, type: string, required: true }
      - { name: position, type: string, required: false }
      - { name: real_team, type: string, required: false }
      - { name: market_value, type: money, required: false }
    repository: PlayerRepository
    preserved_methods: [save_player, save_players, save_players_batch, delete_orphan_players, get_player_by_id, save_player_championship_stats, get_clausulable_player_stats, get_player_streak_data, get_free_agent_candidates, get_all_players_with_points, get_users_unique_players_stats]
  - name: TeamUser
    context: data_manager
    root: Team
    description: Equipo de fantasy y su usuario propietario; agregado de equipos/usuarios.
    value_objects: [TeamId, UserId]
    attributes:
      - { name: team_id, type: identifier, required: true, unique: true }
      - { name: user_id, type: identifier, required: true }
      - { name: name, type: string, required: true }
    repository: TeamUserRepository
    preserved_methods: [save_team, get_team_by_id, get_user_by_id, get_user_id_by_name, get_all_users_with_points, ensure_championship_exists]
  - name: Transaction
    context: data_manager
    root: Transaction
    description: Movimientos de mercado y pressroom (altas/bajas/pujas).
    value_objects: [Money, TransactionDate]
    attributes:
      - { name: transaction_id, type: identifier, required: true, unique: true }
      - { name: player_id, type: identifier, required: true, references: Player }
      - { name: amount, type: money, required: true }
      - { name: kind, type: enum, allowed: [buy, sell, pressroom], required: true }
    repository: TransactionRepository
    preserved_methods: [save_pressroom_transactions, save_player_transactions, save_market_players, get_transactions_raw, get_user_transactions, get_all_player_transactions]
  - name: Clause
    context: data_manager
    root: Clause
    description: Cláusulas de rescisión parseadas por jugador/equipo.
    attributes:
      - { name: clause_id, type: identifier, required: true, unique: true }
      - { name: player_id, type: identifier, required: true, references: Player }
      - { name: amount, type: money, required: true }
    repository: ClauseRepository
    preserved_methods: [parse_clause_text, save_clauses, get_user_clauses_stats, get_clauses_raw]
  - name: PunishmentBonus
    context: data_manager
    root: PunishmentBonus
    description: Castigos y bonificaciones por usuario; incluye dream-team/MVP.
    attributes:
      - { name: id, type: identifier, required: true, unique: true }
      - { name: user_id, type: identifier, required: true, references: TeamUser }
      - { name: amount, type: money, required: true }
      - { name: kind, type: enum, allowed: [punishment, bonus, dream_team, mvp], required: true }
    repository: PunishmentBonusRepository
    preserved_methods: [save_punishments_bonuses, get_user_punishments_bonuses, save_dream_team_mvp, get_dream_team_bonus_stats]
  - name: Standing
    context: data_manager
    root: Standing
    description: Clasificaciones, rankings por jornada, odds y evolución; lecturas que analytics consume.
    value_objects: [Matchday, Ratio]
    attributes:
      - { name: id, type: identifier, required: true, unique: true }
      - { name: team_id, type: identifier, required: true, references: TeamUser }
      - { name: matchday, type: integer, required: true }
      - { name: points, type: integer, required: false }
    repository: StandingRepository
    preserved_methods: [save_team_standing, save_round_ranking, get_team_standings_history, save_match_odds, get_match_odds, get_evolution_data_from_db, get_prizes_by_team, get_latest_matchday]
  - name: Roster
    context: data_manager
    root: Roster
    description: Plantillas por equipo y rendimiento por jugador/jornada.
    attributes:
      - { name: id, type: identifier, required: true, unique: true }
      - { name: team_id, type: identifier, required: true, references: TeamUser }
      - { name: player_id, type: identifier, required: true, references: Player }
    repository: RosterRepository
    preserved_methods: [save_team_roster, save_player_performance, save_player_performance_batch, get_player_performance_history]
  - name: SyncMetadata
    context: data_manager
    root: SyncMetadata
    description: Metadatos de sincronización y noticias/artículos por jornada.
    attributes:
      - { name: id, type: identifier, required: true, unique: true }
      - { name: last_sync_at, type: timestamp, required: false }
    repository: SyncMetadataRepository
    preserved_methods: [save_matchday_article, get_matchday_article, save_pressroom_news, get_matchday_data_for_news, get_last_sync_metadata, update_sync_metadata, should_update_cache]
  - name: DatabaseSchema
    context: data_manager
    root: DatabaseSchema
    description: DDL/migraciones. NO es un agregado de negocio (queda EXCLUIDO del recuento de agregados y de BR2.4); se aísla como servicio de infraestructura de esquema SchemaInitializer. Preserva el método público reset_database y la DDL privada (_init_database, _ensure_schema_updates).
    attributes:
      - { name: version, type: string, required: false }
    repository: SchemaInitializer
    preserved_methods: [reset_database]

  # --- Bounded context: assistant ---
  - name: AssistantUsage
    context: assistant
    root: AssistantUsage
    description: Rate-limit/uso del asistente; agregado propio con su tabla.
    attributes:
      - { name: id, type: identifier, required: true, unique: true }
      - { name: user_id, type: identifier, required: true }
      - { name: window_start, type: timestamp, required: true }
      - { name: count, type: integer, required: true, default: 0 }
    repository: AssistantUsageRepository
    preserved_methods: [get_assistant_service, ask]

entity_level_constraints:
  - "Ningún agregado cruza su bounded context: un repositorio pertenece a exactamente un contexto (SRP)."
  - "El acceso a datos de un agregado ocurre SOLO a través de su repositorio; no queda SQL crudo fuera de infrastructure/ (FR2.2)."
  - "Los identificadores (PlayerId, TeamId, UserId, …) son value objects inmutables; su semántica no cambia respecto al código actual (preservación de comportamiento)."

relationships:
  - { from: Transaction, to: Player, cardinality: "many-to-one", direction: "Transaction → Player" }
  - { from: Clause, to: Player, cardinality: "many-to-one", direction: "Clause → Player" }
  - { from: Standing, to: TeamUser, cardinality: "many-to-one", direction: "Standing → TeamUser" }
  - { from: Roster, to: TeamUser, cardinality: "many-to-one", direction: "Roster → TeamUser" }
  - { from: Roster, to: Player, cardinality: "many-to-one", direction: "Roster → Player" }
  - { from: PunishmentBonus, to: TeamUser, cardinality: "many-to-one", direction: "PunishmentBonus → TeamUser" }
  - { from: AssistantUsage, to: TeamUser, cardinality: "many-to-one", direction: "AssistantUsage → TeamUser (identidad de usuario como value object UserId)" }
```

## Resumen del conjunto de entidades

La descomposición identifica **8 agregados** en `data_manager` (Player, TeamUser, Transaction, Clause, PunishmentBonus, Standing, Roster, SyncMetadata) — cada uno mapeado 1:1 a un repositorio (SRP, BR2.4) — **más** un servicio de infraestructura de esquema (`SchemaInitializer` para DDL/migraciones) que **NO es agregado** y por tanto queda excluido del recuento de agregados y de BR2.4. En `assistant` hay **1 agregado** propio (AssistantUsage). Los contextos `sync` y `analytics` **no poseen agregados persistentes propios**: son contextos de aplicación que orquestan (sync) o calculan (analytics) consumiendo los repositorios de `data_manager` a través de sus interfaces de dominio (DIP).

La suma de `preserved_methods` de los 8 agregados + `SchemaInitializer` cubre los **51 métodos públicos** reales de `DataManagerV2` (verificado por inspección: `grep` de `def` públicos), que es la superficie que la fachada debe seguir exponiendo sin cambio observable (FR2.1); es el contrato que la caracterización congela antes de mover código (FR3, BR1.1/BR1.3). Los métodos **privados** de soporte (p. ej. `_ensure_user`, `_get_or_create_user_id`, `_init_database`, `_ensure_schema_updates`) NO forman parte de la superficie pública: se reubican junto al repositorio/servicio de su agregado como detalle de implementación, sin contrato de preservación observable propio (su efecto se preserva indirectamente vía los métodos públicos que los usan).
