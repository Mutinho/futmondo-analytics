<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-11T13:28:00Z — En intent de análisis, domain-design NO crea componentes: el catálogo refleja la arquitectura actual (10 componentes del codekb, con CICD añadido como transversal) y se anota por componente qué FRs le afectan (campo no estándar improvements + tabla "Mapa de mejoras"). Sirve de mapa "dónde toca cada mejora".
- 2026-09-11T13:28:00Z — traceability.json mapea los 18 FRs a su componente (fallback FR, no hay stories); FR transversales (FR11/FR12/FR17) → CICD, marcado N/A en reverse por no tener runtime de aplicación.
- 2026-09-11T13:28:00Z — 6 ADRs: 5 estructurales (FR1 persistir sync, FR2 caché transaccional, FR5 credenciales, FR14 consolidar BD Neon, FR13 god files incremental) + ADR-006 enfoque global conservador (Accepted). Todas descartan alternativas con coste recurrente por la regla coste 0€.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-11T13:34:00Z — Backward jump solicitado por el usuario tras aprobar (cambió de opinión): corregidos R-01 (4 aristas depends_on/dependents asimétricas: ApiEndpoints↔IntegrationClients, Cron→DataServices, Proxy→Backend; retirada la arista incorrecta Backend→Cron porque Cron no llama al Backend en runtime), R-03 (nota de backend/scripts consolidado en DataServices) y R-04 (asistente IA Gemini/Groq como external_dependency de DataServices). Tablas derivadas actualizadas para reflejar la simetría.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
