# Entities — Functional Design (`261001-sync-god-file-resto`)

> Refactor de equivalencia estricta: NO hay nuevo esquema físico. Este modelo es
> **lógico** y refleja el esquema existente en Neon y los contratos observables
> del sync. La entidad de diseño central es el `SyncResult` por dominio (contrato
> a congelar, FR5.3/FR7.1). Idioma de artefacto: castellano; identificadores en
> inglés.

## Source of truth

```yaml
entities:
  # --- Contrato observable del sync (a congelar en caracterización, FR5.3/FR7.1) ---
  - name: SyncResult
    description: >
      Diccionario de retorno observable de cada método público sync_*. Su forma
      NO es uniforme entre dominios; la variante exacta por dominio es el
      contrato que la caracterización congela antes de extraer. Base común +
      claves específicas por dominio.
    attributes:
      - name: status
        type: string
        required: true
        allowed_values: ["ok", "error"]
        notes: Clave base presente en todos los dominios.
      - name: records_synced
        type: integer
        required: false
        min: 0
        notes: Presente en dominios por-registro (clauses, transactions, punishments_bonuses, rosters, players_full, dream_teams).
      - name: last_sync_id
        type: integer
        required: false
        notes: Variante de cursor por id (transactions, clauses).
      - name: last_sync_matchday
        type: integer
        required: false
        notes: Variante de cursor por jornada (dominios basados en matchday).
      - name: rounds_synced
        type: integer
        required: false
        min: 0
        notes: Variante por rondas (round_rankings/player_performance).
      - name: last_matchday
        type: integer
        required: false
        notes: Acompaña a rounds_synced en round_rankings.
      - name: rounds_processed
        type: integer
        required: false
        min: 0
        notes: Variante de prizes.
      - name: stale_prizes_removed
        type: integer
        required: false
        min: 0
        notes: Variante de prizes (filas borradas en el reemplazo atómico).
      - name: duration_seconds
        type: number
        required: false
        min: 0
        notes: Presente donde el método público lo reporta hoy; se preserva verbatim.
    constraints:
      - La variante exacta (qué claves aparecen y su tipo) es fija POR DOMINIO y
        debe preservarse byte-a-byte respecto al comportamiento actual (FR5.3).
      - En fallo recoverable el paso se marca DEGRADED vía sync_step_status sin
        corromper datos; en fatal se propaga excepción tipada. (FR6.2)

  # --- Dominios de datos ingestados/persistidos (lógico; esquema existente) ---
  - name: SyncDomain
    description: >
      Abstracción lógica de un dominio de sincronización extraíble. No es una
      tabla; representa la unidad de extracción (clauses, transactions,
      punishments_bonuses, dream_teams, rosters, round_rankings/team_standings,
      player_performance, players_full) y, aparte, prizes a uniformar.
    attributes:
      - name: domain_name
        type: string
        required: true
        unique: true
        allowed_values:
          - clauses
          - transactions
          - punishments_bonuses
          - dream_teams
          - rosters
          - round_rankings
          - player_performance
          - players_full
          - match_odds
          - prizes
      - name: public_method
        type: string
        required: true
        notes: >
          Método público de DataSyncService (sync_clauses, sync_transactions,
          sync_punishments_bonuses, sync_dream_teams_mvps, sync_rosters,
          sync_round_rankings, sync_player_performance, sync_players_full,
          sync_match_odds, sync_prizes). Firma preservada verbatim (FR5.1).
      - name: sync_all_key
        type: string
        required: true
        notes: >
          Clave literal en el dict de sync_all(). Mapeo no-trivial:
          players_full -> players; dream_teams_mvps -> dream_teams;
          round_rankings -> team_standings. (FR5.2)
      - name: sync_result_shape
        type: reference
        references: SyncResult
        required: true
        notes: Variante del SyncResult observada hoy para este dominio.
    constraints:
      - El orden de los 10 dominios en sync_all() es fijo (FR5.2); players
        primero por dependencia FK.

  - name: IngestedRecord
    description: >
      Representación lógica de los datos crudos que un dominio ingesta desde la
      API Futmondo y persiste vía DataManagerV2. No se modela el esquema físico
      (existente, sin cambios): es el payload por-dominio que el adapter escribe.
    attributes:
      - name: domain_name
        type: reference
        references: SyncDomain
        required: true
      - name: source_endpoint
        type: string
        required: true
        notes: Método de FutmondoClient que lo provee (p.ej. get_round_ranking).
      - name: persistence_calls
        type: list
        required: true
        notes: >
          Métodos de DataManagerV2 invocados hoy para persistir este dominio
          (nombres + argumentos verbatim). Es lo que el domain port declara y la
          caracterización congela (FR3.1/FR7.2).
    constraints:
      - El esquema físico NO cambia; sólo se mueve el punto de invocación del SQL
        al adapter de infraestructura (FR3.1).

relationships:
  - from: SyncDomain
    to: SyncResult
    cardinality: "1:1"
    direction: produces
    notes: Cada dominio produce una variante fija de SyncResult.
  - from: SyncDomain
    to: IngestedRecord
    cardinality: "1:N"
    direction: ingests-and-persists
    notes: Un dominio ingesta/persiste uno o más tipos de registro.
```

## Resumen del modelo

El refactor no introduce entidades de datos nuevas ni cambia el esquema de Neon;
por eso el modelo es deliberadamente lógico. La entidad de diseño que importa es
el **`SyncResult`** porque es el contrato observable que la caracterización
congela por dominio antes de extraer (FR5.3, FR7.1). `SyncDomain` cataloga las
diez operaciones de sync y su mapeo método↔clave de `sync_all()` (incluido el
mapeo no-trivial `players_full→players`, `dream_teams_mvps→dream_teams`,
`round_rankings→team_standings`). `IngestedRecord` captura, por dominio, el
endpoint de ingesta y las llamadas de persistencia a `DataManagerV2` que el
domain port declarará verbatim y que el adapter delegará 1:1.
