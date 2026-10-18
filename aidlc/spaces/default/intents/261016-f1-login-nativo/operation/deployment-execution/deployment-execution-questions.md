# Deployment Execution — Preguntas y confirmación — F1: Login nativo end-to-end

> Fase: operación (deployment-execution). Idioma: castellano; tokens técnicos verbatim en inglés.

## Pre-deployment checks

- **¿Checks previos en verde?** Sí: gate de CI bloqueante verde antes del merge del backend
  (gitleaks + pip-audit + `ruff check` + `pytest` 422 + `npm audit` + `ng test`); `swift test` 29
  passed antes de instalar la app iOS.
- **¿Migraciones de BD requeridas/probadas?** No: D-01 no incluye migraciones.
- **¿Servicios dependientes sanos?** Sí: Neon alcanzable (confirmado por `/health` 200).
- **¿Ventana de despliegue?** Sin ventana formal (single-maintainer, entorno único, on-merge).

## Consolidated Summary Confirmation

Resumen de lo producido en deployment-execution para F1 (despliegue ya ejecutado y validado):

- **deployment-log.md**: backend D-01 desplegado por el CD on-merge a Fly.io (cadena
  `verify → deploy-backend → deploy-frontend → smoke-test`, commit `f5a51f44`); app iOS instalada
  en el iPhone 13 Pro por firma gratuita con `xtool`. Sin migraciones de BD. Publicación App Store
  diferida (B-09).
- **smoke-test-results.md**: smoke `/health` del CD en verde; verificación en vivo adicional
  2026-10-18 (HTTP 200 `{"status":"healthy"}`, 0.47 s); smoke funcional de auth contra prod (login
  → auto-login vía Keychain → logout) en verde; PWA sin regresión por precedencia cookie-primero.
- **health-check-report.md**: backend/frontend/Neon/app iOS sanos; SLI informal (sin SLO de pago);
  rollback disponible pero no necesario.
- **Adaptación al stack (coste 0 €)**: observabilidad por `fly status`/`fly logs`/`/health`;
  alarmas/dashboards gestionados de pago marcados NO-APLICA. Smoke E2E de dispositivo es manual
  (deuda P-1 registrada), no bloquea F1. No se inventa infraestructura.

¿Es todo correcto?

[Answer]: Looks correct
