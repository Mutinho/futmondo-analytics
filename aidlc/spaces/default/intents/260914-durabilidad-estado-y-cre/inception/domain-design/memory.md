<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-15T14:50:00Z — FR1.2 se modela como condicional a que CredentialProtection ofrezca medio de re-auth; si el diseño fino de FR5.2 opta por no persistir credencial, FR1.2 no aplica y prevalece FR1.3 (401 accionable). La frontera de componentes no prejuzga esa elección.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T15:00:00Z — Tras la revisión advisory, los ciclos caché↔servicio se resolvieron modelando el caché con dirección única (servicio depends_on caché; caché solo como dependent), en lugar de declarar el ciclo como deliberado. Mantiene el grafo acíclico y simétrico. La referencia UserSession→ProtectedCredential se deja solo como references.entity, no como arista de llamada.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
- 2026-09-15T14:50:00Z — Se conservan SessionStore/TaskManager como caché best-effort (no autoritativos) en lugar de eliminarlos: prioriza preservar el comportamiento observable (C5) y la latencia del camino caliente (NFR2) sobre la simplicidad de "solo BD". Coste: gestionar coherencia caché↔BD, acotada por la regla "BD autoritativa".
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
