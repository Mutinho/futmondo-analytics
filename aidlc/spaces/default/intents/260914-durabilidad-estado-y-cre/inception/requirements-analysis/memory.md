<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-15T12:42:00Z — FR1 se desglosa en durabilidad de sesión (FR1.1–FR1.3, reconstrucción transparente + acción clara) y de tareas (FR1.4–FR1.6, consultable + marca de interrupción + idempotencia relanzable). FR5 se limita a "no en claro en BD" (FR5.1) dejando el mecanismo (re-auth vs cifrado) para diseño (FR5.2). NFR2 (rendimiento) queda sin umbral numérico a validar por medición, por incertidumbre de latencia de Neon free.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T12:48:00Z — Tras revisión advisory (READY) y decisión humana Request Changes: se aplicó R-01 (FR5.1/NFR1 reformulados para ser explícitamente coherentes con la regla dura de project.md sin pre-decidir re-auth vs cifrado) y R-04 (FR1.2 marcado condicional a FR5.2 en el propio requisito). R-02 (umbral NFR2) y R-03 (criterios pass/fail de NFR4/NFR5) se dejan como cuestiones abiertas para diseño, por decisión humana.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
