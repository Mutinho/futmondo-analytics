# CD Config — Enriquecimiento del sync de jugadores

## Pipeline existente (sin cambios)

Este intent **no modifica** el pipeline de CD. Se despliega a través del flujo
Fly.io ya operativo (`.github/workflows/fly-deploy.yml`):

```
push a main → verify (gate bloqueante) → deploy-backend → deploy-frontend → smoke-test
```

- **verify**: réplica del gate de CI (gitleaks + ruff check + pytest + pip-audit
  + ng test + npm audit). Un rojo no llega a producción.
- **deploy-backend**: `futmondo-api` (Fly.io, región `cdg`, puerto 8000,
  healthcheck `/health`). Redeploy rolling con healthcheck.
- **deploy-frontend**: `futmondo-app` (nginx). Este intent es solo backend; el
  frontend se redepliega sin cambios funcionales.
- **smoke-test**: `GET /health` (5 reintentos, HTTP 200).

## Base de datos

- **Neon PostgreSQL** (eu-central-1, tier free), compartida.
- **Migración de esquema: MANUAL, ya aplicada.** Las 6 columnas nuevas de
  `players` (`points`, `change`, `home_average`, `away_average`, `matches`,
  `status`) se añadieron directamente a Neon con `ALTER TABLE ... ADD COLUMN IF
  NOT EXISTS` (no destructivo, idempotente), ANTES de desplegar el código que
  las usa, y verificadas (las 6 presentes). El `ALTER` de arranque se retiró del
  código: la migración NO se auto-aplica (decisión del propietario).

## Secretos

- Vía `secrets` de GitHub Actions / Fly.io; `JWT_SECRET` efímero en CI.
  `DATABASE_URL` nunca en el repo.

## Orden seguro de release (este cambio)

1. ✅ Migración manual a Neon (hecha) — las columnas existen antes del deploy.
2. Merge a `main` → pipeline Fly.io despliega el backend nuevo.
3. (Opcional) lanzar un sync de jugadores para poblar las columnas de inmediato;
   si no, el sync periódico lo hace.
