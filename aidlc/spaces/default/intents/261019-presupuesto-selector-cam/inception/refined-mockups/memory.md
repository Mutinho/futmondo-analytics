<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T15:48Z — Refined Mockups: recogidos TODOS los findings pendientes. Métricas visibles en lista = 4 (team_name, balance, performance, puja máxima, premios); team_value/gastado/ingresado/ops diferidos a detalle (decisión de densidad iPhone). Estado vacío añadido (teams[] vacío → estado vacío no-error; lista campeonatos vacía → mensaje + selector deshabilitado). Accesibilidad de carga/error explícita (VoiceOver + foco en Reintentar). Orden descendente-sólo con toggle diferido. NFR4/NFR5 anclados a accessibility-checklist verificable. design-system-mapping mapea cada elemento a tokens de F1 (consume, no rediseña).

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-19T15:48Z — La lista muestra 4 métricas (no las 9 de FR1.2) por densidad en iPhone; las 5 restantes van al detalle de equipo diferido. FR1.2 pide los 9 "disponibles" (no todos en la fila). A vigilar en domain/contract-design que los DTOs sí incluyan los 9 aunque la vista muestre 4.
- 2026-10-19T16:04Z — Tras review advisory READY con 1 finding Major: realineada AC1.1 en stories.md (cross-stage) para reflejar 4 visibles + 5 diferidas al detalle (resuelve la contradicción). Minor: añadido placeholder de alcance de la pantalla de detalle diferida en mockups.md; añadida nota en interaction-spec.md de que ordenar por clave no visible es intencional. Re-pase de reviewer iteración 2 por cambio en mockups.md.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
