# Environment Inventory — Durabilidad del estado

> Etapa Environment Provisioning (Operation). Inventario del entorno de producción de
> futmondo-analytics tras la durabilidad de sesión (u1) y de tareas de sync (u2). Plataforma
> Fly.io + Neon (no AWS); perspectiva de plataforma/seguridad/cumplimiento adaptada a coste 0 €.
> El entorno ya existe y está en producción; esta etapa lo inventaría y valida el delta de la
> durabilidad, no lo aprovisiona de cero.

## Topología del entorno

| Recurso | Detalle | Fuente |
|---------|---------|--------|
| Backend | Fly.io app `futmondo-api`, región `cdg`, puerto interno 8000, `force_https`, healthcheck `/health` (30s/5s) | `backend/fly.toml` |
| Frontend | Fly.io app `futmondo-app`, nginx, puerto 80, healthcheck `/` | `team.md`, `docs/DEPLOY.md` |
| Máquinas | Ambas `min=max=1`, `shared-cpu-1x` / 256 MB (siempre activa, `auto_stop_machines=off`) | `backend/fly.toml` |
| Base de datos | Neon PostgreSQL (Frankfurt), tier free, vía `db_connection` | `team.md`, README |
| Crons coste ~0 | `daily-sync.yml` (04:30 UTC), `sofascore-sync.yml` (05:00 UTC): máquinas Fly one-shot | `team.md` |
| Región | `cdg` (París) en fly.toml (la doc menciona `mad`; prevalece fly.toml como fuente de verdad) | `backend/fly.toml` |

## Inventario de secretos (Fly.io app `futmondo-api`)

| Secret | Propósito | Estado | Delta durabilidad |
|--------|-----------|--------|-------------------|
| `DATABASE_URL` | Conexión Neon PostgreSQL | Existente | — |
| `JWT_SECRET` | Firma JWT; arranque exige no-default (NFR1.1) | Existente | — |
| `FUTMONDO_EMAIL` | Credencial de arranque (cron/global) | Existente | — |
| `FUTMONDO_PASSWORD` | Credencial de arranque (cron/global) | Existente | — |
| `BASE_URL` | Endpoint API Futmondo | Existente | — |
| `CHAMPIONSHIP_ID` | Campeonato por defecto | Existente | — |
| **`FUTMONDO_CRED_KEY`** | **Clave Fernet para cifrado en reposo del handle de re-auth (FR5.1/NFR1)** | **NUEVO — debe fijarse antes del deploy** | **Delta de u1** |
| `FLY_API_TOKEN` (GitHub) | Token de despliegue CI→Fly.io | Existente | — |

Todos los secretos productivos se gestionan via `fly secrets` / GitHub Actions secrets — nunca
literales en el repositorio ni en workflows (regla del equipo; el `JWT_SECRET` efímero de `ci.yml`
es solo un literal de arranque no productivo permitido por el guard).

## Esquema de base de datos (durabilidad)

| Tabla | Creación | Nota |
|-------|----------|------|
| `sync_session` (u1) | Idempotente en el arranque (`ensure_durable_session_schema`) | Sin migración manual |
| `sync_task` (u2) | Idempotente en el arranque (`ensure_durable_task_schema`) | Sin migración manual |

El arranque también ejecuta el sweep `mark_interrupted_on_startup` (u2, FR1.5) y la reconstrucción de
sesión perezosa (u1). No hay paso de provisión de BD fuera del arranque de la app.

## Restricciones y postura

- **Coste**: 0 € — Neon free, Fly.io free allowance, GitHub Actions free. Sin recursos de pago nuevos.
- **Encriptación en reposo**: el handle de re-auth se cifra con Fernet (`FUTMONDO_CRED_KEY`); el
  password nunca se persiste en claro (FR5.1).
- **Cumplimiento**: sin PII regulada nueva (el dato sensible es la credencial Futmondo del usuario,
  ahora cifrada en reposo — reduce exposición frente al estado previo). Sin residencia de datos
  regulada adicional (Neon Frankfurt / Fly `cdg`, ambos UE).
- **Paridad de entornos**: no hay staging separado (decisión del equipo); el smoke test `/health`
  es la verificación de release.
