# Deployment Strategy — refactor DDD del asistente

Intent `260929-assistant-god-file`, scope `refactor` (Minimal). Estrategia de despliegue vigente,
documentada sin cambios (refactor sin cambio de comportamiento sobre un sistema en producción).

## Estrategia elegida: recreate/rolling gestionado por Fly.io (single-environment)

- **Mecanismo**: `flyctl deploy` construye y publica la imagen y sustituye las máquinas de cada app
  Fly.io (`futmondo-api`, `futmondo-app`). Fly.io gestiona el reemplazo de máquinas; el proyecto no
  configura blue/green ni canary explícitos.
- **Entorno único de producción** (sin staging separado). La verificación de release es el smoke
  test `/health` post-deploy (5 reintentos, HTTP 200).
- **Orden**: backend antes que frontend (`deploy-frontend` depende de `deploy-backend`), de modo
  que el nginx del frontend nunca apunta a un backend aún no desplegado.

## Por qué es la estrategia adecuada para este intent

- El refactor **no cambia el artefacto desplegado** (superficie pública idéntica vía shim), así que
  no hay riesgo de release nuevo que justifique canary/blue-green.
- **Compatibilidad de esquema**: el intent no toca esquema de BD (el `CREATE TABLE IF NOT EXISTS`
  idempotente se preserva en el adaptador); no hay migración destructiva que coordinar.
- **Coste 0 €**: blue/green duplica infraestructura y canary gestionado (CodeDeploy/Evidently) es
  AWS de pago — ambos NO-APLICA. El recreate/rolling de Fly.io es gratuito y suficiente.

## Gestión de migración de esquema

- **N/A** en este intent: sin cambios de esquema. El patrón de referencia para futuros cambios sería
  expand-contract (añadir columnas backward-compatible, backfill, contraer en release posterior),
  pero no aplica aquí.

## Estrategia de feature flags

- **Ninguna**. El proyecto no usa feature flags; AppConfig/Evidently son de pago (NO-APLICA por
  coste 0 €). El refactor no introduce comportamiento nuevo que requiera lanzamiento progresivo.

## Ventana de despliegue y consideraciones

- Despliegue continuo on-merge a `main` (single-maintainer); sin ventana de freeze formal.
- **Limitación aceptada**: el estado en memoria (`TaskManager`, sesiones de sync en curso) se pierde
  en cada redeploy — inherente al modelo de un único entorno; los syncs se relanzan tras el deploy.

## NO-APLICA (equivalentes AWS de pago)

- Blue/green (CodeDeploy ECS/Lambda), canary (`Canary10Percent5Minutes`), A/B testing (Evidently),
  rollback automático por CloudWatch alarms: sustituidos por recreate/rolling de Fly.io + smoke
  `/health` + rollback manual (`fly releases rollback`). Documentado en `rollback-runbook.md`.
