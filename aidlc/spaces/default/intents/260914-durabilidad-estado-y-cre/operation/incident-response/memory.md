<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-16T13:56:00Z — Ejecuto (contenido genuino): la durabilidad introduce modos de fallo nuevos con procedimientos claros a coste 0 €. Aplico el patrón aprendido en observability-setup: adaptar el conocimiento AWS (SSM Automation, Incident Manager, on-call) al stack real (Fly.io, un solo operador, coste 0 €). Runbooks reales: secret FUTMONDO_CRED_KEY ausente/rotado → re-fijar y forzar re-login; error de descifrado de sesión → rotar clave; tareas huérfanas tras redeploy → ya se auto-marcan interrumpidas (FR1.5), no requieren intervención; backend caído → Fly auto-restart + `fly logs`; rollback → `docs/ROLLBACK.md`. Escalación: proyecto personal de un operador, sin rotación on-call formal (NO-APLICA); severidades simplificadas. RTO/RPO: sin compromiso formal; Neon (tier free) tiene su propia retención, BD es autoridad. Sin preguntas nuevas.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
