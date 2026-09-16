# Environment Provisioning Questions — Durabilidad del estado

> Etapa Environment Provisioning (Operation). En Operation las preguntas son excepcionales; aquí
> todo el contexto de entorno ya está decidido y documentado (fly.toml, `docs/DEPLOY.md` actualizado
> con el secret nuevo durante code-generation). No se abren preguntas nuevas: la etapa se ejecuta
> sobre contexto ya resuelto para inventariar el entorno y validar el delta operativo del secret.

## Contexto resuelto (no requiere pregunta)

- **Entorno**: Fly.io (región `cdg`) + Neon PostgreSQL (Frankfurt), tier gratuito. Dos apps:
  `futmondo-api` (backend, `/health`) y `futmondo-app` (frontend nginx). `min=max=1`,
  `shared-cpu-1x` / 256 MB. (De `backend/fly.toml` y `team.md`.)
- **Secretos existentes**: `DATABASE_URL`, `JWT_SECRET`, `FUTMONDO_EMAIL`, `FUTMONDO_PASSWORD`,
  `BASE_URL`, `CHAMPIONSHIP_ID` — via secrets de Fly.io. (De `docs/DEPLOY.md`.)
- **Secreto NUEVO (delta de durabilidad)**: `FUTMONDO_CRED_KEY` (clave Fernet, FR5.1/NFR1). Ya
  documentado en `docs/DEPLOY.md` con generación (`Fernet.generate_key()`), semántica y
  comportamiento sin configurar (401 accionable). Debe fijarse como secret de Fly.io antes del deploy.
- **Esquema durable** (`sync_session`, `sync_task`): se crea idempotente en el arranque
  (`ensure_durable_*_schema`), sin paso de provisión de BD manual.
- **Cumplimiento**: sin PII regulada nueva; el cambio REDUCE exposición de credenciales (password ya
  no en claro en reposo). Coste 0 € (sin servicios de pago nuevos).

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
