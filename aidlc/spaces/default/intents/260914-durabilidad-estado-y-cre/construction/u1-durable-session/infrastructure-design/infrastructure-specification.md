# Infrastructure Specification — u1-durable-session

> Etapa Infrastructure Design (Construction). Mapea el diseño de la sesión durable a la plataforma
> **ya existente** (Fly.io región `cdg` + Neon PostgreSQL Frankfurt free + GitHub Actions). NO es
> AWS. Es diseño (qué infra y por qué), no IaC. Restricción dura: coste 0€, sin servicios nuevos.

## Sources

- nfr-design/security-design.md (FUTMONDO_CRED_KEY cifrado en reposo, secret de Fly.io) [scope]
- nfr-design/scalability-design.md, reliability-design.md (BD autoridad, tolera multi-instancia) [scope]
- nfr-design/logical-components.md (nota infra: 2 tablas + 1 secreto nuevo) [scope]
- domain-design/components.md (UserSession, ProtectedCredential; SessionRepository) [scope]
- team.md (topología Fly.io: futmondo-api/futmondo-app, Neon free, on-merge) [scope]
- infrastructure-design-questions.md (Q1 SQL idempotente, Q2 secreto, Q4 despliegue, Q6 sin migración) [Q1] [Q2] [Q4] [Q6]

## Deployment

| Facet | Choice | Rationale |
|-------|--------|-----------|
| Compute model | Contenedores en Fly.io (apps existentes `futmondo-api` puerto 8000 y `futmondo-app` nginx puerto 80); esta unidad solo toca `futmondo-api` | Sin cambio de topología (Q4-A); C1 mantener stack |
| Networking | Ingress HTTPS vía Fly.io; el backend habla con Neon por TLS; sin subredes/VPC nuevas | No se añade superficie de red; reutiliza la existente |
| Storage | Neon PostgreSQL (Frankfurt, tier free) ya provisionado; se añaden 2 tablas (`UserSession`, `ProtectedCredential`) | BD es la autoridad de estado (NFR5.1/5.2); coste 0€ dentro del tier free |
| Environments | Un solo entorno productivo (sin staging separado); on-merge a `main` | Q4-A; añadir staging implicaría coste (Q4-B rechazada) |
| IaC approach | Sin IaC nueva; `fly.toml` existente sin cambios de recursos. Esquema de tablas por **script SQL idempotente** versionado (`CREATE TABLE IF NOT EXISTS`), aplicado al arranque del backend / pre-deploy | Q1-A; sin herramienta de migraciones (Alembic) nueva; coste 0€ |
| Resource sizing | `shared-cpu-1x` / 256 MB, `min=max=1` máquina por app (sin cambios) | Volumen de sesiones sin crecimiento nuevo (scalability-design); no se re-dimensiona |

### Esquema de las tablas nuevas (ilustrativo, ≤15 líneas)

```sql
-- Aplicado idempotentemente al arranque del backend (Q1-A). No es implementación final.
CREATE TABLE IF NOT EXISTS user_session (
  user_id     TEXT PRIMARY KEY,
  email       TEXT NOT NULL,
  token       TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL              -- TTL 12h (BR1.1)
);
CREATE TABLE IF NOT EXISTS protected_credential (
  user_id            TEXT PRIMARY KEY,
  protected_material BYTEA NOT NULL,            -- handle de re-auth CIFRADO (nunca password en claro)
  scheme             TEXT NOT NULL,             -- p. ej. 'refresh-token+aesgcm-v1' (rotación de clave)
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Infrastructure Services

| Service | Role | Configuration | Notes |
|---------|------|---------------|-------|
| Neon PostgreSQL | database | Frankfurt, tier free; conexión vía `DATABASE_URL` (secret existente) y `db_connection`; +2 tablas | Autoridad de estado y concurrencia (`SELECT ... FOR UPDATE`, NFR5.2); sin réplicas nuevas |
| Fly.io app `futmondo-api` | compute (backend) | Contenedor Python 3.12/FastAPI, puerto 8000, check `/health`; nuevo secret `FUTMONDO_CRED_KEY` | Ejecuta el script SQL idempotente al arrancar; única app tocada por la unidad |
| Fly.io app `futmondo-app` | compute (frontend) | nginx puerto 80, check `/` | Sin cambios en esta unidad |
| Fly.io secrets | secrets-manager | `DATABASE_URL`, `JWT_SECRET` (existentes) + **`FUTMONDO_CRED_KEY`** (nuevo, Q2-A) | `fly secrets set`, fuera del repo; rotación manual + `scheme` versionado; gitleaks bloquea literales |
| GitHub Actions | ci/cd | Workflows `ci.yml` (MR) y `fly-deploy.yml` (push→`main`) | Ver cicd-pipeline.md; se añade gitleaks a `verify` (Q3-A) |

## Shared Infrastructure

No aplica un desglose multi-unidad de recursos compartidos en esta etapa: el contrato inter-unidad es
ninguno (contract-summary: U1 y U2 son independientes, DAG sin aristas). El único recurso compartido
con el resto del backend es la BD Neon (vía `db_connection`), donde esta unidad **añade** tablas
propias sin tocar las existentes.

| Shared Resource | Owner Unit | Consumer Units | Access Boundary |
|-----------------|-----------|----------------|-----------------|
| Neon PostgreSQL (`db_connection`) | plataforma (preexistente) | u1-durable-session (tablas `user_session`, `protected_credential`); resto del backend (tablas existentes) | Cada unidad accede solo a sus tablas vía la capa estrecha `stores/`; sin SQL cruzado entre unidades |

## Notas de coste y cumplimiento

- **Coste 0€ (NFR3):** sin servicios nuevos; 2 tablas y 1 secret caben en los tiers free (Neon free,
  Fly.io free allowance, GitHub Actions free).
- **Cumplimiento (compliance):** no se introduce marco regulatorio nuevo ni PII nueva. El único dato
  sensible es el handle de re-auth (clasificación **restricted**), cifrado en reposo (secret de
  Fly.io) y con retención acotada por el TTL de 12h. La contraseña NUNCA se persiste (FR5/Q6-A). Sin
  obligaciones GDPR/PCI nuevas derivadas de esta unidad.
