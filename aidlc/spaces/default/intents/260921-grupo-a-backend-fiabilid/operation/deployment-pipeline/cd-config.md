# Configuración de CD — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. La CD **ya existe**
> (`.github/workflows/fly-deploy.yml`); esta etapa la documenta. Intent
> backend-only, aditivo: **no cambia la topología ni el orden de despliegue**.
> Todo en tiers gratuitos (coste 0 €).

## Disparo

- `push` a `main` (y `workflow_dispatch` manual). El deploy on-merge es la
  política del equipo; no hay staging separado.

## Cadena de jobs (`needs:`)

```
verify  →  deploy-backend  →  deploy-frontend  →  smoke-test
```

| Job | Qué hace | Bloquea el deploy |
|---|---|---|
| `verify` | gitleaks (`@v2`) + `pytest tests` + `ng test --watch=false` | Sí — los deploys dependen de él vía `needs:` |
| `deploy-backend` | `flyctl deploy` en `./backend` (app `futmondo-api`) | — |
| `deploy-frontend` | `flyctl deploy` en `./angular-app` (app `futmondo-app`) | — |
| `smoke-test` | `curl` a `/health` (5 reintentos, HTTP 200 = release OK) | Verificación de release |

- `needs:` NO cruza workflows, por eso `verify` replica el gate del PR
  (`ci.yml`) para el push directo a `main` (FR8.2: un rojo nunca llega a prod).
- Secretos: `FLY_API_TOKEN` vía `secrets` de GitHub Actions; nunca literales en
  el workflow.

## Topología de infraestructura (real)

- **Fly.io** región `cdg`: backend `futmondo-api` (puerto 8000, check `/health`)
  y frontend `futmondo-app` (nginx, puerto 80, check `/`).
- **Neon PostgreSQL** (Frankfurt, tier free).
- Crons de coste ~0 (`daily-sync.yml`, `sofascore-sync.yml`) con máquinas Fly
  one-shot; no afectan a este intent.

## Impacto de este intent

**Ninguno en la CD.** El código de `sync-reliability` se despliega con el mismo
`flyctl deploy` del backend; los tests nuevos ya se ejercen en `verify` antes de
desplegar. La topología y el orden (`verify → deploy-backend → deploy-frontend
→ smoke-test`) no cambian.

## Notas de infraestructura (Operation, coste 0 €)

Adaptación al stack real (no AWS/CloudWatch): la observabilidad y el rollback se
apoyan en las herramientas gratuitas de Fly.io (`fly logs`, `fly releases`,
healthcheck `/health`). SLOs formales con burn-rate, tracing distribuido y
anomaly detection ML quedan **NO-APLICA/diferidos** (exigen servicios de pago).

## Sources

- `.github/workflows/fly-deploy.yml`, `construction/ci-pipeline/ci-config.md`,
  `construction/ci-pipeline/quality-gates.md`, `README.md` (topología).

## Assumptions & Open Questions

None.
