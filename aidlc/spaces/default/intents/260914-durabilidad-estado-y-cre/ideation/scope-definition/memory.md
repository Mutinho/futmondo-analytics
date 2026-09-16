<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-09-14T17:14Z — Scope acotado por intent-statement + feasibility ya aprobados: dos capacidades (FR1 durabilidad de estado, FR5 credenciales) con dependencia común en el estado en memoria de SessionStore/TaskManager. Backlog = 2 proto-unidades. Secuenciación natural: riesgo/seguridad primero.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
- 2026-09-15T11:48:00Z — Se declaró la reanudación automática de tareas (PU-7) fuera de alcance (Won't-this-time) para evitar un salto de complejidad que rozaría "reescritura grande"; se persiste el estado pero no se re-lanzan las tareas. Alineado con Q2 (nice-to-have) y Q5 (OUT).
- 2026-09-15T11:48:00Z — Elección concreta de FR5 (re-auth vs. cifrado en reposo) diferida a diseño, conforme a la disciplina de Ideación de no fijar detalle de implementación; ambas vías son coste 0 €, por lo que diferir no introduce riesgo de presupuesto.
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
