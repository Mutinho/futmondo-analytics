# Drift Report — Feedback & Optimization (FR3.2 + FR4)

Detección de drift a coste 0 €: **diff de git** sobre la configuración
versionada (sin AWS Config; NO-APLICA).

## Superficie de configuración versionada

| Config | Fichero(s) | Cómo se detecta drift |
|---|---|---|
| Topología / runtime Fly.io | `backend/fly.toml`, `fly.toml` frontend | `git diff` / revisión de PR |
| Build backend | `backend/Dockerfile`, `backend/nixpacks.toml` | `git diff` |
| Pipeline CI/CD | `.github/workflows/*.yml` | `git diff` |
| Lint | `backend/ruff.toml` | `git diff` (incluye el cambio `E722` de este intent) |

## Estado tras el intent

- **Sin drift de infraestructura**: este intent no cambia `fly.toml` ni la
  topología (dos apps `min=max=1`, Neon). El único cambio de config versionada
  es `ruff.toml` (`E722` advisory), en su commit aislado.
- Cualquier cambio manual en la consola de Fly.io que no se refleje en
  `fly.toml` sería drift; la práctica es mantener `fly.toml` como fuente de
  verdad y aplicar por deploy.

## NO-APLICA (coste 0 €)

- AWS Config / drift detection gestionado → NO-APLICA. Alternativa: diff de git
  sobre config versionada + revisión en PR. Documentado, no inventado.

## Assumptions & Open Questions

None.
