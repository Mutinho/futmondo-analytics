# CD Configuration — refactor `data_manager_v2`

Configuración de entrega continua **existente**, sin cambios en este refactor de
equivalencia. Fuente de verdad: `.github/workflows/fly-deploy.yml` (versionado).

## Pipeline CD (`fly-deploy.yml`, disparo `push` → `main`)

| Job | Depende de | Qué hace |
|---|---|---|
| `verify` | — | Gate bloqueante: gitleaks (secretos) · allowlist-expiry · pip-audit (entorno instalado) · ruff check · pytest `--cov=app` con piso · npm audit (high) · ng test con cobertura |
| `deploy-backend` | `verify` | `flyctl deploy` en `./backend` (app `futmondo-api`) |
| `deploy-frontend` | `deploy-backend` | `flyctl deploy` en `./angular-app` (app `futmondo-app`) |
| `smoke-test` | `deploy-backend`, `deploy-frontend` | `curl` a `/health` (5 reintentos, exige HTTP 200) |

Un fallo en `verify` **impide** los deploys (`needs:`). Un fallo del smoke test
deja el workflow en rojo → señal para rollback.

## Gate de PR (`ci.yml`, disparo `pull_request` → `main`)

Job `quality`, required status check en `main`: mismo conjunto bloqueante que
`verify` (gitleaks + ruff + pytest con cobertura + pip-audit + ng test + npm
audit; ESLint advisory). Paridad PR ↔ push ya establecida en intents previos.

## Impacto de ESTE refactor sobre el CD

**Ninguno estructural.** No se toca `fly-deploy.yml` ni `ci.yml`: el refactor es
código de aplicación (descomposición DDD) que el pipeline existente valida tal
cual. Lo que cambia es que el gate ahora ejerce **68 tests de caracterización
nuevos** y una **cobertura mayor** (57.48%), ambos ya verdes localmente
(ver Build and Test). El piso `--cov-fail-under` no se relaja.

## Secretos y coste

- Secretos vía `secrets`/`vars` de GitHub Actions y `fly secrets`. En CI el
  `JWT_SECRET` es efímero y no productivo (`ci-ephemeral-secret-not-a-real-one`).
- Acciones de terceros: `gitleaks-action@v3` (unificado en ambos gates),
  `superfly/flyctl-actions/setup-flyctl@master`. El pin por SHA de acciones
  mutables es deuda de `ci-pipeline`, fuera del alcance de este refactor.
- Todo en tiers gratuitos (GitHub Actions, Neon free, Fly.io free). Coste 0 €.

## Pin de versiones del gate (ya existente)

`ruff==0.16.9`, `pip-audit==2.10.1`, Python `3.12`, Node `22`. Sin dependencias
de tooling nuevas en este refactor.
