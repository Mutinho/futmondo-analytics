<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-16T13:48:00Z — El despliegue de este proyecto es AUTOMÁTICO on-merge a `main` (fly-deploy.yml); el código de durabilidad aún no está fusionado y desplegar a producción es acción de alto impacto que NO se dispara desde esta sesión (ni `fly deploy` manual, ni fijar secretos productivos, ni desplegar fuera del flujo de merge del equipo). Enfoque: documentar el runbook/plan de ejecución (acción previa del secret FUTMONDO_CRED_KEY, orden verify→deploy-backend→deploy-frontend→smoke `/health`, criterios de verificación) como artefactos de esta etapa; el deploy efectivo lo realiza el pipeline al fusionar el MR. deployment-pipeline se saltó, así que cd-config/deployment-strategy ausentes son esperados: inventario el pipeline real del workspace (fly-deploy.yml) en su lugar. Sin preguntas nuevas: todo decidido/documentado.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
