<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-15T15:23:00Z — Contract Design aplica pese a no haber fronteras inter-unidad ni API externa nueva: el contrato formal a fijar es la interfaz interna de CredentialProtection (intra-U1), que ADR-003 difirió aquí. Se modela como code-interface (Protocol Python), no como contrato de red (no cruza la red). El mecanismo fino FR5.2 sigue diferido a Functional/NFR design.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T15:27:00Z — Tras la revisión advisory se añadió una nota de armonización de nombre (R-01): can_reauthenticate (contrato, canónico) == canReauthenticate (components.md); una sola operación. R-02 (razón de ejecución de etapa condicional) y R-03 (ReauthMaterial opaco por FR5.2 diferido) se aceptaron como están.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
