# Infrastructure Specification — u2-integrations (Integraciones)

Este intent **no cambia la infraestructura**. Los patrones de fiabilidad de U2
viven en el código (excepciones tipadas, timeout, transacción atómica), no en la
infra. Se documenta la topología existente como "sin cambio" y se adapta a
Fly.io + Neon (coste 0 €); los recursos AWS del conocimiento se marcan NO-APLICA.

Consume: `nfr-design/*`, `logical-components.md`, `components.md`, `functional-spec.md`,
`contract-summary.md`. Perspectivas inline: plataforma (Fly.io) + DevSecOps + Compliance.

## Deployment

| Facet | Choice | Rationale |
|---|---|---|
| Compute model | Contenedores en Fly.io (dos apps) — **sin cambio** | `futmondo-api` (Python/FastAPI, puerto 8000) y `futmondo-app` (nginx, puerto 80); U2 sólo toca código backend |
| Networking topology | Ingress HTTPS gestionado por Fly.io; egress a Futmondo/Sofascore (HTTPS) y Neon (TLS) — **sin cambio** | Fly.io gestiona red/routing; no hay VPC/subnets que diseñar (NO-APLICA AWS) |
| Storage strategy | Neon PostgreSQL (Frankfurt, tier free); fallback SQLite/Turso — **sin cambio** | U2 no cambia el esquema ni el volumen; sólo endurece el manejo de fallo del punto `team_prizes` |
| Environments | Un entorno productivo (sin staging separado) — **sin cambio** | Smoke test `/health` es la verificación de release (coste 0 €) |
| IaC approach | `fly.toml` versionado + `Dockerfile`/`nixpacks.toml` (backend), nginx (frontend) — **sin cambio** | Drift detectable por diff de git; sin CDK/Terraform (NO-APLICA AWS) |
| Resource sizing | `min=max=1`, `shared-cpu-1x` / 256 MB por app — **sin cambio** | Escala fija por diseño; coste 0 € (Fly free allowance) |
| Crons | `daily-sync.yml` (04:30 UTC), `sofascore-sync.yml` (05:00 UTC), máquinas Fly one-shot — **sin cambio** | Ejercitan las rutas de sync que U2 endurece; sin estado entre ejecuciones |

## Infrastructure Services

| Service | Role | Configuration | Notes |
|---|---|---|---|
| Neon PostgreSQL | database | Frankfurt, tier free; pool `ThreadedConnectionPool` 5–20, retry x3 en `db_connection` | **Sin cambio**; la transacción atómica de `team_prizes` usa el pool existente |
| Fly.io (backend app) | compute / load-balancer | `futmondo-api`, check `/health`, TLS gestionado | **Sin cambio** |
| Fly.io (frontend app) | compute / cdn-edge | `futmondo-app` nginx, check `/` | **Sin cambio**; fuera del área de U2 |
| GitHub Actions | ci/cd | `ci.yml` (PR→main), `fly-deploy.yml` (push→main), crons | **Sin cambio** salvo el commit aislado de `E722` (ver `cicd-pipeline.md`) |

## Shared Infrastructure

No aplica: U2 y U1 comparten el mismo despliegue `futmondo-api` (organización del
trabajo, no despliegue independiente); no hay recurso de infraestructura nuevo
compartido que provisionar. La frontera U1↔U2 es un contrato de **código**
(jerarquía `IntegrationError`), no de infraestructura.

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- VPC / subnets / security groups / NACL / NAT gateway → NO-APLICA (Fly.io
  gestiona la red). Documentado, no inventado.
- KMS / Secrets Manager / IAM → NO-APLICA; secretos vía `fly secrets` / GitHub
  secrets (ver `security-design.md`).
- Multi-AZ / auto-scaling / ElastiCache / colas gestionadas → NO-APLICA
  (topología fija `min=max=1`, coste 0 €, sin necesidad en el alcance de U2).
- CDK / CloudFormation / Terraform → NO-APLICA; IaC = `fly.toml` + Dockerfile
  versionados.

## Assumptions & Open Questions

None.
