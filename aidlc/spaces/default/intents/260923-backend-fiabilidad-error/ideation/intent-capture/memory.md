<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-23T13:12:08Z — Alcance FR3.2 acotado por Q4=B a `except: pass` de arranque (`main.py`) + migraciones (`scripts/migrate_*`) + `db_connection.py` (9 capturas); las 29 de `data_sync_service.py` quedan como deuda salvo puntos concretos de corrupción, para no ampliar el god-file [memory:M1]. FR4 (Q5=A) = doc de contratos/modos de fallo Sofascore/Futmondo + detección de baneo reflejada en estado. Semántica error (Q6=A): recuperable→degradado y sigue; fatal→aborta limpio sin datos a medias. Cifra real medida: 194 broad-except (7 bare + 187 Exception), no 159+6.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
