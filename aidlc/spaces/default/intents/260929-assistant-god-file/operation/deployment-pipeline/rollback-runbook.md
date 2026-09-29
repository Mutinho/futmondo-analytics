# Rollback Runbook — refactor DDD del asistente

Intent `260929-assistant-god-file`, scope `refactor` (Minimal). El runbook de rollback vigente vive
en `docs/ROLLBACK.md` (fuente de verdad, versionado en el repo). Este documento lo referencia y
resume, y añade la nota específica del refactor. No se cambia el mecanismo de rollback.

## Cuándo hacer rollback

- El smoke test post-deploy contra `/health` falla (el workflow lo marca en rojo).
- Un error funcional o de disponibilidad se detecta en producción tras un merge a `main`.

## Procedimiento (resumen de `docs/ROLLBACK.md`)

Precondición: `flyctl` autenticado con acceso a `futmondo-api` y `futmondo-app`.

1. **Identificar la release previa sana**:
   ```bash
   fly releases --app futmondo-api
   fly releases --app futmondo-app
   ```
2. **Revertir a la imagen previa** (rollback directo recomendado):
   ```bash
   fly releases rollback <vN> --app futmondo-api
   # y, si el frontend quedó afectado:
   fly releases rollback <vN> --app futmondo-app
   ```
   Alternativa: redeploy explícito de la imagen previa
   (`fly deploy --app <app> --image <registry.fly.io/...:deployment-XXXX>`).
3. **Verificar salud**:
   ```bash
   curl -sS https://futmondo-api.fly.dev/health   # esperado: HTTP 200 {"status":"healthy"}
   ```
   Si sigue en rojo, escalar y considerar `fly machine stop` mientras se diagnostica.

## Nota específica del refactor

- **Rollback trivial y seguro**: como el refactor preserva la superficie pública vía el shim de
  re-export, revertir a la release previa (el god-file monolítico) es un rollback estándar de imagen
  Fly.io — no hay cambio de esquema ni de contrato que deshacer. El artefacto previo y el nuevo son
  intercambiables desde el punto de vista del endpoint.
- **Sin migración que revertir**: el intent no toca esquema de BD (OOS5); el rollback no requiere
  pasos de datos.

## Limitaciones conocidas (aceptadas)

- El estado en memoria (`TaskManager`, syncs en curso) se **pierde** en cada redeploy/rollback:
  limitación del modelo de un único entorno. Los syncs en curso se relanzan tras el rollback.
- No hay staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`): el gate de CI debe pasar antes de
  fusionar (`docs/PR-GATE.md`).
- Registrar el incidente y la causa raíz.

## Disparadores de rollback (resumen)

| Disparador | Detección | Acción |
|-----------|-----------|--------|
| Smoke `/health` != 200 post-deploy | job `smoke-test` en rojo | rollback manual `fly releases rollback` |
| Error funcional/disponibilidad en prod | observación / `fly logs` | rollback manual + PR de fix |
