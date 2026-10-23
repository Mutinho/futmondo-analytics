<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T09:31Z — Mapeo Material 3 → SwiftUI (Q1=A): hex representativos por rol (del SCSS + paletas Material verde/violeta) como Color Assets claro/oscuro. Materialización (Q2=A): Color Assets + enum `DesignTokens` para tipografía/espaciado. Interacción (Q3=A), accesibilidad WCAG AA móvil (Q4=A), iPhone vertical (Q5=A).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-19T09:31Z — Fidelidad vs. esfuerzo (Q1=A): se fijan hex representativos en vez de extraer en runtime cada `--mat-sys-*`; el ajuste fino se valida en el catálogo contra Angular. Evita levantar el frontend para una capa de diseño personal.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
None.
