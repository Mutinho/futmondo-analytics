# CI Configuration — Construcción (FR3.2 + FR4)

El CI/CD **ya existe y es adecuado**; este intent no cambia su estructura. Se
documenta la configuración vigente y la única incidencia (config `E722`
advisory). Coste 0 € (GitHub Actions free tier).

## Herramienta y disparadores

- **GitHub Actions** (free tier).
- **`ci.yml`**: disparo `pull_request` → `main`. Gate **bloqueante**.
- **`fly-deploy.yml`**: disparo push → `main`. Job `verify` (re-ejecuta el gate)
  → `deploy-backend` → `deploy-frontend` → `smoke-test`.
- **Crons** (coste ~0): `daily-sync.yml` (04:30 UTC), `sofascore-sync.yml`
  (05:00 UTC) — máquinas Fly one-shot; ejercitan las rutas de sync endurecidas.

## Rama y merge

- Trunk-based sobre `main`; ramas cortas con prefijo (`fix/`, `chore/`, `feat/`).
- **Squash-merge** a `main` vía Merge Request (cada MR = un commit).
- Conventional Commits en castellano. El commit de `E722` va aislado como
  `chore(ci)`.

## Etapas del pipeline (sin cambio en la cadena `needs:`)

| Workflow | Job/Etapa | Acción |
|---|---|---|
| `ci.yml` | gate | gitleaks + `pytest` (`--cov=app`) + `ng test` — **bloqueante** |
| `fly-deploy.yml` | `verify` | gitleaks + `pytest -q` + `ng test` |
| `fly-deploy.yml` | `deploy-backend` | deploy Fly.io `futmondo-api` |
| `fly-deploy.yml` | `deploy-frontend` | deploy Fly.io `futmondo-app` (nginx) |
| `fly-deploy.yml` | `smoke-test` | `/health` 5 reintentos, HTTP 200 |

## Incidencia de este intent: `E722` advisory (FR3.2.3)

- `backend/ruff.toml`: `E722` (bare-except) **fuera de `ignore`** para que
  `ruff check` lo reporte. `ruff check` sigue **advisory** (no bloqueante);
  cambio de una línea, commit aislado `chore(ci)`, sin `--fix`/`ruff format`.
  (Verificado ya presente en HEAD.)

## Repositorios de artefactos

- Ninguno nuevo. Las imágenes se construyen en el deploy de Fly.io
  (`Dockerfile`/`nixpacks.toml`); sin ECR/registry externo (coste 0 €).

## Secretos

- Vía `secrets` de GitHub Actions / `fly secrets`; nunca literales. Los tests
  usan fakes; `gitleaks` los escanea.

## Assumptions & Open Questions

None.
