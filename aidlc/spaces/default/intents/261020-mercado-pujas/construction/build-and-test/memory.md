<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-10-21 — Build verde (exit 0) y suite 153/153 verde (40 nuevos de Mercado). Dos objetivos Unverified por limitaciones de toolchain WSL afirmadas como durables: cobertura numérica llvm-cov no fiable y validación de vistas SwiftUI en dispositivo (`xtool dev build` no compila en WSL por desajuste compilador/SDK). Sin fix identificable en dimensión swappable → halt-and-ask variante no-fix; el humano eligió **Accept failure**. Registrado en test-results.md; la validación de UI/cobertura queda como trabajo de dispositivo documentado, no como umbral relajado.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
