# Runbook de rollback — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. Consolida y referencia el
> runbook operativo ya presente en el repo (`docs/ROLLBACK.md`, NFR2.2), con la
> nota específica de este intent. Rollback **manual** vía `flyctl`; coste 0 €.

## Cuándo hacer rollback

- El `smoke-test` post-deploy contra `/health` falla (workflow en rojo).
- Se detecta en producción un fallo funcional/disponibilidad tras un merge a
  `main`.

## Precondición

- `flyctl` autenticado con acceso a `futmondo-api` (backend) y `futmondo-app`
  (frontend).

## Procedimiento

1. **Identificar la release estable previa**:
   ```bash
   fly releases --app futmondo-api
   fly releases --app futmondo-app
   ```
   Anotar el `vN` de la última release sana.

2. **Revertir a la imagen previa** (opción A recomendada):
   ```bash
   fly releases rollback <vN> --app futmondo-api
   ```
   Opción B (si `rollback` no está disponible): redeploy explícito de la imagen
   previa con `fly deploy --image <...>`. Repetir para `futmondo-app` si aplica.

3. **Verificar salud tras el rollback**:
   ```bash
   curl -sS https://futmondo-api.fly.dev/health   # esperado: HTTP 200 {"status":"healthy"}
   ```
   Si sigue en rojo, escalar y considerar `fly machine stop` mientras se
   diagnostica.

## Especificidad de este intent (sync-reliability)

- Los cambios son **aditivos y backend-only** (helper de estado `degraded`,
  techo de `price`, `except` acotados). Un rollback de la release del backend
  revierte por completo el intent sin efectos colaterales de esquema: **no hay
  migración de BD** (el estado `degraded` vive en `progress`, JSON libre; no se
  añadieron tablas ni columnas nuevas por esta unidad).
- Por tanto el rollback es un simple redeploy de la release previa del backend;
  no requiere pasos de reversión de datos.

## Limitaciones conocidas (heredadas, aceptadas)

- El estado en memoria (`TaskManager`, sesiones/syncs en curso) se **pierde** en
  cada redeploy/rollback (entorno único). Los syncs en curso se relanzan tras el
  rollback.
- Sin staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI
  (gitleaks + pytest + ng test) debe pasar antes de fusionar.
- Registrar incidente y causa raíz.

## Sources

- `docs/ROLLBACK.md` (runbook operativo del repo), `cd-config.md`,
  `deployment-strategy.md`, `construction/sync-reliability/functional-design/entities.md`
  (sin cambios de esquema).

## Assumptions & Open Questions

None.
