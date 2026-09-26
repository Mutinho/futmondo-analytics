# Environment Inventory — Intent 4 (gate CI/CD hardening)

> Fase Operation. Conocimiento de aprovisionamiento AWS **adaptado al stack real
> (Fly.io + Neon, coste 0 €)**. Este intent es **config-only**: no se aprovisiona
> ni cambia ningún entorno; se inventaría el entorno de producción existente y
> se marca NO-APLICA lo AWS-específico (regla afirmada, learned 2026-09-16).

## Alcance (Q1=A)

**Ningún aprovisionamiento nuevo.** El entorno de producción ya existe y no
cambia. La etapa inventaría lo existente y valida las expectativas del gate
endurecido sobre el entorno.

## Inventario del entorno de producción (existente, SIN cambios)

| Componente | Plataforma | Configuración | Healthcheck | Estado |
|------------|------------|---------------|-------------|--------|
| `futmondo-api` (backend FastAPI) | Fly.io, región `cdg` | puerto 8000 | `/health` (HTTP 200) | Existente, sin cambios |
| `futmondo-app` (frontend nginx/Angular) | Fly.io, región `cdg` | puerto 80 | `/` | Existente, sin cambios |
| Base de datos | Neon PostgreSQL | Frankfurt, tier free | conexión TLS | Existente, sin cambios |
| Crons de sync | Fly.io máquinas one-shot | `daily-sync.yml`, `sofascore-sync.yml` | — | Existentes, sin cambios |

## Inventario de secretos (por ubicación, sin exponer valores — Q2=A)

Perspectiva DevSecOps + Compliance: se referencian por **nombre**, nunca por
valor. gitleaks bloqueante garantiza que ninguno está en claro en el repo.

| Secreto | Ubicación | Uso | Cambia en este intent |
|---------|-----------|-----|:---:|
| `JWT_SECRET` (productivo) | Fly secret (`futmondo-api`) | arranque del servicio (no-default exigido, NFR1.1) | No |
| `JWT_SECRET` (CI, efímero) | inline en workflows (`ci-ephemeral-secret-not-a-real-one`) | que la app importe en pytest; no productivo | No (ya existe en ambos gates) |
| `DATABASE_URL` | Fly secret (`futmondo-api`) | conexión a Neon | No |
| `FLY_API_TOKEN` | GitHub Actions secret | `flyctl deploy` en `fly-deploy.yml` | No |
| `GITHUB_TOKEN` | GitHub Actions (automático) | gitleaks-action en ambos gates | No |

**El gate endurecido no introduce ningún secreto nuevo**: pip-audit, npm audit,
ruff check, el piso de cobertura y el expiry check no requieren credenciales.

## Red y seguridad de red (Q3=A)

**NO-APLICA en términos AWS.** No hay VPC/subnets/security groups/NACL que
inventariar: Fly.io gestiona red, routing y TLS de forma gestionada; la conexión
a Neon es TLS gestionado. Equivalente gratuito de "drift detection": el diff de
git sobre `fly.toml` y los workflows versionados. El intent **no cambia red ni
cifrado** → no requiere risk assessment de infraestructura (guardrail Operation).

## Configuración como código (fuente de verdad)

| Config | Fichero | Cambia en este intent |
|--------|---------|:---:|
| Deploy backend/frontend | `fly.toml` (por app) | No |
| Gate PR | `.github/workflows/ci.yml` | Sí (contenido del gate) |
| Gate push + deploy | `.github/workflows/fly-deploy.yml` | Sí (contenido del job `verify`) |
| Crons | `daily-sync.yml`, `sofascore-sync.yml` | No |

## Mapeo AWS→gratuito (aprovisionamiento)

| Concepto AWS del stage | Equivalente en este stack | Estado |
|------------------------|---------------------------|--------|
| Provisionar VPC/subnets/SG/NACL | Fly.io gestiona la red | NO-APLICA |
| Secrets Manager / SSM Parameter Store | Fly secrets + GitHub Actions secrets | Aplica (gestionado) |
| AWS Config drift detection | diff de git sobre `fly.toml`/workflows | Sustituido |
| Cross-account/cross-VPC connectivity | app↔Neon vía TLS gestionado | NO-APLICA (términos AWS) |
| Multi-AZ / multi-región | single-región `cdg` + Neon Frankfurt (coste 0 €) | NO-APLICA (de pago) |

## Sources

- `../../construction/infrastructure-design/infrastructure-specification.md`.
- `../deployment-pipeline/cd-config.md`.
- `.github/workflows/fly-deploy.yml`, `.github/workflows/ci.yml`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- El entorno de producción es preexistente y su aprovisionamiento no forma parte de este intent config-only.
