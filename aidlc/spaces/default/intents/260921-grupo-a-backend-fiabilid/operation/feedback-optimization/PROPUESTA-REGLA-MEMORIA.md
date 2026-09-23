# Propuesta de regla de memoria — Unificación del contexto de Operation

> Conversation language: Spanish. **Borrador de propuesta**, NO es memoria
> activa. La memoria del espacio (`aidlc/spaces/default/memory/`) SOLO se escribe
> por el ritual de learnings (human-gated), que audita, deduplica y chequea
> conflictos. Esta etapa (feedback-optimization) no ofreció ese ritual en el
> scope `feature`, así que aquí queda como borrador para registrar en el próximo
> intent que active learnings, o para que el usuario lo afirme en un gate de
> practices-discovery.

## Contexto

Durante todo el intent `260921-grupo-a-backend-fiabilid`, las etapas de Operation
(4.1-4.7) repitieron el mismo patrón de adaptación, porque su conocimiento
embebido asume AWS y el stack real es otro. Unificar ese patrón como regla
persistente evita re-derivarlo intent a intent.

## Estado actual (ya persiste, parcialmente)

`project.md` → `## Corrections` ya contiene (learned 2026-09-16):

> "En etapas de Operation cuyo conocimiento asume AWS/CloudWatch, adaptar al
> stack real (Fly.io + Neon) y al mandato de coste 0 €: generar artefactos con
> las herramientas gratuitas disponibles (`fly logs`, healthcheck, logging
> estructurado) y marcar explícitamente como NO-APLICA/diferido lo que exige
> servicios de pago (SLOs formales con burn-rate, tracing distribuido, anomaly
> detection ML), documentando la alternativa gratuita en vez de inventar
> infraestructura inexistente."

Esa regla ya se cargó y aplicó en este intent. Es la base; la propuesta la
refuerza/amplía.

## Regla propuesta (para afirmar vía learnings)

Candidata a `## Corrections` de `project.md` (o `team.md` si el equipo la asume
como práctica general), redactada para el ritual:

- ALWAYS en fase Operation sobre este stack (Fly.io + Neon, single-maintainer,
  coste 0 €), mapear cada herramienta AWS del stage a su equivalente gratuito y
  marcar el resto NO-APLICA/diferido, usando esta tabla de referencia estable:
  - CloudWatch dashboards/metrics → `fly status` + `fly logs` + healthcheck `/health`.
  - CloudWatch Alarms / SNS / PagerDuty → gate `verify` bloqueante + `smoke-test`
    `/health`; escalado single-maintainer por notificación de GitHub Actions.
  - X-Ray / tracing distribuido → correlación por log estructurado + `task_id`.
  - CloudWatch Anomaly Detection (ML) → barreras deterministas (validación de
    entrada) + estados explícitos (`degraded`), no ML.
  - AWS Config drift → diff de git sobre `fly.toml` y workflows versionados.
  - Cost Explorer / Trusted Advisor → mandato coste 0 € (tiers gratuitos),
    verificado por diseño.
  - SSM Automation / AWS Backup / DR multi-región → diferidos; rollback manual
    `flyctl` + RPO = datos en Neon.

## Cómo materializar la unificación (para el usuario)

1. **Regla de memoria** (esta propuesta): afirmarla en el próximo intent cuyo
   ritual de learnings se ofrezca, o en practices-discovery. Se aplicará sola a
   todos los intents del espacio.
2. **Conocimiento de equipo reutilizable**: si se quiere el detalle completo como
   documento cargable por todos los intents, moverlo a
   `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (todos los
   agentes lo leen) o catalogarlo vía DocumentKB (`aidlc knowledge onboard`).
3. **Feedback loop**: ver `feedback-loop.md` de este intent, que ya recoge el
   backlog para el próximo ciclo.

## No hacer

- NO editar `org.md`/`team.md`/`project.md` a mano para "persistir" esto: saltaría
  el evento de auditoría, la deduplicación y el chequeo de conflictos del ritual.
