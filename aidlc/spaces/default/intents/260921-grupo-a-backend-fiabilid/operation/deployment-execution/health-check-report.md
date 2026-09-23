# Informe de health check — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. Health checks ya operativos en
> producción; se documentan y se valida que el intent no los degrada. El deploy
> real ocurre on-merge. Coste 0 €.

## Health checks definidos

| App | Check | Criterio |
|---|---|---|
| `futmondo-api` (backend) | `GET /health` (puerto 8000) | HTTP 200 `{"status":"healthy"}` |
| `futmondo-app` (frontend) | `GET /` (nginx, puerto 80) | HTTP 200 |

- Fly.io usa estos checks para el enrutado y el estado de las máquinas; el job
  `smoke-test` reutiliza `/health` como verificación de release.

## Impacto del intent en la salud del servicio

- **Neutro/positivo**. El intent es backend-only y aditivo; no cambia el
  contrato de `/health` ni añade dependencias de arranque.
- **Mejora de fiabilidad observable**: con el estado `degraded`, un paso
  non-critical de la sync (`prizes`/`phantoms`) que falla ya no se reporta como
  `done`; el `progress[step].status` refleja el fallo con un log estructurado
  (`record_degraded_step`). La Tarea global puede completar aunque un paso quede
  degradado (BR3/NFR1), sin afectar a la disponibilidad del servicio.
- **Endurecimiento sin regresión**: el techo de `price` (422) y los `except`
  acotados no cambian rutas de arranque; `import app.main` y la suite (166)
  confirman que la app levanta correctamente.

## Estado

- **Pendiente de merge**: la validación de health en producción se confirmará
  con el `smoke-test` de la CD al fusionar. No se dispara manualmente aquí.

## Observabilidad disponible (coste 0 €)

- `fly logs` (logs estructurados, incl. el `logger.warning` de pasos degradados),
  healthcheck `/health`, historial de releases Fly.io.
- **NO-APLICA/diferido** (servicios de pago): métricas con dashboards, SLOs con
  burn-rate, tracing distribuido, anomaly detection ML.

## Sources

- `.github/workflows/fly-deploy.yml`, `operation/environment-provisioning/{environment-inventory,validation-report}.md`,
  `construction/sync-reliability/functional-design/functional-spec.md` (FS1/FS2),
  `construction/build-and-test/test-results.md`.

## Assumptions & Open Questions

None.
