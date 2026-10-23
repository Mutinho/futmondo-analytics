<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-18T12:58Z — Intent nacido del fast-follow registrado al cerrar F1 (`261016-f1-login-nativo/operation/feedback-optimization/feedback-loop.md`): sistema de diseño nativo que PRECEDE a F2. Problema (Q1=E): retrabajo + coherencia + velocidad + claro/oscuro+Dynamic Type. Beneficiario (Q2=C): usuario único y mantenedor a la vez (single-maintainer).
- 2026-10-18T12:58Z — Éxito (Q3=E): F2 se apoya sólo en el sistema; login F1 revestido sin cambios de comportamiento; claro/oscuro+Dynamic Type en todos los componentes (demostrable en catálogo/preview); coste 0 € sólo SDK de Apple.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-18T12:58Z — Boundary (Q8=E): se deja FUERA la tab bar nativa (B-08) y la aplicación del sistema a pantallas de F2, para no solapar con F2; sólo tokens + componentes base + revestir F1.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-18T12:58Z — [Q9] Diseño de referencia de Google Stitch en curso: el usuario aportará export (imágenes y, si se puede, código/CSS), "casi completo" pero NO garantizado. El sistema debe reproducirlo en SwiftUI y el material entra como input en las etapas de mockups (rough/refined); lo que falte se cubre con Apple HIG a coste 0 €. Pendiente: formato real del export y completitud, a confirmar al llegar a mockups.
