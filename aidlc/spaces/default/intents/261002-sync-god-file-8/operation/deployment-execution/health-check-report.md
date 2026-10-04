# Health Check Report — Sync Domain Decomposition (Fly.io + Neon)

Validación de salud del release, adaptada al stack real Fly.io + Neon a coste 0 €
(ver `operation-fly-stack.md`). El conocimiento del stage asume AWS/CloudWatch;
aquí se mapea a las herramientas gratuitas disponibles y se marca como
NO-APLICA/diferido lo que exige servicios de pago.

## Fuentes

- `operation/deployment-execution/deployment-log.md`, `smoke-test-results.md`
- `operation/deployment-pipeline/deployment-strategy.md`, `rollback-runbook.md`
- `.github/workflows/fly-deploy.yml`
- Adaptación de stack: `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`

## Checks de salud (post-deploy on-merge)

| Check | Herramienta (gratuita) | Umbral / expectativa | Estado |
|-------|------------------------|----------------------|--------|
| Liveness backend | `GET /health` (job `smoke-test`) | HTTP 200 `{"status":"healthy"}`, 5 reintentos | Pendiente de merge |
| Liveness frontend | `GET /` (nginx, check Fly) | HTTP 200 | Pendiente de merge |
| Estado de máquinas | `fly status --app futmondo-api` | máquinas `started`, healthchecks `passing` | Verificación manual on-merge |
| Logs de sync | `fly logs --app futmondo-api` + `grep` | 10 pasos de sync producen el `SyncResult` esperado; sin pasos `degraded` inesperados | Verificación manual on-merge |
| Conectividad Neon | implícita en `/health` / primer sync | sin errores de conexión en `fly logs` | Pendiente de merge |

## SLI/SLO (adaptado, coste 0 €)

- **SLI informal**: `/health` = 200 + ausencia de pasos de sync `degraded`
  inesperados en `fly logs`.
- **SLO formal con burn-rate**: **NO-APLICA** — requiere observabilidad de pago;
  se documenta la alternativa gratuita (observación pull vía `fly status` /
  `fly logs`) en vez de inventar infraestructura.
- **Tracing distribuido / anomaly detection ML**: **diferido / NO-APLICA**
  (servicios de pago); correlación por log estructurado + `task_id` sustituye al
  tracing gestionado.

## Observaciones específicas del refactor

- Equivalencia estricta: la salud del servicio no debería variar respecto a la
  release previa; el refactor reorganiza código sin cambiar comportamiento
  observable ni características de runtime.
- La garantía de no-credenciales-en-logs (NFR5) se preserva en los adapters
  extraídos: `fly logs` no debe exponer password ni token Futmondo/Sofascore.
- Limitación aceptada: el estado en memoria (`TaskManager`, syncs en curso) se
  pierde en el redeploy; los syncs en curso se relanzan tras el deploy.

## Veredicto de readiness

**Listo para release on-merge.** Gate `verify` verde (suite 329 passed, cobertura
43.19% ≥ 27), sin migración, sin servicios dependientes nuevos, rollback
documentado. La validación de salud en vivo se completa cuando el merge dispara
el pipeline (`/health` 200 + `fly status`/`fly logs` sanos).
