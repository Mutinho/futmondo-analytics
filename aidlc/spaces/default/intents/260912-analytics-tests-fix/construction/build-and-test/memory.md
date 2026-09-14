<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-14T09:54Z — Ejecución real de pytest (venv temporal, JWT_SECRET del CI): 53 passed, 1 FAILED. El arreglo aprobado (caches + latest_price) es correcto y resuelve los AttributeError/KeyError. PERO test_championship_trends revela una TERCERA causa, distinta y no incluida en el alcance del intent: get_championship_trends → _safe_team_info consulta la BD directamente (get_db/SELECT teams) en vez de usar self.dm.get_team_by_id; bajo el fixture (sin BD) el except Exception:pass deja _team_cache vacío y team_name cae al fallback team_id ("team-1" en vez de "Team One"). El AttributeError anterior enmascaraba este fallo. Fuera del alcance aprobado — requiere decisión humana (ampliar alcance vs recompose).
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
