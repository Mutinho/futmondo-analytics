# Configuración de CI — Fiabilidad de la sync

> Conversation language: Spanish. Herramienta: **GitHub Actions**. Intent
> acotado y aditivo: la CI **ya existe** y es adecuada; esta etapa la documenta
> y verifica que ejerce los comandos de Build and Test. **No se modifica** la
> pipeline (backend-only; los tests nuevos de `sync-reliability` ya corren bajo
> `pytest tests`). Todo en tiers gratuitos (coste 0 €).

## Topología de la pipeline (defensa en profundidad, FR8)

Dos caminos, ambos con el mismo gate de calidad:

1. **PR → `main`** — `.github/workflows/ci.yml`, job `quality` (`Lint + Tests + Scans`).
   Marcado como *required status check* en `main` (branch protection): ningún MR
   se fusiona sin pasarlo.
2. **push → `main`** — `.github/workflows/fly-deploy.yml`, job `verify`
   (`Verify (lint + tests)`), del que dependen los deploys vía `needs:`
   (`needs:` no cruza workflows, por eso el gate se replica). Un rojo nunca llega
   a producción (FR8.2).

## Job `quality` (PR) — pasos

| Paso | Herramienta | Modo |
|---|---|---|
| Secret scan | `gitleaks/gitleaks-action@v3` | **BLOQUEANTE** |
| Backend deps | `pip install -r backend/requirements.txt` (Python 3.12) | — |
| Ruff lint | `ruff check .` | Advisory (`continue-on-error`) |
| Backend tests | `pytest tests -q --cov=app --cov-report=term-missing` (`JWT_SECRET` efímero) | **BLOQUEANTE** |
| pip-audit | `pip-audit -r requirements.txt` | Advisory |
| Frontend deps | `npm ci` (Node 22) | — |
| ESLint | `ng lint` | Advisory |
| Frontend tests | `ng test --watch=false` (Vitest + cobertura por métrica) | **BLOQUEANTE** |
| npm audit | `npm audit --audit-level=high` | Advisory |

## Job `verify` (push→`main`) — pasos

| Paso | Herramienta | Modo |
|---|---|---|
| Secret scan | `gitleaks/gitleaks-action@v2` | **BLOQUEANTE** |
| Backend tests | `pytest tests -q` (`JWT_SECRET` efímero) | **BLOQUEANTE** |
| Frontend tests | `ng test --watch=false` | **BLOQUEANTE** |
| (deploy) | `deploy-backend` → `deploy-frontend` → `smoke-test` (`/health`) | tras `verify` verde |

## Ubicación de los tests de esta unidad en la CI

Los 4 ficheros de test nuevos de `sync-reliability`
(`test_sync_step_status.py`, `test_sync_degraded_steps.py`,
`test_market_bid_sanity_cap.py`, `test_token_store_migrations.py`) viven en
`backend/tests/` y por tanto los recoge `pytest tests` en **ambos** caminos del
gate (job `quality` del PR y job `verify` del push), sin ningún cambio de
configuración. La suite completa (166 tests) es el gate bloqueante.

## Artefactos y despliegue

- Sin repos de artefactos dedicados (ECR/CodeArtifact/S3). El deploy lo hace
  `fly-deploy.yml` a Fly.io (región `cdg`): backend `futmondo-api` y frontend
  `futmondo-app`, con smoke test contra `/health`.
- Secretos vía `secrets` de GitHub Actions / Fly.io; el `JWT_SECRET` de CI es un
  literal efímero no productivo (exigido por NFR1.1 para que la app importe).

## Cambios de este intent

**Ninguno en la configuración de CI.** El intent es backend-only y aditivo; los
tests nuevos ya se ejecutan bajo el `pytest tests` existente. La CI se documenta
"tal cual" y se verifica que ejerce los comandos de Build and Test.

## Deuda diferida (fuera de alcance, registrada)

- Paridad de la señal de cobertura `--cov` de backend en el job `verify` (hoy
  `pytest -q` sin `--cov`, mientras `ci.yml` mide con `--cov=app`).
- SAST/DAST del frontend más allá de ESLint advisory.

## Sources

- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`,
  `construction/build-and-test/{build-and-test-summary,test-results}.md`,
  `construction/sync-reliability/code-generation/code-summary.md`.

## Assumptions & Open Questions

None.
