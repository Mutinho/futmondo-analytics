# Alarms — Durabilidad del estado (coste 0 €)

> Etapa Observability Setup (Operation). Alertas viables en Fly.io + Neon (tier gratuito) sin
> herramientas de pago. La alerta primaria automatizada disponible a coste 0 € es el healthcheck de
> Fly.io + el smoke test del pipeline; el resto son revisiones manuales de logs (no automatizadas).

## Alertas automatizadas disponibles (coste 0 €)

| Alerta | Mecanismo | Severidad | Acción |
|--------|-----------|-----------|--------|
| Backend caído | Healthcheck `/health` de Fly.io (30s/5s) → Fly reinicia la máquina | Crítica | Auto-restart por Fly.io; el operador revisa `fly logs` si persiste |
| Release fallido | Smoke test `/health` del pipeline (5 reintentos, 200) → job falla, deploy no completa | Crítica | El deploy no se marca OK; operador investiga |
| Arranque fallido | El guard `JWT_SECRET` no-default aborta el arranque (NFR1.1) → healthcheck falla | Crítica | Fijar secret correcto y redeploy |

## Alertas por revisión de logs (manual, coste 0 €)

Sin un sistema de alerting de pago, estas señales se revisan manualmente vía `fly logs`
(comandos en `log-queries.md`), p. ej. tras un redeploy o ante un reporte de usuario:

| Señal | Cuándo revisar | Interpretación |
|-------|----------------|----------------|
| Fallos de descifrado de sesión | Tras rotar `FUTMONDO_CRED_KEY` o si usuarios reportan re-login inesperado | Clave rotada/ausente → handles invalidados (esperado tras rotación) |
| Pico de 401 tras reinicio | Tras un redeploy | Esperado si el secret falta; anómalo si es sostenido con clave presente |
| `TaskPersistenceError` | Ante errores de sync | Problema de conexión a Neon o esquema |

## Umbrales

- **Healthcheck**: HTTP 200 en `/health`; 3 fallos consecutivos (interval 30s) → Fly reinicia.
- No hay umbrales de error-rate automatizados (requeriría alerting de pago).

## No-aplica a coste 0 € (diferido)

Alarmas compuestas, alerting por error-rate/burn-rate y paginación on-call automatizada requieren
CloudWatch Alarms/PagerDuty u equivalente de pago. Diferido; la alternativa gratuita es el healthcheck
+ revisión manual de logs descrita arriba. Para un proyecto personal de un solo operador, no hay
rotación on-call (ver `incident-response`).
