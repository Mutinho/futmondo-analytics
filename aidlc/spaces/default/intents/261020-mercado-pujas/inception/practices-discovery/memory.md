<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — Descubrimiento de CONFIRMACIÓN (delegado a pipeline-deploy-agent, subagent): las prácticas vigentes de team.md/project.md/org.md aplican íntegramente a F3. NINGUNA regla nueva a proponer. La novedad de F3 (escritura pujar/cancelar + 2º endpoint Sofascore) REFUERZA las reglas de seguridad ya afirmadas (Bearer, refresh token en Keychain, errores tipados sin credenciales), no las cambia. 4 artefactos escritos; discovered-rules lista todo como [YA-AFIRMADA].

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
