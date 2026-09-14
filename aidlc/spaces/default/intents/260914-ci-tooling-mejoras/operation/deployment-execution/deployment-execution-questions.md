# Preguntas — Deployment Execution (Mejoras de CI/Tooling)

> Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Depth Minimal · Brownfield.
> El despliegue de estas mejoras se produce vía merge a `main` → `fly-deploy.yml` (GitHub Actions). No hay `fly deploy` manual desde esta sesión.

## Q1 — Vía de despliegue de las mejoras

Las 5 mejoras son cambios de CI/tooling que se integran a `main`. ¿Cómo se ejecuta el despliegue?

- A. Vía el pipeline existente: merge/push a `main` dispara `fly-deploy.yml` (verify → deploy backend → deploy frontend → smoke test `/health`). Esta etapa documenta el plan y el estado de verificación; el disparo real (commit + push/merge) lo realiza el humano. (recomendado)
- B. Ejecutar `fly deploy` manualmente ahora desde esta sesión.
- C. No desplegar (dejar los cambios sin integrar).
- X. Other (please specify)

[Answer]: A

## Q2 — Migraciones de base de datos

¿Requieren estas mejoras migraciones de base de datos?

- A. No — son cambios de CI/tooling/dependencias/entorno; no tocan esquema ni datos (Neon PostgreSQL intacto). (recomendado)
- B. Sí (especificar).
- X. Other (please specify)

[Answer]: A

## Q3 — Verificación pre-despliegue

¿Qué verificaciones pre-despliegue confirmamos antes de integrar a `main`?

- A. Tests del frontend en verde (6/6 con Vitest, verificado en contenedor node:22.22.3) + `npm ci` limpio (lock revisado); el gate de CI y el smoke test `/health` confirman en el pipeline. El fallo de build por presupuesto de bundle es preexistente y ajeno al intent. (recomendado)
- B. Además, ejecutar el build de producción localmente hasta que pase (implica abordar el presupuesto de bundle, fuera de alcance).
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Resumen de decisiones:
- Q1: A — Despliegue vía el pipeline existente (merge/push a `main` → `fly-deploy.yml`); esta etapa documenta el plan y el estado de verificación; el disparo real lo realiza el humano.
- Q2: A — Sin migraciones de base de datos (no se toca esquema ni datos).
- Q3: A — Verificación pre-despliegue: tests 6/6 verdes con Vitest + `npm ci` limpio; CI y smoke test `/health` confirman en el pipeline; el fallo de build por presupuesto de bundle es preexistente y fuera de alcance.

Se generarán: `deployment-log.md`, `smoke-test-results.md`, `health-check-report.md`. No se ejecuta `fly deploy` ni push a `main` desde esta sesión.

- Looks correct
- Request changes

[Answer]: Looks correct
