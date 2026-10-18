# Drift Report — F1: Login nativo end-to-end

> Fase: operación (feedback-optimization). Idioma: castellano; tokens técnicos verbatim en inglés.
> Sin AWS Config drift detection (otro stack): la detección de drift es el **diff de git sobre la
> configuración versionada** (`fly.toml`, workflows de CI/CD), que es la fuente de verdad del
> estado de infraestructura de este proyecto. Coherente con `aidlc-shared/operation-fly-stack.md`.

## Configuración de infraestructura versionada (fuente de verdad)

Toda la configuración de despliegue está en git y tracked:

- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (+ `daily-sync.yml`,
  `sofascore-sync.yml`).
- `backend/fly.toml`, `angular-app/fly.toml`, `cron/fly.toml`.

## Resultado de drift (2026-10-18)

- **Sin drift de configuración de infraestructura por F1**: D-01 **no modificó** ningún `fly.toml`
  ni workflow (el ajuste fue solo en `backend/app/auth/`). La topología (dos apps Fly.io región
  `cdg` + Neon) coincide con lo versionado.
- `git status` en el working tree muestra únicamente **artefactos AI-DLC de esta sesión** (el
  record del intent bajo `aidlc/...`), no cambios en config de infraestructura.
- La paridad del gate PR ↔ push (`ci.yml` vs job `verify` de `fly-deploy.yml`) se mantiene como
  estado heredado del repo; F1 no la alteró.

## Método (gratuito)

```bash
git status --short                 # cambios no commiteados
git diff -- '*.toml' .github/workflows/   # drift en config de infra/CI
git ls-files | grep -E "fly\.toml|workflows/"  # inventario versionado
```

## NO-APLICA (otro stack)

| AWS Config (stage) | Estado |
|---|---|
| Drift detection gestionada | NO-APLICA; sustituida por diff de git sobre config versionada |

## Deuda conocida (no es drift, es documentación)

- El comentario de cabecera de `backend/ruff.toml` quedó **stale** (describe modo advisory aunque
  `ruff check` es bloqueante). Es deuda de documentación registrada, no drift de infraestructura;
  F1 no la toca.

## Sources

- [consumes] deployment-log.md; cd-config.md.
- [code] `git status`/`git ls-files` (2026-10-18); `.github/workflows/*.yml`, `*/fly.toml`.
- [memory] aidlc-shared/operation-fly-stack.md (AWS Config → diff de git); team.md `## Code Style`
  (ruff.toml stale como deuda de documentación); project.md (coste 0 €).

## Assumptions & Open Questions

None.
