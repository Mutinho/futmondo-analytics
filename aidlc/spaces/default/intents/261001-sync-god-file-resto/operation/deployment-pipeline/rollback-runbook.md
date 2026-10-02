# Rollback Runbook — `261001-sync-god-file-resto`

> Mecanismo real: redeploy de la release anterior en Fly.io (`flyctl`). Runbook
> base: `docs/ROLLBACK.md`. Idioma: castellano.

## Disparadores de rollback

- Smoke test `/health` falla tras el deploy (el job `smoke-test` ya falla el
  workflow, señalando el problema).
- Error 5xx / caída del healthcheck observada en `fly status` / `fly logs`.
- Regresión funcional detectada en el dominio `clauses` (p. ej. un `SyncResult`
  distinto del congelado) — aunque la caracterización lo previene.

## Procedimiento (manual, coste 0 €)

1. Identificar la release previa sana:
   ```bash
   flyctl releases --app futmondo-api
   ```
2. Revertir a la release anterior:
   ```bash
   flyctl releases rollback <version> --app futmondo-api
   ```
   (equivalente para `futmondo-app` si el frontend estuviera afectado — en este
   intent el frontend no cambia).
3. Verificar `/health`:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://futmondo-api.fly.dev/health
   ```
   Esperar `200`.
4. Confirmar en `fly logs` que no hay pasos `degraded` inesperados en el sync.

## Consideraciones de datos

- Sin migración de esquema en este intent → rollback de código es seguro y no
  deja datos a medias.
- El estado en memoria (`TaskManager`, syncs en curso) se pierde en el redeploy
  — limitación aceptada ya documentada.

## Post-rollback

- Registrar el incidente y la causa raíz; abrir corrección antes de re-desplegar.
- Dado el characterization-first, una regresión del dominio implicaría un hueco
  en el test de caracterización: añadirlo antes de reintentar.

## Mapeo AWS → real

Rollback automático por CloudWatch alarms (AWS) → NO-APLICA; se sustituye por el
smoke test `/health` bloqueante + rollback manual `flyctl` (coste 0 €).
