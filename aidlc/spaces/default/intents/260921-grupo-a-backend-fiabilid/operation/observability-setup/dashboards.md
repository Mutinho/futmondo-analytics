# Dashboards — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack** (regla de `project.md`):
> stack real Fly.io + Neon, coste 0 €. NO se provisionan dashboards gestionados
> (CloudWatch/Grafana Cloud son de pago).

## Enfoque a coste 0 €

No hay dashboards gestionados. La "vista" operativa se obtiene con herramientas
gratuitas ya disponibles:

- `fly status --app futmondo-api` — estado de máquinas y checks.
- `fly logs --app futmondo-api` — flujo de logs (incl. el `logger.warning`
  estructurado de pasos `degraded`).
- `curl /health` — disponibilidad puntual.

## Panel lógico equivalente (qué mirar)

| "Panel" | Señal | Cómo obtenerla (gratis) |
|---|---|---|
| Disponibilidad backend | `/health` 200 | `curl https://futmondo-api.fly.dev/health`; job `smoke-test` post-deploy |
| Fiabilidad de la sync | pasos `degraded` | `fly logs` filtrando `sync step degraded` / `sync_step` |
| Rechazos de puja | 422 por techo `price` | `fly logs` filtrando la ruta `/market/bid` (opcional) |
| Salud de la app | reinicios/crashes | `fly status`, `fly logs` |

## NO-APLICA / diferido (servicios de pago)

- Dashboards gestionados (CloudWatch, Grafana Cloud), widgets de métricas con
  retención larga: se difieren; su equivalente gratuito son las consultas de
  `fly logs` documentadas en `log-queries.md`.

## Sources

- `operation/deployment-execution/health-check-report.md`,
  `construction/sync-reliability/functional-design/functional-spec.md` (FS1 log
  estructurado), `project.md` (adaptación de stack + coste 0 €).

## Assumptions & Open Questions

None.
