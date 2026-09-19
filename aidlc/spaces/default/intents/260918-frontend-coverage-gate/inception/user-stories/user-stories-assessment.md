# User Stories — Evaluación de aplicabilidad

Intent: `260918-frontend-coverage-gate` (scope `classic`, brownfield).

## Decisión

**Skip** — las historias de usuario no aportan valor para este intent.

## Rationale

Este intent es una intervención de **infraestructura de tests y de pipeline (developer tooling)**, no una funcionalidad de cara al usuario. Su alcance es:

- FR10.1 — retirar `skipTests: true` de los schematics de lógica en `angular.json` (configuración de tooling).
- FR10.2 — añadir el proveedor de cobertura `@vitest/coverage-v8` y declarar cobertura/umbrales por métrica en el target `test` de `angular.json`; sembrar specs de la capa `core/` crítica (configuración de tooling + tests).
- FR17.1 — cablear el umbral de `ng test` para que bloquee en `ci.yml` y en el job `verify` de `fly-deploy.yml` (configuración de pipeline CI/CD).

La `condition` de esta etapa indica explícitamente **Skip** para "pure refactoring, isolated bug fixes, infrastructure-only changes, or **developer tooling**". Este intent cae de lleno en esa categoría:

- **Sin comportamiento de dominio nuevo**: `business-overview.md` lo confirma — el intent "NO añade comportamiento de dominio nuevo; es una intervención de calidad e ingeniería de entrega". No se tocan componentes ni servicios de negocio (NFR2 de `requirements.md`).
- **Sin personas nuevas ni actores de cara al usuario**: los "actores" de este trabajo son los **desarrolladores** (que escriben código nuevo que nace con spec) y el **pipeline de CI/CD** (que impone el umbral). No hay un usuario final que ejecute un flujo nuevo; las pantallas Angular existentes (`market`, `finances`, `budget`, etc.) no cambian su comportamiento.
- **Lógica de negocio no compleja para el usuario**: la complejidad del intent es de configuración de tooling (denominador de cobertura, umbral por métrica, ratcheting, cableado del gate), ya capturada de forma testable y trazable en `requirements.md` (FR10.1, FR10.2 + sub-reqs, FR17.1) y en las prácticas afirmadas (`team-practices.md`).

## Factores considerados

- **Tipo de proyecto**: brownfield; intervención acotada y aditiva sobre configuración/specs/workflows.
- **Alcance de cara al usuario**: nulo — no hay pantallas nuevas ni cambios de UX; el frontend afectado es la **configuración de test** de la app, no su interfaz.
- **Señales de complejidad**: la complejidad es de infraestructura de calidad (denominador estable, umbral por métrica, propagación del gate a dos workflows), no de flujos de usuario.
- **Coordinación cross-team**: no aplica; single-repo, un equipo.

## Cobertura alternativa

Los requisitos por sí solos son suficientes y ya están completos y trazables:

- `requirements.md` captura el trabajo como FR10.1, FR10.2 (con sub-requisitos FR10.2.1–3), FR10.3 (P0 duro + P1/P2 guía) y FR17.1 (con FR17.1.1/17.1.2), cada uno con criterios de aceptación Given/When/Then verificables.
- La trazabilidad se mantiene a nivel de requisito (FR10.1 / FR10.2 / FR17.1) hacia el plan de mejoras origen (`260911-analisis-mejoras`) y el estado base verificado (`docs/BACKLOG-cobertura-frontend-y-pipeline.md`, `code-quality-assessment.md`).
- Las decisiones de diseño (denominador `coverage.all`, umbral por métrica, ratcheting manual, cableado en ambos workflows, política de `skipTests`) están afirmadas en `team-practices.md`.
- La verificación del intent es objetiva (el gate de CI mide y bloquea por cobertura), no depende de criterios de aceptación centrados en un actor humano.

Introducir personas y historias "As a [persona], I want..." forzaría un encuadre artificial (p. ej. "As a developer, I want new files to be born with a spec") que no añade información sobre la ya capturada en los requisitos y sus criterios de aceptación. Se difiere el modelado de historias porque no hay valor de usuario que estructurar.
