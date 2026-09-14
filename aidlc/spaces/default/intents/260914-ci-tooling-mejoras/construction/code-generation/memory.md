<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-14T12:38:00Z — Spec `auth.interceptor.spec.ts` reescrito de Jasmine a Vitest; la migración Karma→Vitest obliga a retirar `jasmine-core`/`@types/jasmine`, y el único spec usaba `jasmine.createSpyObj`/`.and.returnValue`. Se reescribió a `vi.fn()`/`mockReturnValue`/`mockResolvedValue` conservando idénticas aserciones (no regresión, BR4.3).
- 2026-09-14T12:39:00Z — `ng test` no ejecutable en el entorno local: Angular CLI 22 exige Node >=22.22.3 y el entorno tiene 22.22.1. Verificación delegada a CI (Node 22 compatible) y a Build and Test; a nivel local se revisó el lock regenerado (npm 11.12.1: 0 Karma, Vitest presente, 0 vulnerabilidades), cumpliendo la regla de proyecto ("verificar npm ci/ng test en local O revisar el lock").
- 2026-09-14T12:39:30Z — Mejora 2 (punycode DEP0040) resuelta como consecuencia de la mejora 4: la cadena `dom-serialize → ent → punycode@1.4.1` colgaba del stack de Karma (dev). Tras retirar Karma, el lock ya no contiene `punycode`. Nota de vigilancia registrada en el CodeKB dependencies.md.
- 2026-09-14T12:40:00Z — `vitest` fijado a `^4.0.8` (no 3.x) por el peer de `@angular/build@22.1.2`. Coste 0€ (tier gratuito).
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
