# Dashboards — Durabilidad del estado (coste 0 €)

> Etapa Observability Setup (Operation). Enfoque de visibilidad viable en Fly.io + Neon (tier
> gratuito) sin herramientas de pago. No hay dashboards de CloudWatch/Grafana de pago; la visibilidad
> se apoya en el dashboard nativo de Fly.io y en consultas de logs (`log-queries.md`).

## Señales de las cuatro señales de oro (adaptadas a Fly.io free)

| Señal | Fuente disponible (coste 0 €) | Nota |
|-------|-------------------------------|------|
| Latencia | Métricas nativas de Fly.io (dashboard de la app) + logs de acceso | Sin percentiles automáticos; observación cualitativa |
| Tráfico | Fly.io metrics (requests) | — |
| Errores | `fly logs` filtrando por nivel ERROR / códigos 401/409/5xx | Ver `log-queries.md` |
| Saturación | Fly.io metrics: CPU / memoria (256 MB por máquina) | Vigilar memoria tras el deploy de durabilidad |

## Panel de durabilidad (observación por logs, sin dashboard de pago)

Señales nuevas que conviene revisar periódicamente vía `fly logs` (comandos en `log-queries.md`):

- **Rehidratación de sesión (FR1.2)**: eventos de sesión reconstruida tras reinicio vs fallos de
  descifrado (`FUTMONDO_CRED_KEY` ausente/rotada).
- **401 accionables tras reinicio (FR1.3)**: recuento de 401 (esperado tras rotación de clave o si el
  secret falta; anómalo si es sostenido con la clave presente).
- **Tareas interrumpidas por reinicio (FR1.5)**: recuento de tareas marcadas `interrupted_by_restart`
  al arranque (un pico correlaciona con un redeploy).
- **Conflictos de tarea (FR1.6)**: recuento de 409 en `/trigger`.

## Herramienta nativa

- **Dashboard de Fly.io** (`https://fly.io/apps/futmondo-api`): CPU, memoria, requests, estado de
  máquinas y healthchecks — incluido en el tier gratuito, sin configuración adicional.
- **`fly status --app futmondo-api`**: estado de máquinas y checks desde CLI.

## No-aplica a coste 0 € (diferido)

Un dashboard dedicado con percentiles de latencia por journey, error budget y burn-rate requeriría
CloudWatch/Grafana de pago o un stack de observabilidad autogestionado — fuera del mandato de coste
0 €. Si el proyecto graduara a un tier de pago, este panel se formalizaría (ver `slo-config.md`).
