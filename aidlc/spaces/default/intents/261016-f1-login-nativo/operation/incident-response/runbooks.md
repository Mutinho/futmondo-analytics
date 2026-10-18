# Runbooks — F1: Login nativo end-to-end

> Fase: operación (incident-response). Perspectiva de operations engineer. Idioma: castellano;
> comandos y rutas verbatim en inglés. Sin SSM Automation / AWS Incident Manager / AWS Backup (de
> pago): los runbooks son **procedimientos manuales con `flyctl`** sobre el stack Fly.io + Neon.
> Coste 0 €, single-maintainer. Reutilizan `docs/ROLLBACK.md`.

## Modos de fallo probables de F1 y su runbook

### RB-1 — Backend caído / `/health` != 200

1. Confirmar: `curl -sS https://futmondo-api.fly.dev/health` (espera 200 `{"status":"healthy"}`).
2. Estado: `fly status --app futmondo-api`; logs: `fly logs --app futmondo-api`.
3. Si el fallo viene de un deploy reciente → **rollback** (RB-4 / `docs/ROLLBACK.md`).
4. Si persiste: `fly machine restart` (o `fly machine stop` mientras se diagnostica).

### RB-2 — Login nativo falla (`POST /auth/login`)

1. Reproducir desde la app (iPhone) y revisar `fly logs ... | grep "/auth/login"`.
2. Distinguir causa:
   - **Credencial inválida** (401): esperado, no es incidente.
   - **5xx / excepción**: incidente; revisar `Traceback` en logs (sin exponer credenciales).
   - **Falta `refresh_token` en el body**: regresión de D-01 → ver RB-3.
3. Si es regresión de D-01 introducida por un deploy → rollback (RB-4).

### RB-3 — Refresh falla (`POST /auth/refresh`) / auto-login no funciona

1. Revisar `fly logs ... | grep "/auth/refresh"`.
2. Verificar la precedencia del transporte (cookie → header `X-Refresh-Token` → body): un cambio
   que rompa la resolución del token rompe el auto-login nativo.
3. Si el backend dejó de aceptar el refresh token por header/body (p. ej. rollback a pre-D-01), la
   app degrada a "requiere re-login" — comportamiento seguro, sin corrupción. Rehabilitar
   redeployando la versión con D-01.

### RB-4 — Rollback de release (reutiliza `docs/ROLLBACK.md`)

1. `fly releases --app futmondo-api` → anotar la última release sana `vN`.
2. `fly releases rollback <vN> --app futmondo-api` (o redeploy explícito de la imagen previa).
3. Verificar: `curl -sS https://futmondo-api.fly.dev/health`.
4. Abrir PR con el fix real (nunca push directo a `main`); el gate de CI debe pasar.

### RB-5 — Incidente de la app iOS (no del backend)

1. Si el fallo es solo en la app (no en `/auth/*`), **reinstalar el build bueno previo**:
   `bash ios/scripts/install-app.sh` tras checkout del commit iOS estable.
2. Si la firma caducó (~7 días), re-ejecutar el script refresca la firma. Impacto contenido (un
   dispositivo, el del propietario).

## Seguridad en el manejo de incidentes

- NUNCA volcar el refresh token, el access token ni el password del usuario en logs, tickets ni
  notas de incidente (guardarraíl durable). Capturar solo status/endpoint/`reason`.

## Sources

- [consumes] alarms.md, dashboards.md (operation/observability-setup).
- [consumes] reliability-design.md, security-design.md, infrastructure-specification.md — NO
  existen (nfr-design/infrastructure-design `skipped`); derivado de la app desplegada.
- [code] `docs/ROLLBACK.md`, `ios/scripts/install-app.sh`, `.github/workflows/fly-deploy.yml`.
- [memory] phases/operation.md (runbooks con escalado); aidlc-shared/operation-fly-stack.md
  (SSM/Backup → rollback manual flyctl); project.md (coste 0 €, no credenciales en logs).

## Assumptions & Open Questions

None.
