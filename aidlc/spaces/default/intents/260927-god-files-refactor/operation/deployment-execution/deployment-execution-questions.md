# Preguntas — Deployment Execution (Oleada 1: analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.
>
> El despliegue a producción es **deploy-on-merge**: lo ejecuta el push a `main` vía `.github/workflows/fly-deploy.yml`. El código de la extracción está hoy en el working tree **sin commitear** (rama `main`). Este stage documenta la verificación previa ya realizada y el plan de ejecución; **NO hace push a `main`** (regla de git safety: sin push directo a `main` sin permiso explícito).

## Q1 — Modelo de ejecución del despliegue

Dado que el deploy es on-merge a `main` (Fly.io), ¿este stage documenta la ejecución vía el pipeline existente (el merge dispara `verify → deploy → smoke`) sin que el asistente haga push directo?

- A. Sí — documentar la ejecución vía merge a `main`; el push/merge lo realiza el humano (o el flujo de PR). El asistente no hace push directo a `main`.
- B. No — otra vía de despliegue.
- X. Other (please specify)

[Answer]: A

## Q2 — Migraciones de BD

¿Requiere esta oleada migraciones de base de datos?

- A. No — la extracción de `analytics` no cambia el esquema (los 2 SELECT movidos son de solo lectura, mismo SQL). Sin migraciones.
- B. Sí — hay migraciones que ejecutar/testear.
- X. Other (please specify)

[Answer]: A

## Q3 — Verificación post-deploy

¿La verificación post-deploy es el smoke test `/health` del pipeline (HTTP 200, 5 reintentos)?

- A. Sí — el smoke test `/health` de `fly-deploy.yml` es la verificación post-deploy.
- B. No — verificación adicional.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
