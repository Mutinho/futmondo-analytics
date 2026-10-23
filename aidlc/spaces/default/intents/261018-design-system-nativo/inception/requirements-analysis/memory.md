<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-18T19:07Z — Requisitos acotados por la ideación aprobada. Tokens (Q1=A): roles semánticos clave del tema Angular en claro/oscuro. Tipografía (Q2=A): escala h1/h2/h3 + Dynamic Type, Roboto con fallback a fuente del sistema. Componentes (Q3=A): botón/campo/tarjeta/estados carga-error. Catálogo (Q7=A): evidencia con toggles claro/oscuro + tamaño de texto.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-18T19:07Z — Revestir F1 (Q4=A) y accesibilidad (Q5=A) con verificación MANUAL en iPhone 13 Pro; sin arnés de test de UI nativo (diferido, coherente con practices Q1=A). Fuente/Roboto: fallback a fuente del sistema permitido para no empaquetar dependencia.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-18T19:07Z — Mapeo exacto de valores hex del tema Angular → color sets SwiftUI (claro/oscuro) a concretar en functional-design/code-generation.
