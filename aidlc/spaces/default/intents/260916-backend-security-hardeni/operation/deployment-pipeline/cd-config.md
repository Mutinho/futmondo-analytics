# Configuración de CD — Backend Security Hardening

> Scope `security-patch`, depth Minimal, brownfield, fase Operation. Este
> documento **confirma y documenta** el pipeline de CD existente
> (`.github/workflows/fly-deploy.yml`) como apto para desplegar este release de
> seguridad. No se crea ni modifica pipeline: las cinco correcciones (FR6, FR7,
> FR8, FR9, FR18) se despliegan por la vía habitual. Stack real: Fly.io + Neon,
> coste 0 €.

## Pipeline de CD existente (autoritativo)

Fichero: `.github/workflows/fly-deploy.yml`. Disparo: `push` a `main` (más
`workflow_dispatch` manual). Jobs encadenados por `needs:`:

| Job | Depende de | Qué hace |
|-----|-----------|----------|
| `verify` | — | gitleaks (bloqueante) + `pytest -q` (Python 3.12) + `ng test` (Node 22) |
| `deploy-backend` | `verify` | `flyctl deploy` en `./backend` (app `futmondo-api`) |
| `deploy-frontend` | `deploy-backend` | `flyctl deploy` en `./angular-app` (app `futmondo-app`) |
| `smoke-test` | `deploy-backend`, `deploy-frontend` | `curl` a `/health`, 5 reintentos esperando HTTP 200 |

Un rojo en `verify` impide los deploys (defensa en profundidad sobre el gate de
CI del MR + branch protection).

## Gates de calidad (bloqueantes)

- **gitleaks**: escaneo de secretos. **Nota de corrección**: el job `verify` de
  `fly-deploy.yml` **ya replica gitleaks** (`gitleaks-action@v2`), cerrando el
  hueco FR5 que `team.md` anotaba como pendiente. Push→`main` y PR→`main` están
  ambos cubiertos.
- **pytest**: suite del backend (135 passed en esta etapa; ver Build and Test).
- **ng test**: suite del frontend (Vitest). Este patch no toca el frontend.

## Topología de despliegue

- Backend `futmondo-api`: puerto 8000, healthcheck `/health` (`interval=30s`,
  `timeout=5s`), `min=max=1` máquina `shared-cpu-1x`/256 MB, región `cdg`,
  `force_https=true`.
- Frontend `futmondo-app`: nginx, puerto 80, check `/`.
- BD: Neon PostgreSQL (Frankfurt, tier free). Este patch no requiere migración
  de esquema.

## Secretos

Los secretos productivos SIEMPRE via GitHub Actions / Fly.io (`FLY_API_TOKEN`,
`JWT_SECRET`, `DATABASE_URL`), nunca literales en el workflow. El `JWT_SECRET`
efímero de CI es un literal de arranque no productivo, exigido por el guard
NFR1.1/NFR1.2. Ninguna de las cinco correcciones introduce secretos.

## Idoneidad para este patch

Las correcciones son cambios de código Python + tests y una edición de
`docker-compose.yml` (solo entorno local, no productivo; Fly.io usa `fly.toml`,
que no tenía `SSL_VERIFY`). El pipeline existente las despliega sin cambios de
configuración de CD.
