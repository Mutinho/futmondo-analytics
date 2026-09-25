# Dashboards — Observabilidad (FR3.2 + FR4)

Sin dashboards gestionados (CloudWatch / Grafana Cloud → de pago, **NO-APLICA**).
A coste 0 €, el "dashboard" operativo es:

| Vista | Herramienta (gratuita) |
|---|---|
| Estado de apps (running, versión, health) | `fly status --app futmondo-api` / `--app futmondo-app` |
| Salud del release | `curl -sS https://futmondo-api.fly.dev/health` → `{"status":"healthy"}` |
| Fallos de integración | `fly logs \| grep failure_mode=` (ver `log-queries.md`) |
| Estado de crons | pestaña Actions de GitHub (verde/rojo) |

## NO-APLICA (coste 0 €)

- CloudWatch dashboards / Grafana gestionado / paneles con widgets → NO-APLICA.
  Alternativa gratuita: `fly status` + `fly logs` + healthcheck. Documentado, no
  inventado.

## Assumptions & Open Questions

None.
