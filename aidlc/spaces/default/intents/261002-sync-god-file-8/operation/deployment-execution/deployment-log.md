# Deployment Log — Sync Domain Decomposition (on-merge release path)

Scope `refactor`, fase Operation, última etapa. Coste 0 €. Documenta la **ruta de
despliegue y la readiness** del refactor de descomposición de dominios de sync.
El despliegue es **on-merge a `main`** vía `fly-deploy.yml`; **no se ejecuta un
`flyctl deploy` en vivo desde esta sesión** (Q1=A): el deploy real lo dispara el
merge del PR, gateado por `verify`.

## Fuentes

- `operation/deployment-pipeline/cd-config.md`, `deployment-strategy.md`,
  `rollback-runbook.md`
- `construction/build-and-test/test-results.md`, `build-and-test-summary.md`
- Workspace: `.github/workflows/fly-deploy.yml`, `backend/fly.toml` (target real;
  `environment-provisioning` saltada por alcance → inventario tomado del workspace)
- Adaptación de stack: `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`

## Target de despliegue (inventariado del workspace)

| App Fly.io | Rol | Puerto | Health check | Cambia en este intent |
|------------|-----|--------|--------------|------------------------|
| `futmondo-api` | backend FastAPI | 8000 | `/health` | Sí (código refactorizado; superficie pública idéntica) |
| `futmondo-app` | frontend nginx | 80 | `/` | No (backend-only refactor) |
| Neon PostgreSQL | BD (Frankfurt, free) | — | — | No (sin cambio de esquema) |

## Estado de ejecución

**Modo: documentado / readiness verificada (deploy NO ejecutado en vivo desde la
sesión).**

| Paso | Estado | Nota |
|------|--------|------|
| Build/readiness (gate `verify`) | **Listo (verde)** | Suite 329 passed, cobertura 43.19% ≥ 27; `ruff check` OK; `data_manager_v2.py` sin cambios |
| Migración de BD | **No aplica** | Equivalencia estricta, sin cambio de esquema (Q2=A) |
| `deploy-backend` (`flyctl deploy ./backend`) | **Pendiente de merge** | Lo ejecuta el pipeline al fusionar a `main` |
| `deploy-frontend` (`flyctl deploy ./angular-app`) | **Pendiente de merge** | Sin cambios de frontend; se redeploya por la cadena `needs:` |
| `smoke-test` (`/health`) | **Pendiente de merge** | 5 reintentos, HTTP 200; ver `smoke-test-results.md` |

## Ruta de release (on-merge)

1. Abrir PR del refactor contra `main`. El gate de PR (`ci.yml`) debe pasar.
2. Al fusionar (squash) a `main`, `fly-deploy.yml` corre:
   `verify → deploy-backend → deploy-frontend → smoke-test`.
3. `verify` re-ejecuta el gate (gitleaks + pip-audit + ruff + pytest con piso +
   npm audit + ng test). Un rojo detiene los deploy (`needs:`).
4. Fly despliega backend y frontend; el smoke test `/health` verifica el release.
5. Si el smoke test queda en rojo → rollback manual (`rollback-runbook.md`).

## Verificación post-deploy (cuando ocurra el merge)

- `smoke-test` job: `curl` a `https://futmondo-api.fly.dev/health` → HTTP 200.
- Comprobación manual opcional: lanzar un sync (`/api/v1/sync/trigger`) y
  confirmar en `fly logs` que los 10 pasos producen el mismo `SyncResult`
  observable (equivalencia). Diagnóstico vía `fly logs` + `fly status` (coste 0 €).

## Rollback

Manual, documentado en `rollback-runbook.md` (`fly releases rollback`). Alcance
backend-only; sin rollback de datos (no hubo migración).
