# CI/CD Pipeline — u2-integrations (Integraciones)

El pipeline de entrega **no cambia su estructura** en este intent: se reusa el
gate CI bloqueante y la cadena de despliegue Fly.io existentes. La única
intervención de pipeline es un **cambio de config aislado** (`E722` advisory).
Coste 0 € (GitHub Actions free + Fly.io free allowance).

Consume: `observability-design.md`, `reliability-design.md`, `security-design.md`,
`logical-components.md`, `contract-summary.md`. Perspectivas inline: plataforma +
DevSecOps + Compliance.

## Pipeline existente (sin cambio de estructura)

Dos workflows, **sin cambio en la cadena `needs:`**:

- **`ci.yml`** (disparo `pull_request` → `main`): gate bloqueante
  **gitleaks + `pytest` (`--cov=app`) + `ng test`**. Un rojo bloquea el merge.
- **`fly-deploy.yml`** (disparo push → `main`): job **`verify`**
  (gitleaks + `pytest -q` + `ng test`) → **`deploy-backend`** →
  **`deploy-frontend`** → **`smoke-test`** (`/health`, 5 reintentos, HTTP 200).

| Stage | Gate | Acción si falla |
|---|---|---|
| `verify` (gitleaks) | sin secretos en el diff (incl. tests) | bloquea |
| `verify` (`pytest`) | suite backend en verde (NFR4.1) | bloquea |
| `verify` (`ng test`) | suite frontend en verde | bloquea |
| `deploy-backend` | despliegue Fly.io OK | aborta release |
| `deploy-frontend` | despliegue Fly.io OK | aborta release |
| `smoke-test` | `/health` = 200 | marca release fallida |

## Intervención de pipeline de U2: `E722` advisory por trinquete

- **Cambio**: quitar `E722` (bare-except) del `ignore` de `backend/ruff.toml`
  (una sola línea) para que `ruff check` lo **reporte**.
- **NO** se promueve `ruff check` a bloqueante: sigue **advisory** en CI.
- **Aislamiento**: va en su **propio commit** (`chore(ci)`), **sin `--fix` ni
  `ruff format`**, para no inflar diffs, no exponer avisos preexistentes en masa
  ni invalidar el pase de revisión en vuelo (regla de proyecto afirmada). La
  reviewer sólo corre `ruff check`, no `ruff format`.
- **Cadena `needs:` sin cambio**; el pipeline mantiene su forma.

## Estrategia de despliegue y rollback (sin cambio)

- **Despliegue**: on-merge a `main` → Fly.io (región `cdg`). Sin blue-green ni
  canary (topología `min=max=1`, coste 0 €); es un **recreate** implícito por
  redeploy de Fly.
- **Rollback**: manual, `flyctl` redeploy de la release anterior; runbook
  `docs/ROLLBACK.md`. El estado en memoria (syncs en curso) se pierde en el
  redeploy — limitación aceptada.
- **Promoción de entornos**: no hay staging separado; el smoke test `/health` es
  la verificación de release.

## Secretos en CI/CD (sin cambio)

- Secretos vía `secrets` de GitHub Actions / `fly secrets`, nunca literales en el
  workflow. `gitleaks` bloquea en CI (PR) y `verify` (push). Los specs de U2 usan
  fakes/dobles, nunca credenciales/tokens reales.

## Deuda de pipeline DIFERIDA (fuera de alcance)

- Asimetría de la señal de cobertura backend: `verify` corre `pytest -q` **sin
  `--cov`** mientras `ci.yml` mide `--cov=app`. Registrada como deuda; este
  intent no la cierra.

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- CodePipeline / entornos gestionados / DAST gestionado / aprobación formal de
  producción → NO-APLICA (single-maintainer, coste 0 €). El gate CI bloqueante +
  smoke test es la garantía de release.

## Assumptions & Open Questions

None.
