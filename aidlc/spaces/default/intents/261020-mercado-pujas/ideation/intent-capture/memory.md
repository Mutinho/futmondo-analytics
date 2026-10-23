<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-21 — Fuente de verdad del comportamiento = vista Angular `features/market/` (component.ts/html, bid-dialog, confirm-dialog, sofascore-detail). F3 reproduce sólo cards (no tabla), igual que F2. Orden siempre descendente por campo numérico (mismo patrón F2).
- 2026-10-21 — Rasgo nuevo frente a F1/F2: Mercado incluye ESCRITURA (pujar/cancelar) con efecto real en el campeonato compartido. Se eleva a la decisión de alcance Q1 por sus implicaciones de seguridad/riesgo; recomendación = incluirla (A), usando la sesión autenticada de F1 (Keychain, sin credenciales nuevas).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-20 — Propietario acepta las opciones recomendadas (Q1=A escritura completa, Q2=A card 1:1, Q3=A detalle Sofascore como sheet, Q4=A TabView 2 pestañas). intent-statement.md actualizado: escritura confirmada en alcance; assumptions resueltas.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-20 — Reviewer advisory (aidlc-product-lead-agent, 1 iter) sobre intent-statement: veredicto READY, 0 Major, 4 Minor. Aplicados: (1) tope de importe nombrado como "disponible para pujas"; (2) resultado de escritura distingue puja aceptada vs rechazada por backend además de error de red; (3) sección Assumptions marcada como "sin preguntas abiertas / supuestos confirmados"; (4) alineada la nota de Sofascore en stakeholder-map (ya dentro de alcance, Q3=A).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
