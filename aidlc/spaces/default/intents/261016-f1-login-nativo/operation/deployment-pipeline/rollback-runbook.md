# Rollback Runbook — F1: Login nativo end-to-end

> Fase: operación (deployment-pipeline). Idioma: castellano; comandos y rutas verbatim. NFR de
> operación: toda procedura de despliegue incluye pasos de rollback. F1 reutiliza el runbook de
> rollback del repo (`docs/ROLLBACK.md`) para el backend y añade el procedimiento del canal iOS.

## Canal 1 — Backend D-01 (Fly.io): reutiliza `docs/ROLLBACK.md`

El rollback del backend ya está documentado y no cambia en F1. Resumen operativo (fuente de verdad:
`docs/ROLLBACK.md`):

### Cuándo

- El `smoke-test` post-deploy contra `/health` falla (el workflow queda en rojo).
- Se detecta un fallo funcional del login/refresh en producción tras un merge a `main`.

### Precondición

- `flyctl` autenticado con acceso a `futmondo-api` (backend) y `futmondo-app` (frontend).

### Procedimiento

1. Identificar la release estable previa:
   ```bash
   fly releases --app futmondo-api
   ```
2. Revertir (recomendado):
   ```bash
   fly releases rollback <vN> --app futmondo-api
   ```
   Alternativa (redeploy explícito de imagen previa):
   ```bash
   fly deploy --app futmondo-api --image <registry.fly.io/futmondo-api:deployment-XXXX>
   ```
3. Verificar salud:
   ```bash
   curl -sS https://futmondo-api.fly.dev/health   # espera HTTP 200 + {"status":"healthy"}
   ```

### Específico de D-01

- El rollback del backend al estado previo a D-01 **restaura el comportamiento solo-cookie**. La
  PWA sigue funcionando (nunca dependió del `refresh_token` del body). La **app iOS perdería la
  capacidad de refrescar** (dejaría de recibir el refresh token por body/header), degradando a
  "requiere re-login" — es el comportamiento seguro esperado, sin corrupción de datos.
- D-01 **no tiene migraciones de BD**, por lo que el rollback no requiere revertir esquema.

### Disparadores de rollback (backend)

| Disparador | Umbral | Acción |
|------------|--------|--------|
| Smoke `/health` | != HTTP 200 tras 5 reintentos | Rollback a release previa |
| Error funcional de `/auth/login` o `/auth/refresh` en prod | observado por el mantenedor | Rollback + PR con fix |

## Canal 2 — App iOS (`xtool`): reinstalar build anterior

No hay despliegue atómico reversible de la app nativa (instalación local, un dispositivo). El
"rollback" de la app es **reinstalar el build bueno conocido**:

1. Hacer checkout del commit iOS estable previo (el último validado en dispositivo).
2. Re-ejecutar la instalación:
   ```bash
   bash ios/scripts/install-app.sh
   ```
3. Validar en el iPhone: login → auto-login al reabrir → logout.

Notas:

- Al ser un único dispositivo del propietario, el impacto de un build iOS defectuoso está
  **contenido** (no hay base de usuarios). La reinstalación es inmediata.
- Si el fallo del login nativo viene de D-01 (no de la app), el rollback efectivo es el del
  **Canal 1** (backend), no reinstalar la app.

## Limitaciones conocidas (heredadas del stack)

- El estado en memoria (`TaskManager`, syncs en curso) se **pierde** en cada redeploy/rollback del
  backend: limitación aceptada del entorno único. Los syncs en curso se relanzan tras el rollback.
- Sin staging: la verificación de release es el smoke `/health` (backend) y la validación manual en
  dispositivo (iOS).
- DR multi-región / backup gestionado: **diferido** (serían de pago; NO-APLICA a coste 0 €). El RPO
  del backend está acotado por los datos persistidos en Neon.

## Post-rollback

- Abrir un PR con el fix real (nunca push directo a `main`); el gate de CI debe pasar antes de
  fusionar.
- Registrar el incidente y la causa raíz.

## Sources

- [consumes] cd-config.md, deployment-strategy.md.
- [code] `docs/ROLLBACK.md` (reutilizado), `ios/scripts/install-app.sh`, `.github/workflows/fly-deploy.yml`.
- [memory] phases/operation.md (rollback obligatorio, smoke/health); aidlc-shared/operation-fly-stack.md
  (rollback manual flyctl, limitaciones); project.md (coste 0 €).

## Assumptions & Open Questions

None.
