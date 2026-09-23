# Preguntas — Feedback & Optimization (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation (última etapa). **Adaptación de
> stack** (regla de `project.md`): el stage asume AWS Cost Explorer/Config/
> Trusted Advisor; el stack real es Fly.io + Neon a coste 0 €. Se genera con
> herramientas gratuitas (`fly`, `fly logs`, panel Neon) y se marca
> NO-APLICA/diferido lo de pago. Respuestas determinadas por el proyecto real
> (Operation: preguntas excepcionales).

## Q1 — ¿Se cumplen los SLOs? ¿Burn rate del error budget?

A. Sin SLO formal (NO-APLICA burn-rate — servicio de métricas de pago); SLI informal cumplido: `/health` verde y sin `degraded` inesperados observados
B. SLOs formales con burn-rate
X. Other (please specify)

[Answer]: A. Sin SLO formal (diferido, ver `slo-config.md`). El SLI informal se cumple: `/health` 200 y, tras el intent, los pasos de sync que fallan se hacen visibles (`degraded`) en vez de enmascararse — mejora directa de la señal de fiabilidad (NFR1). No hay error budget cuantificado que quemar.

## Q2 — ¿Oportunidades de optimización de coste?

A. Ninguna con gasto; el proyecto ya está a coste 0 € (Neon free, Fly.io free allowance, GitHub Actions free) y el intent no añade coste
B. Optimizaciones identificadas
X. Other (please specify)

[Answer]: A. Ninguna acción de coste necesaria. El intent es aditivo y no añade recursos ni dependencias con gasto (el proveedor de cobertura de frontend, ajeno a este intent backend, ya es OSS). Se mantiene el mandato coste 0 €.

## Q3 — ¿Drift de configuración/infraestructura?

A. Sin drift introducido por el intent; sin IaC gestionada (Fly.io por `fly.toml`/CLI); NO-APLICA AWS Config
B. Drift detectado
X. Other (please specify)

[Answer]: A. Sin drift por el intent (no cambia infra ni `fly.toml`). NO-APLICA AWS Config drift detection (servicio de pago); la "config" vive en `fly.toml` versionado y en los secrets de Fly/GitHub.

## Q4 — ¿Patrones de uso que sugieran nuevas features o problemas?

A. Insight del intent: ahora se pueden detectar pasos de sync que fallan de forma recurrente (`degraded` en `fly logs`) — insumo para futuras mejoras de robustez de pasos concretos
B. Otros
X. Other (please specify)

[Answer]: A. El nuevo estado `degraded` genera datos de fiabilidad antes inexistentes: si un paso concreto (p. ej. `prizes`) aparece `degraded` con frecuencia, es señal para un futuro intent de robustez de ese paso. Insumo para el siguiente ciclo de Ideation.

## Q5 — ¿Toil operativo automatizable?

A. Mínimo; el rollback es manual por diseño (coste 0 €). Posible mejora futura diferida: paridad de cobertura `--cov` de backend en el job `verify` (deuda ya registrada)
B. Automatización propuesta ahora
X. Other (please specify)

[Answer]: A. El toil actual (rollback manual, inspección de `fly logs`) se mantiene por el mandato coste 0 €. Deuda diferida registrada como insumo del feedback loop: (1) paridad `--cov` backend en `verify`; (2) SAST/DAST frontend. No se aborda en este intent.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
