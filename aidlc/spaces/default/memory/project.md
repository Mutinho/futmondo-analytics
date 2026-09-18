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

- NUNCA correr `ruff format` masivo sobre archivos brownfield ya modificados: infla diffs con reflow ajeno, expone avisos preexistentes y (al cambiar bytes) invalida el pase de revisión en vuelo. Formatear SOLO los archivos nuevos de la unidad, o de forma quirúrgica; la reviewer solo corre `ruff check` (no `format`), así que el binding de la fuente reclamada se mantiene estable durante su pasada si los archivos nuevos ya están formateados. (learned 2026-09-16) <!-- cid:260914-durabilidad-estado-y-cre:code-generation:d7c0abb41ccada61c3f057facae6ffcf14f199480e188a8fca2562657840933c -->

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

- NEVER almacenar la contraseña Futmondo en claro: ni en memoria (deuda actual de (affirmed 2026-09-15)

`UserSession`, FR5) ni en la base de datos al diseñar la durabilidad. (El orden de (affirmed 2026-09-15)

preferencia entre re-autenticación y cifrado en reposo se decide en diseño, no aquí.) (affirmed 2026-09-15)

- NEVER usar un `JWT_SECRET` por defecto en producción; el arranque del servicio web (affirmed 2026-09-15)

exige un secreto no-default (NFR1.1; endurecido en `test_jwt_startup.py`). (affirmed 2026-09-15)

- NEVER almacenar la contraseña Futmondo en claro: ni en memoria ni en base de datos. (affirmed 2026-09-18)

- NEVER usar un `JWT_SECRET` por defecto en producción. (affirmed 2026-09-18)

- NEVER ampliar los god-files existentes (`data_sync_service.py` ~84 KB, (affirmed 2026-09-18)

`data_manager_v2.py` ~166 KB) ni el patrón SQL-en-router al tocar el cálculo de premios; (affirmed 2026-09-18)

el código nuevo va tras una capa/función estrecha testeable. (affirmed 2026-09-18)

- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados (infla diffs, (affirmed 2026-09-18)

expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear solo los (affirmed 2026-09-18)

archivos nuevos o de forma quirúrgica. (affirmed 2026-09-18)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS mantener el proyecto a coste 0 €: descartar toda mejora o dependencia con (affirmed 2026-09-15)

gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, (affirmed 2026-09-15)

Fly.io free allowance, GitHub Actions free). (ya afirmada en `project.md`) (affirmed 2026-09-15)

- ALWAYS pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de (affirmed 2026-09-15)

fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-15)

- ALWAYS caracterizar (congelar con tests) el comportamiento de `SessionStore` y (affirmed 2026-09-15)

`TaskManager` antes de refactorizarlos hacia durabilidad (characterization-first; (affirmed 2026-09-15)

hoy no tienen cobertura directa). (affirmed 2026-09-15)

- ALWAYS mantener el proyecto a **coste 0 €**: descartar toda mejora o dependencia con (affirmed 2026-09-18)

gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free (affirmed 2026-09-18)

allowance, GitHub Actions free). (affirmed 2026-09-18)

- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de (affirmed 2026-09-18)

fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-18)

- ALWAYS **caracterizar (congelar con tests) el comportamiento de `sync_prizes` en TODAS (affirmed 2026-09-18)

sus ramas antes de refactorizarlo** hacia la mejora del cálculo de premios (affirmed 2026-09-18)

(characterization-first, Q2=A): `points_prize`, gating `round_fully_played`, ranking (affirmed 2026-09-18)

flop/top, MVP, dream-team, jornada adelantada/negativa y el borrado defensivo (affirmed 2026-09-18)

`DELETE ... NOT IN`. Hoy la producción del premio tiene cobertura directa cero. Extiende a (affirmed 2026-09-18)

este intent el mandato ya afirmado de characterization-first para `SessionStore`/`TaskManager`. (affirmed 2026-09-18)

- ALWAYS exigir un `JWT_SECRET` **no-default** en el arranque del servicio web (NFR1.1; (affirmed 2026-09-18)

endurecido en `test_jwt_startup.py`). (affirmed 2026-09-18)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11) <!-- cid:260911-analisis-mejoras:intent-capture:a64ea58ac71fc6e7985eddb4c78948ff11827c7ed40537a25c6fac73a6bb3c81 -->
- ALWAYS verificar npm ci y ng test en local (o revisar el lock) antes de pushear tras cambiar devDependencies del frontend, para no romper el gate de CI (learned 2026-09-14) <!-- cid:260912-analytics-tests-fix:deployment-execution:0ea68257a2ff0bccf48656b5ace52be1efaf362d3166078342c2a0491ce27727 -->
- ALWAYS verificar el build/tests del frontend en un contenedor `node:<versión de .nvmrc>` (con volumen anónimo para `node_modules`) cuando el Node local no alcance el mínimo que exige el Angular CLI; coste 0€ (learned 2026-09-14) <!-- cid:260914-ci-tooling-mejoras:deployment-execution:4a9616552729869fa85366642edb5f7079643479f82a6cf5c5d3baeb8674792c -->
- Para reproducir la suite de pytest en local a coste 0 cuando el Python del sistema es más nuevo que el de CI, crear un venv efímero excluyendo `libsql-experimental` (no compila fuera de 3.12 y no lo ejercitan los tests, que usan el fake SQLite) y fijar un `JWT_SECRET` de arranque efímero. (learned 2026-09-16) <!-- cid:260914-durabilidad-estado-y-cre:build-and-test:f52ef2ddf207ebcfd3e714b2c51187edc37270edcd4e578e7a7026806759a479 -->
- En etapas de Operation cuyo conocimiento asume AWS/CloudWatch, adaptar al stack real (Fly.io + Neon) y al mandato de coste 0 €: generar artefactos con las herramientas gratuitas disponibles (`fly logs`, healthcheck, logging estructurado) y marcar explícitamente como NO-APLICA/diferido lo que exige servicios de pago (SLO formales con burn-rate, tracing distribuido, anomaly detection ML), documentando la alternativa gratuita en vez de inventar infraestructura inexistente. (learned 2026-09-16) <!-- cid:260914-durabilidad-estado-y-cre:observability-setup:f9a04574d004210fe9d1df0e23a826a072857aa96e41777667e6c0e7237d8e61 -->
