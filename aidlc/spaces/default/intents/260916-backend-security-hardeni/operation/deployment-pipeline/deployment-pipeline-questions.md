# Preguntas — Deployment Pipeline (Backend Security Hardening)

Scope `security-patch`, depth Minimal, brownfield, fase Operation. El pipeline
de CD ya existe y es maduro (`.github/workflows/fly-deploy.yml`), y las cinco
correcciones de seguridad **no lo modifican**: son cambios de código + tests que
el pipeline actual despliega por su vía habitual.

En Construcción/Operation las preguntas son excepcionales y aquí las decisiones
de CD ya están tomadas y afirmadas en `team.md` (`## Deployment`):

- **Estrategia de despliegue**: on-merge a `main` → Fly.io (región `cdg`), sin
  staging separado; smoke test `/health` como verificación de release.
- **Orden**: `verify` (gitleaks + pytest + ng test) → `deploy-backend` →
  `deploy-frontend` → `smoke-test` (5 reintentos contra `/health`).
- **Gates de promoción**: gate de CI bloqueante en el MR + branch protection; el
  job `verify` de push→`main` lo replica (incluido gitleaks).
- **Rollback**: manual documentado (`docs/ROLLBACK.md`) vía `fly releases
  rollback`.
- **Coste 0 €**: Fly.io free allowance + GitHub Actions free.

Esta etapa, por tanto, **documenta y confirma** el pipeline existente como apto
para este release de seguridad (no crea ni modifica un CD nuevo), en línea con
la naturaleza «verificar y documentar» del intent.

## No se abren preguntas sustantivas nuevas

Ninguna decisión de CD queda sin resolver para este patch. No aplica Q&A
interactivo.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
