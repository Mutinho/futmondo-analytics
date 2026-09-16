# Feedback & Optimization Questions — Durabilidad del estado

> Etapa final (Operation). Adaptada al stack real (Fly.io + Neon, coste 0 €): AWS Cost Explorer /
> Config / Trusted Advisor no aplican. Se consolidan las mejoras de seguimiento reales identificadas
> durante el flujo y se cierra el bucle de feedback hacia un próximo intent. No se abren preguntas
> nuevas: el contexto está resuelto por los artefactos previos.

## Contexto resuelto (no requiere pregunta)

- **SLO**: sin SLO formal (diferido en slo-config, coste 0 €); estado cualitativo por healthcheck + logs.
- **Coste**: 0 € — la durabilidad no añade recursos de pago; free allowance de Fly.io/Neon/GH Actions
  cubre el cambio.
- **Drift**: sin herramienta de drift automatizada de pago. Nota menor conocida: `backend/fly.toml`
  fija región `cdg` mientras `docs/DEPLOY.md` menciona `mad` (documentación desalineada, no drift de
  infraestructura activa; fly.toml es la fuente de verdad).
- **Mejoras de seguimiento reales** (para el bucle de feedback / próximo intent):
  - R-01 (u2): cerrar la ventana no-atómica SELECT→INSERT en `/trigger` con índice único parcial (NFR5).
  - `verify` de `fly-deploy.yml`: replicar `--cov` (paridad con gate de MR) — referencia informativa.
  - Fijar umbral numérico NFR2 y ejecutar el load-test-plan (coste 0 € con máquina Fly one-shot).
  - Logging estructurado (event=...) para observabilidad por logs fiable.
  - Endurecer ruff/ESLint de advisory a bloqueante tras un formateo inicial aislado.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
