# Entities — Sync Domain Decomposition (unit: sync-domains-decomposition)

This is a **structural refactor with strict functional equivalence**: no new
persisted data and no new observable shapes are introduced. The entities below
are the *existing* logical shapes the extracted sync domains already produce and
consume; they are modelled here so the business rules (`rules.md`) and workflows
(`functional-spec.md`) can reference them precisely. The physical persistence is
owned, unchanged, by `DataManagerV2` (`data_manager_v2.py`), which this refactor
does not touch (NFR2).

## Sources

- `aidlc/spaces/default/intents/261002-sync-god-file-8/inception/requirements-analysis/requirements.md` (FR1–FR6, NFR1–NFR9)
- Brownfield code (de-facto domain design; refactor scope skips units-generation and domain-design):
  - `backend/app/services/sync/clauses/` and `backend/app/services/sync/match_odds/` (reference pilots)
  - `backend/app/services/prizes/calculator.py`, `prizes/team_prizes_writer.py`
  - `backend/app/services/data_sync_service.py` (the god-file being decomposed)
- CodeKB: `aidlc/spaces/default/codekb/futmondo-analytics/` (architecture, code-structure, component-inventory)

```yaml
source_of_truth: entities
scope_note: >
  Refactor with strict functional equivalence. No entity, attribute, or shape
  below is new; each mirrors an existing observable contract that must be
  preserved byte-for-byte after extraction (FR5.2, NFR1).

entities:
  - name: SyncResult
    description: >
      The observable per-domain return payload of every DataSyncService.sync_<domain>()
      method. Its shape intentionally DIVERGES between domains and must be
      reproduced identically after extraction (FR5.1, FR5.2). It is a logical
      value object (a plain dict in code), never persisted by the sync layer.
    attributes:
      - name: status
        type: string
        required: true
        allowed_values: ["success", "no_new_data", "error"]
        constraints: >
          Resolution rule is per-domain and preserved verbatim. Pilots:
          "success" when records_synced > 0 else "no_new_data"; "error" on
          caught failure. Other domains may always return "success" on the
          happy path (e.g. match_odds). The exact per-domain rule is frozen.
      - name: records_synced
        type: integer
        required: false
        constraints: Present on happy-path payloads that report a count; omitted on error payloads that only carry error + duration_seconds.
      - name: last_sync_id
        type: string
        required: false
        constraints: Present for incremental domains (e.g. transactions, clauses); the newest ingested id or the previous one.
      - name: matchday
        type: integer
        required: false
        constraints: Present for round-scoped domains (e.g. match_odds, round_rankings).
      - name: duration_seconds
        type: number
        required: true
        constraints: Wall-clock seconds; present on every payload including error.
      - name: error
        type: string
        required: false
        constraints: Present only on status == "error"; carries str(exception), never credentials (NFR5, BR4.2 of the pilots).
    entity_level_constraints:
      - The set of keys present per domain is frozen; a domain's happy-path and error-path key sets must match the historical inline method exactly (FR5.2).
      - Divergence of shape between domains is intentional and must NOT be uniformised (requirements Assumptions; Out of Scope).

  - name: SyncMetadataRecord
    description: >
      The per-(championship, data_type) bookkeeping row written through
      DataManagerV2.update_sync_metadata(...). Persistence is owned by
      DataManagerV2 and unchanged; modelled here because every orchestrator
      must forward ONLY the kwargs its historical inline call supplied, so the
      persisted row is identical (FR1.3).
    attributes:
      - name: championship_id
        type: string
        required: true
      - name: data_type
        type: string
        required: true
        constraints: The domain key (e.g. "clauses", "match_odds", "transactions").
      - name: last_sync_id
        type: string
        required: false
      - name: last_sync_date
        type: datetime
        required: false
      - name: last_sync_matchday
        type: integer
        required: false
      - name: records_synced
        type: integer
        required: false
        defaults: "DataManagerV2 default when the inline call did not pass it"
      - name: sync_duration_seconds
        type: number
        required: false
      - name: sync_status
        type: string
        required: false
      - name: error_message
        type: string
        required: false
        constraints: str(exception) only; never credentials/tokens (NFR5).
    entity_level_constraints:
      - Each orchestrator forwards ONLY the keyword arguments its historical inline call actually supplied; the rest keep DataManagerV2's own defaults (FR1.3). This preserves the persisted row verbatim.

  - name: SyncDomain
    description: >
      A logical bounded context for one sync data_type. After the refactor each
      lives under backend/app/services/sync/<domain>/ as the proven triad:
      orchestrator (application) + domain port (consumer-owned Protocol) +
      infrastructure adapter (sole DataManagerV2 touch point). Modelled as the
      organising entity of this unit of work.
    attributes:
      - name: name
        type: string
        required: true
        unique: true
        allowed_values:
          - transactions
          - punishments_bonuses
          - dream_teams_mvps
          - rosters
          - round_rankings
          - player_performance
          - players_full
          - prizes
          - clauses        # already extracted (pilot)
          - match_odds     # already extracted (pilot)
        constraints: The 10 domains behind DataSyncService's 10 public sync_* methods.
      - name: public_method
        type: string
        required: true
        constraints: >
          The frozen facade method that delegates to this domain's orchestrator
          (FR3.1). Name↔key divergences are preserved (see SyncAllResult).
      - name: extraction_status
        type: string
        required: true
        allowed_values: ["extracted-pilot", "to-extract-inline", "to-uniformise"]
        constraints: >
          clauses/match_odds = extracted-pilot; the 7 inline domains =
          to-extract-inline; prizes = to-uniformise (calculator + atomic writer
          already exist under prizes/).
      - name: ingestion_throttle_seconds
        type: number
        required: false
        allowed_values: [0.3, 0.2, 0.1, 0.05]
        constraints: Observable time.sleep throttle per domain; preserved by the orchestrator (requirements Constraints).
      - name: pagination_limit
        type: integer
        required: false
        allowed_values: [50, 1000]
        constraints: Observable page/pagination limit per domain; preserved by the orchestrator (requirements Constraints).
    relationships:
      - "SyncDomain (1) produces (1) SyncResult — one observable payload per sync() call"
      - "SyncDomain (1) writes (0..1) SyncMetadataRecord — via its persistence port, per sync() call"

  - name: SyncAllResult
    description: >
      The aggregate payload of DataSyncService.sync_all(). A frozen dict with 10
      literal keys in fixed order, each value a per-domain SyncResult. The router
      worker _run_sync_in_background depends on these keys and order (FR3.2).
    attributes:
      - name: keys_in_fixed_order
        type: list
        required: true
        constraints: >
          Exact order: players, transactions, clauses, punishments_bonuses,
          dream_teams, player_performance, rosters, team_standings, match_odds,
          prizes.
      - name: name_key_divergences
        type: list
        required: true
        constraints: >
          "team_standings" ← sync_round_rankings(); "dream_teams" ←
          sync_dream_teams_mvps(); "players" ← sync_players_full(). Preserved
          verbatim (FR3.2).
    relationships:
      - "SyncAllResult (1) aggregates (10) SyncResult — one per domain, keyed and ordered as frozen"
```

## Entity summary

The refactor introduces **no new data**. Four logical shapes govern the work:

- **SyncResult** — the per-domain return payload. Its per-domain divergence
  (keys present, status resolution) is a frozen contract to reproduce exactly.
- **SyncMetadataRecord** — the bookkeeping row persisted by `DataManagerV2`
  (unchanged). Orchestrators must forward only the kwargs the inline code did,
  so the row is byte-identical.
- **SyncDomain** — the organising entity: one bounded context per `data_type`,
  landed as orchestrator + domain port + adapter, with per-domain observable
  throttle and pagination limits preserved.
- **SyncAllResult** — the aggregate `sync_all()` dict with 10 frozen keys in
  fixed order, including the three name↔key divergences the router depends on.

The physical persistence (tables, SQL) stays entirely inside `DataManagerV2` and
the raw SQL wrapped verbatim in each domain's adapter; this unit models the
logical contracts those shapes must honour, not a new schema.
