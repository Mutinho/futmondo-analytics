# Log de ejecución del despliegue — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. **Encuadre**: el despliegue es
> **on-merge a `main`** (automático, `fly-deploy.yml`). Este intent es trabajo
> en curso **aún no fusionado**: este log documenta el PLAN de ejecución y su
> estado, no un deploy manual disparado desde esta etapa. Coste 0 €.

## Estado del despliegue

- **Estado**: PLANIFICADO / pendiente de merge a `main`.
- **Disparador**: la fusión del MR de este intent a `main` (branch protection +
  gate `verify` verde). No se ejecuta `flyctl deploy` manual desde el workflow
  AI-DLC (respeta la política on-merge del equipo).

## Secuencia que ejecutará la CD al fusionar

| Paso | Job | Acción | Verificación |
|---|---|---|---|
| 1 | `verify` | gitleaks + `pytest tests` + `ng test` | bloqueante (un rojo no despliega) |
| 2 | `deploy-backend` | `flyctl deploy` en `./backend` → `futmondo-api` | — |
| 3 | `deploy-frontend` | `flyctl deploy` en `./angular-app` → `futmondo-app` | — |
| 4 | `smoke-test` | `curl` a `/health` (5 reintentos) | HTTP 200 = release OK |

## Artefactos desplegados por este intent

- Backend `futmondo-api`: código nuevo de fiabilidad (helper `record_degraded_step`,
  cableado `degraded` en `sync.py`, techo `PRICE_SANITY_CAP` en `market.py`,
  `except` acotados en `token_store.py`/`db_connection.py`).
- Frontend `futmondo-app`: **sin cambios** (intent backend-only); su deploy corre
  igualmente en la cadena pero no aporta cambios de este intent.

## Migraciones de BD

- **Ninguna.** Cambio aditivo sin migración (estado `degraded` en `progress`,
  JSON libre). No hay paso de migración que ejecutar ni delegar.

## Pre-deployment checks

- Suite completa en verde (166 tests; `construction/build-and-test/test-results.md`).
- Servicios dependientes sanos (Neon TLS; `/health` 200 en producción).

## Rollback

- Documentado en `operation/deployment-pipeline/rollback-runbook.md`: redeploy
  manual de la release previa con `flyctl`; sin reversión de datos (sin
  migración). El estado en memoria se pierde en el redeploy (limitación aceptada).

## Sources

- `operation/deployment-pipeline/{cd-config,deployment-strategy,rollback-runbook}.md`,
  `operation/environment-provisioning/environment-inventory.md`,
  `construction/build-and-test/test-results.md`, `.github/workflows/fly-deploy.yml`.

## Assumptions & Open Questions

None.
