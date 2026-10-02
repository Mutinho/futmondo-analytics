# Health Check Report — `261001-sync-god-file-resto`

> Validación de salud post-deploy en el stack real (Fly.io + Neon, coste 0 €).
> Estado: **pendiente de disparo humano**. Idioma: castellano.

## Healthchecks vigentes

- Backend `futmondo-api`: healthcheck `/health` (puerto 8000). Fly.io reemplaza
  la máquina sólo si el nuevo release pasa el check.
- Frontend `futmondo-app`: healthcheck `/` (nginx).

## Validación esperada tras el deploy

| Señal | Herramienta (gratuita) | Esperado |
|-------|------------------------|----------|
| Estado de las apps | `fly status --app futmondo-api` | running, healthy |
| Health endpoint | smoke test `/health` (en el pipeline) | HTTP 200 |
| Logs de sync | `fly logs --app futmondo-api` | sin pasos `degraded` inesperados en `sync_clauses` |
| Equivalencia funcional | SLI informal | `SyncResult` de clauses idéntico al previo |

## Mapeo AWS → stack real

- CloudWatch dashboards/alarms (AWS) → NO-APLICA; sustituido por `fly status` +
  `fly logs` + healthcheck `/health` + smoke test bloqueante (observación pull,
  coste 0 €).
- SLO formal con burn-rate → diferido (de pago); SLI informal = `/health` 200 +
  ausencia de `degraded` inesperados.

## Estado

**PENDIENTE** — la validación se completa en el pipeline tras el push a `main`
del humano.
