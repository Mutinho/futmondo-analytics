<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-16T11:25:00Z — El developer creó un `backend/unit-test-instructions.md` duplicado en la raíz del backend; lo eliminé para no dejar dos fuentes de verdad, ya que las instrucciones de test aprobadas y autoritativas viven en el record dir (`.../code-generation/unit-test-instructions.md`). Sin impacto en la ejecución; no se lista en source-manifest.json (ya no es una escritura persistente).
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
- 2026-09-16T12:15:00Z — Un `ruff format` masivo para estabilizar el binding de revisión reformateó archivos brownfield tracked (main.py, routes.py, _helpers.py...) más allá del cambio de la unidad, inflando diffs y exponiendo un F841 preexistente. Se revirtió: restaurar tracked a HEAD y re-aplicar SOLO el cambio funcional; los archivos NUEVOS de la unidad quedan formateados/estables. Lección: no correr `ruff format` masivo sobre archivos brownfield modificados; estabilizar solo los archivos nuevos o formatear quirúrgicamente. La reviewer solo corre `ruff check` (no format), así que el binding de bytes de la fuente reclamada se mantiene estable durante su pasada si los archivos nuevos ya están formateados.
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
- 2026-09-16T12:32:00Z — u2 R-01 (Major, no bloqueante, READY): la unicidad 409 en /trigger usa SELECT (get_active_or_conflict) + INSERT no atómicos, sin restricción de BD (índice único parcial sobre estados activos / FOR UPDATE) que impida dos tareas activas por championship_id bajo concurrencia o multi-instancia. Estrecho hoy (fly.toml min=max=1) pero real frente a NFR5. A cerrar en Build and Test o un follow-up: índice único parcial / ON CONFLICT, o documentar diferimiento con owner. u2 R-03 (Minor): update_progress hace read-modify-write sin lock (seguro con un worker-thread por task_id; suposición a documentar).
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
