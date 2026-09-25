# Rollback Runbook — Operación (FR3.2 + FR4)

Procedimiento de rollback del despliegue Fly.io. Se **alinea con el runbook ya
existente** en `docs/ROLLBACK.md` (la fuente operativa canónica); este documento
lo resume en el registro del intent. Rollback **manual** = redeploy de la release
previa (NFR2.2, entorno único, sin staging).

## Escalado y contacto

- **Operación single-maintainer** (proyecto personal). El escalado es la
  notificación nativa de GitHub Actions (deploy/cron en rojo) + inspección
  manual. No hay on-call ni PagerDuty (coste 0 € — NO-APLICA).

## Cuándo hacer rollback

- El `smoke-test /health` post-deploy falla (el workflow queda en rojo).
- Un error funcional o de disponibilidad se detecta en producción tras un merge.

## Precondición

- `flyctl` autenticado con acceso a `futmondo-api` (backend) y `futmondo-app`
  (frontend).

## Procedimiento

1. **Identificar la release estable previa**:
   ```bash
   fly releases --app futmondo-api
   fly releases --app futmondo-app
   ```
   Anotar la `vN` de la última release sana.
2. **Revertir**:
   ```bash
   fly releases rollback <vN> --app futmondo-api   # y --app futmondo-app si aplica
   ```
   (Alternativa: `fly deploy --image <imagen previa>` si `rollback` no está en tu
   versión de flyctl.)
3. **Verificar salud**:
   ```bash
   curl -sS https://futmondo-api.fly.dev/health   # esperado: HTTP 200 {"status":"healthy"}
   ```

## Limitaciones conocidas

- El estado en memoria (`TaskManager`, syncs en curso) se pierde en el
  redeploy/rollback (limitación aceptada del modelo de un entorno). Los syncs se
  relanzan tras el rollback (el diseño de fiabilidad garantiza que un sync
  interrumpido no dejó datos corruptos — reemplazo atómico de `team_prizes`).
- Sin staging: la verificación de release es el smoke `/health`.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI debe
  pasar antes de fusionar.
- Registrar el incidente y la causa raíz (ver `incident-response`, etapa 4.5).

## Referencia canónica

- `docs/ROLLBACK.md` (en el repo) es el runbook operativo vigente; este resumen
  no lo sustituye.

## Assumptions & Open Questions

None.
