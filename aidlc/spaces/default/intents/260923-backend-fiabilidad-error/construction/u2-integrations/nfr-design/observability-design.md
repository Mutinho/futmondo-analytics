# Observability Design — u2-integrations (Integraciones)

Diseño de la observabilidad de los fallos de integración, derivado de
`observability-requirements.md` (NFR1.1–1.5). A coste 0 € sobre Fly.io: `fly logs`
+ `grep` como plano de consulta; sin agregador, dashboards ni tracing de pago.

Consume: `observability-requirements.md`, `functional-spec.md`, `reliability-requirements.md`.
Perspectivas inline: arquitecto + plataforma (Fly.io).

## Diseño de logging estructurado (NFR1.1–1.4)

- **Formato**: un helper de logging emite **clave=valor en una sola línea** con
  campos fijos: `sync_step`, `failure_mode`, `status`, `endpoint`, `task_id`,
  `reason`. Basado en el `logging` de la stdlib (sin dependencia nueva).
- **Niveles**: `WARNING` para fallo recuperable / paso `DEGRADED`; `ERROR` para
  fallo fatal (propagado).
- **Campos permitidos**: el helper recibe campos explícitos, nunca el objeto de
  request/credencial completo → garantiza NFR1.4 / NFR3.2 (sin credenciales).

```text
# ejemplo de línea de log (recuperable)
level=WARNING sync_step=transactions failure_mode=timeout status= endpoint=/getTransactions task_id=abc123 reason="read timeout after 30s"
# ejemplo (fatal)
level=ERROR sync_step=sofascore failure_mode=ban status=403 endpoint=/ratings task_id=abc123 reason="IP banned"
```

## Correlación (NFR1.5)

- **`task_id`** es el correlador: todos los logs de un sync llevan el mismo
  `task_id`, de modo que `fly logs | grep task_id=<id>` reconstruye el hilo del
  sync entre pasos. El paso `DEGRADED` se registra vía `sync_step_status.py`
  (`StepStatus.DEGRADED`) y aparece con su patrón de campos.

## Pilares de observabilidad (adaptados a Fly.io)

| Pilar | Diseño | Estado |
|---|---|---|
| **Logs** | clave=valor estructurado, `fly logs` + `grep` | **Pilar principal (U2)** |
| **Métricas** | `fly status` + healthcheck `/health` existentes | Heredado; sin dashboards |
| **Trazas** | correlación por `task_id` en logs | Adaptado; tracing distribuido NO-APLICA |
| **Alerting** | síntomas (`ERROR`/`DEGRADED` inesperado) vía inspección + notificación de fallo de GitHub Actions | Single-maintainer; sin alerting de pago |

## SLI/SLO

- **SLI**: ausencia de `DEGRADED` inesperado + no-corrupción (heredado).
- **SLO formal con burn-rate**: **NO-APLICA/diferido** — requiere métricas
  gestionadas de pago; se documenta la alternativa gratuita (`fly logs`).

## Anti-patrones evitados

- No loguear credenciales (NFR3.2/NFR1.4).
- Alertar sobre síntomas (fallo fatal / DEGRADED inesperado), no sobre CPU.
- Correlación presente (`task_id`).

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- CloudWatch dashboards / X-Ray / anomaly detection ML / PagerDuty → NO-APLICA
  (de pago). Documentado, no inventado; equivalente gratuito = `fly logs` +
  `grep` + healthcheck.

## Assumptions & Open Questions

None.
