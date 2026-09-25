# Observability Setup — Preguntas · Operación (FR3.2 + FR4)

Sin preguntas abiertas. La estrategia de observabilidad ya está decidida en
`nfr-design/observability-design.md` y `infrastructure-design/monitoring-design.md`
(fase Construcción, aprobadas): señales, formato de log, SLI informal y qué queda
NO-APLICA a coste 0 €. Esta etapa sólo la implementa a nivel de Operación
(consultas `fly logs`) y documenta los equivalentes gratuitos.

## Decisiones ya tomadas (no se re-preguntan)

- **Golden signals** (adaptados a batch/sync + coste 0 €): salud `/health`;
  aparición de pasos `DEGRADED` inesperados; fallos fatales (`ERROR`); estado de
  los crons.
- **SLI/SLO**: SLI informal (sin `DEGRADED` inesperado + no-corrupción); **SLO
  formal con burn-rate → NO-APLICA/diferido** (de pago).
- **Logs**: clave=valor en una línea (`sync_step`, `failure_mode`, `status`,
  `endpoint`, `task_id`, `reason`), WARNING recuperable / ERROR fatal; plano de
  consulta = `fly logs` + `grep`. Sin credenciales (NFR3).
- **Tracing distribuido / dashboards gestionados / anomaly detection ML** →
  NO-APLICA (de pago).

## Assumptions & Open Questions

None.

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
