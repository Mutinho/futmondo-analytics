<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-09-14T16:44Z — El intent agrupa FR1 (durabilidad de estado) y FR5 (credenciales en claro) porque ambos convergen en el mismo componente en memoria. Verificado en código: `backend/app/auth/session_store.py` (`UserSession` guarda `email`/`password` en claro; `SessionStore._sessions` es dict en memoria, singleton global) y `backend/app/services/task_manager.py` (`TaskManager._tasks` dict en memoria, singleton global, retiene solo las últimas 20 tareas). Un reinicio del proceso pierde ambos.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-09-14T16:50Z — Revisor advisory (product-lead) READY con 2 observaciones Minor no bloqueantes: (R-01) precisar en requirements cómo se verifica cada criterio de éxito cualitativo (mensaje re-login, mecanismo de no-persistencia de la contraseña); (R-02) etiquetar "suite existente en verde" como criterio de no-regresión, no como métrica de éxito de negocio. Trasladar a la etapa de requisitos.
