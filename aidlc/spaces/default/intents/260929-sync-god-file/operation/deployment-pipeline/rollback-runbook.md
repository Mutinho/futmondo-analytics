# Rollback Runbook — Fly.io (resumen adaptado de `docs/ROLLBACK.md`)

Intent: `sync-god-file` · scope `refactor` · Operation. Runbook de rollback del
release, referenciando el procedimiento canónico versionado en
[`docs/ROLLBACK.md`](../../../../../../docs/ROLLBACK.md). Entorno único de
producción en Fly.io (sin staging); el rollback es **manual** = redeploy de la
imagen previa. Coste 0 €.

## Triggers de rollback

- El **smoke test post-deploy** contra `/health` falla (el job `smoke-test` de
  `fly-deploy.yml` marca el release en rojo).
- Error funcional o de disponibilidad detectado en producción tras un merge a
  `main`.

## Precondición

- `flyctl` autenticado (`fly auth login`) con acceso a `futmondo-api` (backend) y
  `futmondo-app` (frontend).

## Procedimiento

1. **Identificar la release estable previa:**
   `fly releases --app futmondo-api` (y `--app futmondo-app`). Anotar la `vN` sana
   anterior al deploy problemático.
2. **Revertir a la imagen previa:**
   - Opción A (recomendada): `fly releases rollback <vN> --app futmondo-api`.
   - Opción B (si `rollback` no está en tu `flyctl`): `fly deploy --app
     futmondo-api --image <registry.fly.io/futmondo-api:deployment-XXXX>`.
   - Repetir para `futmondo-app` si el frontend quedó afectado.
3. **Verificar salud:** `curl -sS https://futmondo-api.fly.dev/health` → HTTP 200
   y `{"status":"healthy"}`. Si sigue rojo, escalar y considerar `fly machine
   stop` mientras se diagnostica.

## Escalado y contacto

- Operación single-maintainer: la notificación de fallo llega por el job en rojo
  de GitHub Actions (smoke test). Escalado = el propio maintainer detiene la
  máquina afectada (`fly machine stop`) mientras diagnostica. No hay on-call
  formal ni PagerDuty (coste 0 €).

## Limitaciones conocidas

- El **estado en memoria** (`TaskManager`, sesiones de sync en curso) se **pierde**
  en cada redeploy/rollback: limitación aceptada del modelo de un único entorno.
  Los syncs en curso se relanzan tras el rollback. Nota específica de este intent:
  la extracción de `match_odds` no cambia este comportamiento (sin estado nuevo en
  memoria; misma superficie pública).
- No hay staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI
  bloqueante debe pasar antes de fusionar (ver `docs/PR-GATE.md`).
- Registrar el incidente y la causa raíz (revisión post-incidente para P1/P2) para
  no repetir el fallo.

## Aplicabilidad a este refactor

- El refactor preserva la superficie pública y la equivalencia funcional estricta,
  así que el rollback de esta release no difiere del procedimiento estándar: el
  redeploy de la imagen previa restaura el `data_sync_service.py` anterior a la
  extracción sin pasos especiales.
