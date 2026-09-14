# Configuración de CD — Futmondo Analytics

> Brownfield: el pipeline de CD ya existe. Este documento lo describe tal cual y
> confirma que este bugfix fluye por él sin cambios.

## Pipeline existente: `.github/workflows/fly-deploy.yml`

Trigger: `push` a `main`.

Secuencia de jobs:
1. **verify** (BLOQUEANTE) — Python 3.12; `JWT_SECRET` efímero; ejecuta
   `python -m pytest tests -q` (backend) y `ng test` (frontend). **Este es el
   gate que desbloquea el intent**: con la suite en verde (54 passed), deja de
   bloquear.
2. **deploy backend** — `fly deploy` de `futmondo-api` (París).
3. **deploy frontend** — `fly deploy` de `futmondo-app` (nginx + Angular PWA).
4. **smoke test** — verificación de `/health` post-deploy.

## Cómo fluye este cambio
- Merge del arreglo (`backend/tests/test_analytics_service.py`) a `main`.
- `verify` pasa (pytest verde) → se desbloquea el deploy.
- No se modifica el workflow ni la infraestructura (Fly.io, Neon).

## Secretos / configuración
- `JWT_SECRET`, `DATABASE_URL` gestionados como Fly secrets (ver `docs/DEPLOY.md`).
- Sin nuevos secretos ni dependencias con coste (regla coste 0€).

## No aplica a este intent
- No hay cambios de estrategia de branching (trunk-based, squash-merge a `main`).
- No hay migraciones de BD ni feature flags nuevos.
