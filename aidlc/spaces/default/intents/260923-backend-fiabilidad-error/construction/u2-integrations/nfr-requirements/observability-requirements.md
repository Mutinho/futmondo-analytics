# Observability Requirements — u2-integrations (Integraciones)

Observabilidad de los fallos de integración a coste 0 €, sobre el stack real
(Fly.io + `fly logs`, sin agregador de pago). Derivada de NFR1 (log estructurado)
y de la guía de adaptación Fly.io ya afirmada.

Consume: `functional-spec.md`, `rules.md`, `requirements.md`, `technology-stack.md`.
Perspectiva inline: QA (validación de observabilidad).

## Requisitos de observabilidad (derivados)

| ID | Requisito | Fuente | Verificación |
|----|-----------|--------|--------------|
| NFR1.1 | Cada fallo de integración (recuperable o fatal) emite un log estructurado **clave=valor en una línea** con: `sync_step`, `failure_mode`, `status` (si aplica), `endpoint` (no sensible), `task_id`, `reason`. | NFR1 | Spec que asvera los campos del log emitido |
| NFR1.2 | Nivel de log por clasificación: **WARNING** para fallo recuperable / paso `DEGRADED`; **ERROR** para fallo fatal (propagado). | NFR1, functional-design BR2.2/BR3.x | Spec que asvera el nivel por modo de fallo |
| NFR1.3 | El logging usa la stdlib de Python (`logging`); **sin dependencia nueva** (coste 0 €). | NFR5, práctica afirmada | Revisión de dependencias (sin alta en `requirements.txt`) |
| NFR1.4 | El log **nunca** incluye password ni token (ver security NFR3.2). | NFR3 | `gitleaks` + spec de ausencia de credenciales |
| NFR1.5 | Un paso `DEGRADED` es observable: se registra vía `sync_step_status.py` (`StepStatus.DEGRADED`) y queda visible en `fly logs` por su patrón de campos. | NFR1, FR4.4 | Spec de efecto (paso marcado DEGRADED) + grep-abilidad del patrón |

## Pilares de observabilidad (adaptados a Fly.io, coste 0 €)

- **Logs**: pilar principal. Estructurados clave=valor, consultables con `fly logs` + `grep` por `sync_step`/`failure_mode`/`task_id`. Sin agregador de pago.
- **Métricas**: `fly status` + healthcheck `/health` existentes; **sin dashboards de métricas** (CloudWatch/Grafana de pago → NO-APLICA).
- **Trazas**: correlación por `task_id` en los logs; **tracing distribuido → NO-APLICA/diferido** (de pago).

## Alerting

- **SLI informal** (ver reliability): la señal es la aparición de eventos `ERROR` (fatal) o de pasos `DEGRADED` inesperados en `fly logs`.
- **Sin alerting automatizado de pago** (PagerDuty/SNS → NO-APLICA). Escalado single-maintainer: notificación de fallo de GitHub Actions (crons/deploy) + inspección manual de `fly logs`.

## Anti-patrones evitados

- No loguear datos sensibles (credenciales/tokens) — NFR3.
- No alertar sobre causas (CPU) sino sobre síntomas (fallo fatal / DEGRADED inesperado).
- Correlación presente (`task_id`) para seguir un sync entre pasos.

## Assumptions & Open Questions

None.
