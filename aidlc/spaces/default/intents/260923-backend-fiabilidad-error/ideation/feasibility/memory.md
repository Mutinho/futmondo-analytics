<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-23T18:12:39Z — Viabilidad ALTA y baja: el patrón de FR4 (Q1=A) extiende `SofascoreIPBanError` (excepción tipada propagada, ya probado en FR2.1) a Futmondo (hoy `return None` silencioso); el estado (Q2=A) reusa `sync_step_status.StepStatus.DEGRADED` de FR3.1, fuera de los god-files [M1]. Sin dependencias nuevas (stdlib), coste 0 € [M2]. Sin compliance formal (Q3=A). Incertidumbres a diseño (Q7=C): clasificar cada except recuperable/fatal y fijar el punto de corte 'no corromper datos' en la ruta de sync. Riesgos RAID (Q6=C): regresión al endurecer capturas (mitiga characterization-first + gate CI) y baneo real en pruebas (mitiga dobles/mocks sin red).
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
