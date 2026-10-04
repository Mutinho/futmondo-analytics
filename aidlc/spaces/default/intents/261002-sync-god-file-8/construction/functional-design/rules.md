# Business Rules — Sync Domain Decomposition (unit: sync-domains-decomposition)

The "business rules" of a strict-equivalence refactor are **invariants and
structural constraints** that preserve observable behaviour while relocating
code. Each rule traces to a functional requirement in `requirements.md`.

## Sources

- `aidlc/spaces/default/intents/261002-sync-god-file-8/inception/requirements-analysis/requirements.md` (FR1–FR6, NFR1–NFR9, Constraints)
- Pilots `backend/app/services/sync/clauses/`, `sync/match_odds/` (the fixed reference mold)
- `backend/app/services/data_sync_service.py` (frozen public surface + raw SQL points)
- Interview answers Q1–Q3 (`functional-design-questions.md`)

```yaml
source_of_truth: rules
rules:
  - id: BR1.1
    statement: Each of the 7 inline sync domains is extracted under backend/app/services/sync/<domain>/ as orchestrator.py (application) + domain/ports.py (consumer-owned typing.Protocol, no SQL/framework) + infrastructure/<domain>_adapter.py (sole DataManagerV2 touch point).
    category: constraint
    applies_to: SyncDomain (extraction_status == to-extract-inline)
    trigger: Extracting a domain
    logic: IF a domain is extracted THEN it must replicate the pilot triad exactly (orchestrator + domain port + adapter) — no other layering.
    violation_behavior: Design/implementation rejected; does not match the proven mold.
    source: FR1.1

  - id: BR1.2
    statement: Each public DataSyncService.sync_<domain> becomes a thin delegation — lazy-import the orchestrator and adapter, instantiate with client=self.client, championship_id=self.championship_id, data=DataManager<Domain>Adapter(dm=self.dm), and return orchestrator.sync().
    category: constraint
    applies_to: DataSyncService public sync_* methods
    trigger: After a domain is extracted
    logic: IF a domain is extracted THEN its facade method contains only delegation (no business/ingestion logic remains inline).
    violation_behavior: Facade still carries domain logic; god-file not actually reduced (NFR2).
    source: FR1.2

  - id: BR1.3
    statement: Each adapter builds DataManagerV2(skip_init=True) by default and, in operations like update_sync_metadata, forwards ONLY the kwargs the historical inline call supplied, so the persisted SyncMetadataRecord is identical.
    category: constraint
    applies_to: infrastructure/<domain>_adapter.py
    trigger: Adapter delegates a persistence call
    logic: IF the inline call omitted a kwarg THEN the adapter must also omit it (keep DataManagerV2 defaults); IF it supplied one THEN forward it unchanged.
    violation_behavior: Persisted row diverges from historical row — equivalence broken (FR5.2).
    source: FR1.3

  - id: BR2.1
    statement: Uniformise sync_prizes to the facade pattern — move orchestration to sync/prizes/ (orchestrator), leaving the public method as a thin delegation, reusing the existing pure calculator (prizes/calculator.py) and atomic writer (prizes/team_prizes_writer.replace_team_prizes).
    category: constraint
    applies_to: SyncDomain (prizes)
    trigger: Uniformising prizes
    logic: IF uniformising prizes THEN reuse the existing pure calc + atomic writer; do NOT reimplement them.
    violation_behavior: Prize calculation logic altered — forbidden (FR2.2, BR3.3).
    source: FR2.1

  - id: BR3.1
    statement: DataSyncService preserves byte-for-byte its 10 public sync_* methods and sync_all().
    category: constraint
    applies_to: DataSyncService public surface
    trigger: Any extraction/uniformisation
    logic: IF the refactor touches the facade THEN the method names and count (10 sync_* + sync_all) stay identical.
    violation_behavior: Breaks callers (router worker); forbidden (FR3.3).
    source: FR3.1

  - id: BR3.2
    statement: sync_all() keeps its 10 literal keys and their fixed order, including the name↔key divergences team_standings↔sync_round_rankings, dream_teams↔sync_dream_teams_mvps, players↔sync_players_full.
    category: constraint
    applies_to: SyncAllResult
    trigger: sync_all() invoked
    logic: IF sync_all() returns THEN the key set, order, and name↔key mapping equal the historical dict (players, transactions, clauses, punishments_bonuses, dream_teams, player_performance, rosters, team_standings, match_odds, prizes).
    violation_behavior: Router worker _run_sync_in_background breaks — forbidden (FR3.2).
    source: FR3.2

  - id: BR3.3
    statement: Public signatures (parameters, names) do not change; neither the prize calculation logic nor the atomic set-replacement write pattern already in production is altered.
    category: constraint
    applies_to: DataSyncService public methods; prizes calc/writer
    trigger: Any refactor edit
    logic: IF editing the facade or prizes THEN signatures and prize logic/write pattern remain unchanged.
    violation_behavior: Observable behaviour or caller contract broken (FR2.2, FR3.3).
    source: FR2.2, FR3.3

  - id: BR4.1
    statement: Raw SQL executed directly on self.dm.db outside DataManagerV2 methods (sync_transactions ALTER/UPDATE, _enrich_market_values, _save_favorites CREATE/DELETE/INSERT incl. the Postgres execute_values branch, sync_prizes via get_db()) is wrapped VERBATIM inside the corresponding domain's adapter — the sole infrastructure point — without moving it into data_manager_v2.py or rewriting the SQL.
    category: constraint
    applies_to: raw-SQL helpers
    trigger: Extracting a domain whose inline code ran raw SQL
    logic: IF inline code ran raw SQL on self.dm.db THEN that SQL moves verbatim into the domain adapter, never into DataManagerV2, never rewritten.
    violation_behavior: god-file data_manager_v2.py grows (NFR2) or SQL semantics change (FR5.2).
    source: FR4.1

  - id: BR4.2
    statement: The shared helper _find_championship() (used by dream_teams_mvps and rosters) remains in the facade DataSyncService and is injected (as a callable dependency) into the orchestrators that need it; it is neither duplicated nor extracted into a shared module.
    category: constraint
    applies_to: _find_championship; dream_teams_mvps + rosters orchestrators
    trigger: Extracting a domain that uses _find_championship
    logic: IF an orchestrator needs _find_championship THEN the facade injects the existing callable; the orchestrator does not re-implement or import a shared copy.
    violation_behavior: Duplicated logic or new cross-context coupling (deviation from FR4.2, interview Q3).
    source: FR4.2, Q3

  - id: BR4.3
    statement: The pure, I/O-free helper _find_price_at_date lives in the transactions domain layer (sync/transactions/domain/, e.g. pricing.py) as a pure function, isolating it for characterization without network or DB.
    category: constraint
    applies_to: _find_price_at_date (transactions)
    trigger: Extracting the transactions domain
    logic: IF extracting transactions THEN _find_price_at_date is placed in domain/ as a pure function (no I/O, no framework).
    violation_behavior: Pure logic lands in infrastructure/orchestrator against the agreed placement (interview Q2).
    source: Q2

  - id: BR5.1
    statement: Before extracting each domain, freeze with characterization tests its observable SyncResult payload (shape, keys, values) and its observable ingestion behaviour (pagination limits, operation order).
    category: policy
    applies_to: every domain unit
    trigger: Starting a domain's extraction
    logic: IF a domain is about to be extracted THEN its observable behaviour is characterized first (characterization-first).
    violation_behavior: Extraction without a frozen baseline; equivalence unverifiable.
    source: FR5.1, FR6.2, team mandate (characterization-first)

  - id: BR5.2
    statement: After extraction the SyncResult and observable behaviour of each domain are IDENTICAL to the previous (strict equivalence, no observable change), including per-domain time.sleep throttle (0.3/0.2/0.1/0.05) and pagination limits (50 vs 1000).
    category: constraint
    applies_to: every extracted domain
    trigger: After extraction, suite run
    logic: IF a domain is extracted THEN the characterization suite passes unchanged and observable timing/pagination are preserved.
    violation_behavior: Observable regression — forbidden (NFR1).
    source: FR5.2, Constraints

  - id: BR5.3
    statement: The silent except pass of sync_transactions (around an idempotent ALTER TABLE ... IF NOT EXISTS) is preserved VERBATIM as observable behaviour and documented as registered debt; it is NOT replaced by typed handling in this intent.
    category: constraint
    applies_to: sync_transactions
    trigger: Extracting transactions
    logic: IF extracting transactions THEN keep the except pass verbatim; do not reclassify or type it here.
    violation_behavior: Observable error behaviour changes; out-of-scope reclassification (FR5.3, Out of Scope).
    source: FR5.3

  - id: BR6.1
    statement: Work is organised as one unit per domain with a per-unit gate, so a premature stop leaves domains complete-and-verified, never half-done. Each unit follows characterization-first → extract → suite green → next.
    category: policy
    applies_to: delivery of the refactor
    trigger: Sequencing the work
    logic: IF sequencing THEN one domain = one unit; the unit is not done until its characterization is frozen, extraction applied, and the suite is green.
    violation_behavior: Half-extracted domain merged — breaks FR6 safety guarantee.
    source: FR6.1, FR6.2

  - id: BR6.2
    statement: Definitive extraction order is transactions → punishments_bonuses → dream_teams_mvps → rosters → round_rankings → player_performance → players_full, then the uniformisation of sync_prizes (least→most coupling).
    category: policy
    applies_to: unit sequencing
    trigger: Planning the units
    logic: IF ordering units THEN follow the confirmed least→most-coupling sequence, prizes last.
    violation_behavior: Order deviates from the confirmed plan without re-approval.
    source: FR1.4, Q1

  - id: BR7.1
    statement: No credential or Futmondo/Sofascore token may reach any exception message, repr, exc_info, or log of any extracted adapter; the existing guarantee (_log_integration_failure) is preserved, and the orchestrator failure path logs only str(e)/error_message.
    category: authorization
    applies_to: all extracted orchestrators/adapters
    trigger: Any failure/log path
    logic: IF logging or raising on failure THEN emit only non-credential context (str(e), status, endpoint); never credential material.
    violation_behavior: Credential leak — forbidden (NFR5, affirmed never-credentials rules).
    source: NFR5

  - id: BR7.2
    statement: data_manager_v2.py is neither extended nor modified; data_sync_service.py only shrinks (methods to thin delegation), never grows with new logic. Brownfield files are not mass-reformatted (ruff format); only new files or surgical edits.
    category: constraint
    applies_to: god-files; new domain files
    trigger: Any edit
    logic: IF editing THEN never add to data_manager_v2.py; never add logic to the facade; never mass-reformat brownfield files.
    violation_behavior: god-file debt grows or diffs are inflated (NFR2, NFR7, affirmed rules).
    source: NFR2, NFR7

  - id: BR7.3
    statement: Tests use in-memory doubles/fakes (conftest.py pattern), no network, no real DB, no real credentials; specs assert the effect (payload/state/failure mode), never assert True nor mirror specs. No new paid or non-free-tier dependency is introduced (stdlib sufficient); any hypothetical new library is OSS pinned to an exact version. Identifiers/docstrings/comments in English; user text and commit messages in Spanish.
    category: policy
    applies_to: characterization tests; dependencies; language
    trigger: Writing tests / adding deps / writing code and commits
    logic: IF writing tests THEN use fakes and assert effects; IF adding a dependency THEN OSS + exact pin (none expected); IF writing code THEN English identifiers, Spanish user/commit text.
    violation_behavior: Flaky/useless tests, cost > 0 €, or language policy broken (NFR6, NFR8, NFR9).
    source: NFR6, NFR8, NFR9
```

## Rules summary (derived view)

| ID | Category | Rule (short) | Source |
|----|----------|--------------|--------|
| BR1.1 | constraint | Extract each domain as orchestrator + domain port + adapter (pilot triad) | FR1.1 |
| BR1.2 | constraint | Facade method becomes a thin delegation | FR1.2 |
| BR1.3 | constraint | Adapter forwards only the kwargs the inline call supplied | FR1.3 |
| BR2.1 | constraint | Uniformise prizes reusing existing calc + atomic writer | FR2.1 |
| BR3.1 | constraint | Preserve 10 public sync_* methods + sync_all() byte-for-byte | FR3.1 |
| BR3.2 | constraint | sync_all() keeps 10 literal keys, fixed order, name↔key divergences | FR3.2 |
| BR3.3 | constraint | Signatures, prize logic, atomic write pattern unchanged | FR2.2, FR3.3 |
| BR4.1 | constraint | Raw SQL wrapped verbatim in domain adapter, not moved to DataManagerV2 | FR4.1 |
| BR4.2 | constraint | `_find_championship` stays in facade, injected as callable | FR4.2, Q3 |
| BR4.3 | constraint | `_find_price_at_date` lives in transactions `domain/` as pure fn | Q2 |
| BR5.1 | policy | Characterize observable behaviour before extracting | FR5.1 |
| BR5.2 | constraint | Post-extraction behaviour identical (incl. throttle + pagination) | FR5.2 |
| BR5.3 | constraint | Preserve `sync_transactions` `except: pass` verbatim (registered debt) | FR5.3 |
| BR6.1 | policy | One unit per domain, per-unit gate, characterization-first cycle | FR6.1, FR6.2 |
| BR6.2 | policy | Extraction order least→most coupling, prizes last | FR1.4, Q1 |
| BR7.1 | authorization | No credentials in any error/log of extracted code | NFR5 |
| BR7.2 | constraint | Don't grow god-files; no mass reformat | NFR2, NFR7 |
| BR7.3 | policy | Fakes/no-network tests that assert effects; cost 0 €; language policy | NFR6, NFR8, NFR9 |
