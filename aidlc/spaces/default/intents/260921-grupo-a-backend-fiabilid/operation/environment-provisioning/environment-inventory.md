# Inventario del entorno — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. **Adaptación de stack**
> (regla de `project.md`): stack real Fly.io + Neon, no AWS. Entorno **ya
> provisionado y en producción**; se inventaría el existente, no se crea nada.
> Coste 0 €.

## Entorno de producción (único)

| Recurso | Detalle | Check de salud |
|---|---|---|
| Backend `futmondo-api` | Fly.io app, región `cdg`, puerto 8000 (FastAPI/Python 3.12) | `GET /health` → 200 `{"status":"healthy"}` |
| Frontend `futmondo-app` | Fly.io app, nginx, puerto 80 (Angular PWA) | `GET /` → 200 |
| Base de datos | Neon PostgreSQL, Frankfurt, tier free | conexión TLS vía `DATABASE_URL` |
| Crons coste ~0 | `daily-sync.yml` (04:30 UTC), `sofascore-sync.yml` (05:00 UTC) | máquinas Fly one-shot |

- No hay staging separado (restricción coste 0 €). La verificación de release es
  el smoke test `/health`.

## Red y conectividad

- **NO-APLICA (términos AWS)**: VPC, subnets, security groups, NACLs. Fly.io
  gestiona el routing y expone las apps por HTTPS.
- Rutas reales: `futmondo-app` (nginx) proxya `/api/*` y `/auth/*` a
  `futmondo-api`; `futmondo-api` conecta a Neon por TLS.
- Sin cross-account / cross-VPC.

## Secretos y configuración

| Secreto | Ubicación | Uso |
|---|---|---|
| `DATABASE_URL` | Fly secret (backend) | conexión a Neon (TLS) |
| `JWT_SECRET` | Fly secret (backend) | firma JWT; **no-default** exigido en arranque (NFR1.1) |
| `FLY_API_TOKEN` | GitHub Actions secret | `flyctl deploy` en CD |
| `JWT_SECRET` (CI) | literal efímero en workflow | solo arranque no productivo en CI |

- **NO-APLICA**: AWS Secrets Manager / Parameter Store. Los secretos viven en
  Fly.io / GitHub Actions; nunca literales productivos en el repo (gitleaks
  bloqueante los vigila).

## Impacto de este intent en el inventario

**Ninguno.** El intent es backend-only y aditivo (helper de estado degradado,
techo de `price`, `except` acotados). No añade recursos, apps, secretos, tablas
ni cambia la red. El código nuevo se despliega en la app `futmondo-api`
existente.

## NO-APLICA / diferido (servicios de pago)

- CloudWatch, VPC/SG/NACL, Secrets Manager/Parameter Store, cross-account: no
  existen en este stack; su equivalente gratuito (Fly logs, `fly secrets`,
  healthcheck) cubre la necesidad operativa del intent.

## Sources

- `README.md` (topología de producción), `operation/deployment-pipeline/cd-config.md`,
  `.github/workflows/fly-deploy.yml`, `docs/DEPLOY.md`, `project.md` (regla de
  adaptación de stack).

## Assumptions & Open Questions

None.
