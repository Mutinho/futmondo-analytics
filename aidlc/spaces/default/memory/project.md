# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Change Control

<!-- Project-specific. Mode: strict or relaxed. Strict here holds for every intent and cannot be changed from chat. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11) <!-- cid:260911-analisis-mejoras:intent-capture:a64ea58ac71fc6e7985eddb4c78948ff11827c7ed40537a25c6fac73a6bb3c81 -->
- ALWAYS verificar npm ci y ng test en local (o revisar el lock) antes de pushear tras cambiar devDependencies del frontend, para no romper el gate de CI (learned 2026-09-14) <!-- cid:260912-analytics-tests-fix:deployment-execution:0ea68257a2ff0bccf48656b5ace52be1efaf362d3166078342c2a0491ce27727 -->
- ALWAYS verificar el build/tests del frontend en un contenedor `node:<versión de .nvmrc>` (con volumen anónimo para `node_modules`) cuando el Node local no alcance el mínimo que exige el Angular CLI; coste 0€ (learned 2026-09-14) <!-- cid:260914-ci-tooling-mejoras:deployment-execution:4a9616552729869fa85366642edb5f7079643479f82a6cf5c5d3baeb8674792c -->
