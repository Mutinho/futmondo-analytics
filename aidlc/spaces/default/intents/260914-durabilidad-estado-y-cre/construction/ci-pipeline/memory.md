<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-16T13:34:00Z — Skip justificado de ci-pipeline (stage CONDITIONAL: "Skip if CI already exists and is adequate"). El CI del repo es maduro y ya cubre la durabilidad sin cambios: `.github/workflows/ci.yml` (gate de MR: gitleaks BLOQUEANTE, `pytest --cov` BLOQUEANTE ejecutando los 125 tests incluidos los nuevos de durabilidad, `ng test` BLOQUEANTE, ruff/ESLint/audits advisory, `JWT_SECRET` efímero presente) y `.github/workflows/fly-deploy.yml` (push→main: job `verify` con gitleaks BLOQUEANTE + pytest + ng test, deploy backend→frontend→smoke `/health`). La durabilidad no introdujo componentes/lenguajes/herramientas/comandos de build nuevos ni endpoints nuevos: los tests nuevos corren con el `pytest tests` existente. Único delta pendiente (no bloqueante): `verify` corre pytest sin `--cov` — es referencia informativa (Q3, sin piso bloqueante), no un gate debilitado; queda como nota conocida del equipo. No se requiere creación ni modificación significativa del pipeline.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
