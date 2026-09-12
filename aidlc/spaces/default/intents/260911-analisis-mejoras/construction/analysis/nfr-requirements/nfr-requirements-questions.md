# NFR Requirements — Preguntas

## Sources

- [desc] Initial description: "Analizar el proyecto completo futmondo-analytics (arquitectura, codigo, infraestructura) e identificar mejoras y puntos criticos-debiles para abordarlos en futuros intents; generar un plan"
- [scope] Workflow-selected scope: `analysis-plan`.

## Q1. ¿Qué objetivos de disponibilidad/fiabilidad son realistas para este proyecto?

El proyecto corre en Fly.io free allowance (una máquina 256 MB, `min_machines_running=1`) con Neon free, mantenido por una persona. No hay SLA con usuarios.

- A. Objetivos modestos y honestos: ~99% (best-effort), sin multi-AZ ni failover automático; el foco de fiabilidad es NO perder estado (sync/sesión) ni datos, no un uptime alto.
- B. Objetivos exigentes (99.9%+) aunque impliquen redundancia (descartado si tiene coste).
- C. No fijar objetivos numéricos de uptime; solo requisitos cualitativos (durabilidad de datos, recuperación ante reinicio).
- X. Other (please specify)

[Answer]: A. Objetivos modestos y honestos (~99% best-effort, sin multi-AZ/failover); el foco de fiabilidad es no perder estado (sync/sesión) ni datos, no el uptime alto

## Q2. ¿Qué escala esperas (para dimensionar scalability y coste)?

- A. Muy pequeña y estable: 1 grupo de amigos, decenas de usuarios como mucho; sin crecimiento agresivo. El objetivo es no salir del tier gratuito.
- B. Podría crecer a varios grupos/campeonatos; conviene documentar el umbral que obligaría a salir del tier gratuito.
- C. No lo sé; asume el caso conservador (pequeño) y documenta umbrales.
- X. Other (please specify)

[Answer]: A. Escala muy pequeña y estable (grupo de amigos, decenas de usuarios); objetivo = no salir del tier gratuito. Documentar igualmente el umbral que obligaría a reconsiderar.

## Q3. Para observabilidad, dado coste 0€: ¿qué nivel es suficiente?

- A. Lo mínimo sostenible en gratis: logs estructurados de la app + el healthcheck /health existente + revisar logs de Fly; sin plataforma de observabilidad de pago.
- B. Además, definir métricas/alertas básicas si hay opción gratuita (p. ej. alertas por fallo de sync).
- C. No priorizar observabilidad en el plan (solo mencionarla).
- X. Other (please specify)

[Answer]: B. Mínimo sostenible en gratis (logs estructurados + /health + logs de Fly) + métricas/alertas básicas si hay opción gratuita (alerta por fallo de sync/despliegue)

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
