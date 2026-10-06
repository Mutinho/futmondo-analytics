# CD Config — calculadora-mejora (Fly.io, coste 0 €)

> Adaptación AWS→Fly.io (ver `knowledge/aidlc-shared/operation-fly-stack.md`).
> Esta etapa **documenta** el pipeline de CD existente aplicado a este cambio
> frontend-only; no crea pipeline nuevo (CI Pipeline e Infrastructure Design
> SKIP por scope `refactor`).

## Pipeline de CD existente (`.github/workflows/fly-deploy.yml`)

Disparo: push a `main`. Cadena `needs:` (intacta, no se reordena):

```
verify  →  deploy-backend  →  deploy-frontend  →  smoke-test (/health)
```

- **verify**: gate bloqueante replicado del PR-gate — `gitleaks` + `pytest` + `ng test`. Un rojo nunca llega a producción.
- **deploy-backend**: `futmondo-api` (Fly.io, puerto 8000, check `/health`).
- **deploy-frontend**: `futmondo-app` (nginx + bundle Angular, check `/`). **Este es el job que publica el cambio del toggle** (recompila el bundle con la mejora).
- **smoke-test**: 5 reintentos contra `/health`, HTTP 200 = release verificado.

## Qué cambia para este intent

- **Nada en la topología ni el orden**: el cambio es frontend; `deploy-frontend`
  reconstruye el bundle Angular con el toggle. No hay migraciones de BD, cambios
  de backend ni de infraestructura.
- **Crons** (`daily-sync.yml`, `sofascore-sync.yml`): sin cambios.

## Secretos y coste

- Secretos vía `secrets` de GitHub Actions / Fly.io; en CI el `JWT_SECRET` es
  efímero y no productivo. Todo en tiers gratuitos (coste 0 €).

## Feature flags

- NO-APLICA infraestructura de feature-flags gestionada (sería de pago / fuera
  de tier free). El propio toggle "Incorporar jugadores en venta" es una
  preferencia de UI en `localStorage`, no un release flag de pipeline.

## Sources

- `.github/workflows/fly-deploy.yml`, `ci.yml` (pipeline existente).
- `team.md` → `## Deployment`; `knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

None.
