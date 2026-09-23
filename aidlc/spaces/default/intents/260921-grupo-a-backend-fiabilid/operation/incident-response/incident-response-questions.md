# Preguntas — Incident Response (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation. **Adaptación de stack** (regla
> de `project.md`): el stage asume SSM/AWS Incident Manager/AWS Backup; el
> proyecto real es Fly.io + Neon, **single-maintainer**, coste 0 €. Se documentan
> runbooks manuales con herramientas gratuitas (`fly`, `curl`, `fly logs`) y se
> marca NO-APLICA/diferido la automatización de pago. Respuestas determinadas por
> el proyecto real (Operation: preguntas excepcionales).

## Q1 — ¿Modos de fallo más probables (foco de este intent)?

A. (1) Release no sano (`/health` ≠ 200 tras deploy); (2) paso de sync `degraded` (prizes/phantoms); (3) rechazo de puja por techo/positividad; (4) BD Neon inaccesible
B. Otros
X. Other (please specify)

[Answer]: A. Los cuatro. Este intent hace observables (1)-(2)-(3); (4) es preexistente. El nuevo estado `degraded` con log estructurado convierte un fallo silencioso de sync en un incidente diagnosticable.

## Q2 — ¿Rutas de escalado y rotación de guardia?

A. Single-maintainer (sin rotación formal); el/la responsable del proyecto es el único punto de escalado
B. Rotación on-call multi-persona
X. Other (please specify)

[Answer]: A. Single-maintainer. No hay rotación on-call ni PagerDuty (coste 0 €). El escalado es "self": la señal (workflow en rojo / `/health` en rejo) llega por GitHub Actions y por comprobación manual.

## Q3 — ¿Remediación automatizada posible?

A. Mínima y gratuita: el gate `verify` impide desplegar en rojo; el `smoke-test` detecta un release no sano. Remediación (rollback) es MANUAL vía `flyctl`
B. Automatización avanzada (SSM/Lambda auto-remediation)
X. Other (please specify)

[Answer]: A. Remediación automatizada de pago NO-APLICA. La única "auto-remediación" es preventiva (el gate bloquea rojos). El rollback es manual (`rollback-runbook.md`).

## Q4 — ¿Procedimientos de comunicación durante incidentes?

A. Registro del incidente (causa raíz, timeline) en el repo/issue; sin canal de status page de pago
B. Status page + comms multi-canal
X. Other (please specify)

[Answer]: A. Registro en el repo (issue/nota de incidente); post-incidente documentado. Sin status page de pago. Al ser single-maintainer, la "comunicación" es la nota de incidente + el PR del fix.

## Q5 — ¿Objetivos RTO/RPO?

A. Informales: RTO ≈ tiempo de un redeploy de la release previa (minutos); RPO efectivo = último estado persistido en Neon (el estado en memoria se pierde en el redeploy — limitación aceptada)
B. RTO/RPO formales con SLA
X. Other (please specify)

[Answer]: A. Informales. RTO = duración de un `fly releases rollback` + verificación `/health` (minutos). RPO = datos en Neon (durables); el estado en memoria (TaskManager, syncs en curso) NO es durable y se pierde en el redeploy (limitación conocida, sin coste para resolverla en este intent).

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
