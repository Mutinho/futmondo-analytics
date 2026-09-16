<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T11:58:00Z — Focused scan del backend sobre un store STALE (previo del intent bundle-optimization, foco frontend). El compare devolvió NARROWER: la cobertura profunda del frontend Angular se degradó a shallow, algo esperado y aceptado para este intent de backend.
- 2026-09-15T11:58:00Z — El fingerprint del bloque Scope of Analysis debe mintarse sobre la lista EXACTA de analyzed.paths (archivos individuales), no sobre el directorio `backend/`; codekb-publish computa la fuente sobre esos paths concretos. El primer intento falló con CODEKB_CANDIDATE_STALE por mintar sobre `backend/`; se corrigió mintando sobre la lista exacta (d2b01eb) y publicando con --paths igual a esa lista.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
