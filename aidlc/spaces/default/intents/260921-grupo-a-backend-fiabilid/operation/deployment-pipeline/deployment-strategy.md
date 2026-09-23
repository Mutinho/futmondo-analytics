# Estrategia de despliegue — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. Estrategia ya vigente; se
> documenta. Coste 0 €.

## Estrategia: redeploy on-merge con smoke test de release

- **Modelo**: cada merge a `main` que pasa el gate `verify` dispara
  `flyctl deploy`, que sustituye la imagen anterior por la nueva. No hay
  blue/green ni canary: entorno único de producción en Fly.io (restricción de
  coste 0 €).
- **Criterio de éxito del release**: el job `smoke-test` consulta `/health`
  hasta 5 veces (con esperas de 10 s); HTTP 200 = release sano. No hay staging
  separado, así que el smoke test ES la verificación de release (NFR2.2).
- **Orden**: `verify` → `deploy-backend` → `deploy-frontend` → `smoke-test`.
  El backend se despliega antes que el frontend (el frontend proxya al backend).

## Gates y condiciones de aborto

- **Gate previo**: `verify` (gitleaks + pytest + ng test, bloqueantes). Si falla,
  ningún deploy corre (dependencia `needs:`).
- **Condición de aborto / señal de fallo**: el smoke test en rojo (`/health` no
  devuelve 200 tras 5 intentos) marca el workflow como fallido y es el disparador
  del rollback (ver `rollback-runbook.md`).
- **Promoción entre entornos**: no aplica (un único entorno). El "gate de
  promoción" es el propio `verify` + smoke test.

## Aprobación a producción

- Automática on-merge: branch protection (required status check en `main`) +
  gate `verify` verde. Sin aprobación manual adicional (el equipo ha invertido
  en cobertura de tests y healthcheck; deploy continuo a prod es decisión de
  equipo, alineada con la política afirmada).

## Feature flags

- No aplican a este intent (intervención de fiabilidad backend acotada). Sin
  servicio de flags (coste 0 €).

## Impacto de este intent

- **La estrategia y el orden de despliegue no cambian.** El intent solo endurece
  la señal de calidad previa al deploy (ya cableada en `verify`). El nuevo código
  de fiabilidad viaja en el `deploy-backend` habitual.

## Sources

- `.github/workflows/fly-deploy.yml`, `cd-config.md`,
  `construction/ci-pipeline/quality-gates.md`, `team.md` (Deployment),
  `docs/ROLLBACK.md`.

## Assumptions & Open Questions

None.
