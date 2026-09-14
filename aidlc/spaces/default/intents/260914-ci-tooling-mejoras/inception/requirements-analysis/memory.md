<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-14T11:01:00Z — Fuente de requisitos muy clara; el backlog docs/BACKLOG-mejoras-ci-tooling.md define QUÉ/POR QUÉ de las 5 mejoras y el codekb confirma el estado actual (builder @angular/build:unit-test, karma.conf.js huérfano, workflows ci.yml/fly-deploy.yml, coste 0€). Profundidad Minimal (scope refactor): pocas preguntas, centradas en decisiones abiertas que no se pueden inferir con seguridad (criterio de "actualizado" de las actions, alcance de la migración animaciones, definición de done de Karma→Vitest, si Node local entra en requisitos formales).
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-14T11:17:00Z — Tras el gate, el humano eligió Request Changes para incorporar los 4 hallazgos advisory del product lead: R-01 (FR3.4 re-anclado a evidencia, no afirma un aviso no confirmado), R-02 (FR2.3 fija umbral pass/fail de la rama "documentada"), R-03 (corregido tag de fuente malformado [Q2-backlog]->[desc] en FR2.1), R-04 (FR4.5 eleva la línea base de no-regresión a paso verificable; A3 actualizada en consecuencia).
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
