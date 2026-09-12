# Domain Design — Preguntas

## Sources

- [desc] Initial description: "Analizar el proyecto completo futmondo-analytics (arquitectura, codigo, infraestructura) e identificar mejoras y puntos criticos-debiles para abordarlos en futuros intents; generar un plan"
- [scope] Workflow-selected scope: `analysis-plan`.

## Q1. En un intent de análisis (no se crean componentes nuevos), ¿cómo quieres el catálogo de componentes (components.md)?

- A. Reflejar la arquitectura ACTUAL: los componentes reales del proyecto (frontend, backend y sus subsistemas: auth, data services, integration clients, api endpoints, task manager, cron, proxy) tal como existen, con sus dependencias — como base sobre la que se apoyan las mejoras.
- B. Además de reflejar la arquitectura actual, anotar en cada componente qué requisitos de mejora (FR) le afectan, de modo que el catálogo sirva de mapa "dónde toca cada mejora".
- C. Solo un diagrama de bloques ligero, sin detalle de entidades.
- X. Other (please specify)

[Answer]: B. Reflejar la arquitectura ACTUAL (componentes reales + dependencias) y anotar en cada componente qué requisitos de mejora (FR) le afectan, como mapa "dónde toca cada mejora"

## Q2. ¿Sobre qué decisiones quieres ADRs (decisions.md)?

Los ADRs documentarán las decisiones de arquitectura del PLAN de mejoras (no implementaciones), con contexto/decisión/consecuencias/alternativas.

- A. Las decisiones estructurales de fondo que el plan recomienda: p. ej. persistir el estado de sync (FR1), hacer transaccional la caché Sofascore (FR2), no guardar credenciales en claro (FR5), podar el multi-backend de BD hacia Neon único (FR14), y cómo abordar los god files (FR13). Cada una con alternativas.
- B. Solo las más críticas (FR1, FR2, FR5).
- C. Todas las anteriores + una ADR sobre el enfoque conservador/incremental global del plan.
- X. Other (please specify)

[Answer]: C. ADRs para las decisiones estructurales de fondo (FR1 persistir sync, FR2 caché transaccional, FR5 credenciales, FR14 podar multi-backend BD, FR13 god files) + una ADR sobre el enfoque conservador/incremental global del plan

## Q3. Para el mapeo de trazabilidad (traceability.json): ¿mapear cada FR al componente que le corresponde?

- A. Sí: mapear cada requisito de mejora (FR1–FR18) al componente actual donde se abordará. Los que sean transversales (CI/CD, config) se mapean al componente/área correspondiente o se marcan como transversales.
- B. Solo mapear los críticos.
- X. Other (please specify)

[Answer]: A. Mapear cada requisito de mejora (FR1–FR18) al componente actual donde se abordará; los transversales (CI/CD, config) al área correspondiente o marcados como transversales

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
