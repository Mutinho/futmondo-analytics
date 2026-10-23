<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-18T13:12Z — Veredicto GO: alta plausibilidad técnica. Capa autocontenida sobre SwiftUI (Q1=C), sin compliance (Q2=A), coste 0 € sin plazo (Q4=A), sin bloqueadores (Q5=A), sin AWS (Q6=NO-APLICA). SwiftUI cubre de sobra tokens + componentes base + claro/oscuro + Dynamic Type con SDK de Apple.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-18T13:12Z — Market Research saltada (intent interno 1 usuario, coste 0 €); feasibility consume sólo intent-statement. Preguntas de AWS/compliance adaptadas al stack real (Fly.io+Neon / iOS nativo xtool) y marcadas NO-APLICA, coherente con la corrección durable de adaptar etapas que asumen AWS.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-18T13:12Z — Fidelidad vs. coste 0 €: el export de Google Stitch puede no ser 1:1 con SwiftUI; se acepta cubrir lo que falte con Apple HIG en vez de pagar herramientas/dependencias (preserva coste 0 €).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-18T13:13Z — CAMBIO DE DECISIÓN (propietario): se descarta Google Stitch. La referencia de diseño pasa a ser el tema del frontend Angular existente (`angular-app/src/styles.scss`): Material 3 paleta verde (`mat.$green-palette`)/violeta, Roboto, claro/oscuro (`body.dark-theme`), tokens semánticos (`money-positive`/`money-negative`, `h1/h2/h3`, gradiente splash verde). Riesgo dominante reencuadrado a fidelidad de reproducción Material 3 → SwiftUI (no 1:1); lo que no tenga equivalente se cubre con Apple HIG a coste 0 €. Artefactos de feasibility e intent-statement actualizados en consecuencia. Mapeo exacto a concretar en mockups.
