# Observability Setup Questions — Durabilidad del estado

> Etapa Observability Setup (Operation). Ejecución ligera a coste 0 € (Fly.io + Neon tier gratuito;
> sin CloudWatch/X-Ray ni herramientas de pago). Se documenta la observabilidad viable de las señales
> nuevas de durabilidad con las herramientas gratuitas disponibles, y se marca como no-aplica lo que
> exigiría infraestructura de pago. No se abren preguntas nuevas: el enfoque está decidido por el
> mandato de coste y el stack real.

## Contexto resuelto (no requiere pregunta)

- **Herramientas disponibles (coste 0 €)**: healthcheck `/health` (Fly.io check), `fly logs`
  (logs en tiempo real / recientes), smoke test del pipeline. Sin CloudWatch, X-Ray, Grafana de pago,
  ni APM.
- **Señales nuevas de durabilidad a vigilar**: fallos de rehidratación/descifrado de sesión
  (`FUTMONDO_CRED_KEY` ausente/rotada), tasa de 401 accionables tras reinicio (FR1.3), tareas
  marcadas `interrupted_by_restart` al arranque (FR1.5), errores de persistencia (`TaskPersistenceError`,
  `TaskConflictError`).
- **No-aplica a coste 0 €**: SLO formales con burn-rate multi-ventana, tracing distribuido (X-Ray),
  anomaly detection con ML. Se documentan como diferidos con la alternativa gratuita.
- **NFR2 (rendimiento)**: sin umbral numérico; observación por logs, no SLO formal.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
