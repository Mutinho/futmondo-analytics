# Health Check Report — calculadora-mejora

## Health checks del stack (Fly.io, sin cambios en este intent)

- **Backend** `futmondo-api`: check `/health` (puerto 8000). Sin cambios de
  backend en este intent.
- **Frontend** `futmondo-app`: check `/` (nginx). Publica el bundle con el toggle.
- **Observación** (coste 0 €): `fly status` + `fly logs` para verificar estado y
  errores tras el deploy (sustituye a dashboards gestionados; ver
  `knowledge/aidlc-shared/operation-fly-stack.md`).

## Validación post-deploy (pendiente del merge)

| Check | Esperado | Estado |
|-------|----------|--------|
| `smoke-test` `/health` (pipeline) | HTTP 200 (≤5 reintentos) | Pendiente (on-merge) |
| Frontend `/` responde (nginx) | HTTP 200, SPA carga | Pendiente (on-merge) |
| `/calculator` renderiza con el toggle | Toggle visible y funcional | Verificado en local; confirmar en prod |

## Impacto / riesgo

- Cambio frontend-only, de bajo riesgo; sin migraciones ni cambios de contrato.
  Rollback trivial por redeploy (ver `deployment-pipeline/rollback-runbook.md`).

## Sources

- `fly-deploy.yml`; `operation/deployment-pipeline/*`; `operation-fly-stack.md`.

## Assumptions & Open Questions

None.
