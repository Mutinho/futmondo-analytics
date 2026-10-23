<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-18T13:48Z — Alcance (Q1=A, Q2=B): must-have = tokens (color claro/oscuro del tema Angular, Roboto+Dynamic Type, espaciado), componentes base (botón, campo, tarjeta, estados carga/error), catálogo/preview y revestir F1; nice = variantes extra. Dependencias (Q3=A): tokens→componentes→catálogo; revestir F1 depende de tokens+componentes.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-18T13:48Z — Secuenciación risk-first (Q4=B): un spike de tokens + 1 componente validado en claro/oscuro contra el frontend Angular retira pronto el riesgo dominante de fidelidad, respetando a la vez el orden de dependencias. Sin plazo (Q5=A).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-18T13:48Z — Boundary confirmado (Q6=A): fuera tab bar nativa (B-08→F2), aplicación a pantallas de F2, animaciones avanzadas, temas más allá de claro/oscuro y dependencias de pago. Referencia de diseño = tema de Angular (`angular-app/src/styles.scss`), Stitch descartado.
