# SLO Compliance Report — Durabilidad del estado (coste 0 €)

> Etapa Feedback & Optimization (Operation). Reporte de cumplimiento de nivel de servicio. No hay SLO
> formal (diferido en `slo-config.md` por el mandato de coste 0 € y NFR2 sin umbral); se reporta el
> estado cualitativo disponible.

## Estado: sin SLO formal — señal de salud cualitativa

- **Disponibilidad**: verificada por el healthcheck `/health` de Fly.io (auto-restart ante 3 fallos)
  y el smoke test del pipeline. No se compromete un porcentaje numérico (no se mide continuamente a
  coste 0 €).
- **Error budget / burn-rate**: NO-APLICA (sin SLO formal ni sistema de métricas de pago).

## Señales de durabilidad (revisión por logs)

Estado esperado tras el despliegue de la durabilidad (a verificar en producción vía `fly logs`):

| Señal | Estado esperado |
|-------|-----------------|
| Rehidratación de sesión (FR1.2) | Sesiones reconstruidas tras reinicio con `FUTMONDO_CRED_KEY` fijado |
| 401 accionables (FR1.3) | Solo tras rotación de clave o secret ausente; no sostenidos con clave presente |
| Tareas interrumpidas (FR1.5) | Picos correlacionados 1:1 con redeploys; no espontáneos |
| Conflictos 409 (FR1.6) | Esperados cuando ya hay tarea activa; relanzables si interrumpida |

## Recomendación

- Para obtener un SLO real a coste 0 €, primero fijar el umbral NFR2 (ver `feedback-loop.md`) y luego
  derivar SLI/SLO. Hasta entonces, la salud se juzga cualitativamente por healthcheck + logs, lo cual
  es proporcionado a un proyecto personal de bajo volumen.
