# SLO / SLI Configuration — Observabilidad (FR3.2 + FR4)

Coherente con `nfr-design/reliability-design.md` y `observability-design.md`.

## SLI informal (lo que sí se mide, gratis)

| SLI | Definición | Fuente |
|---|---|---|
| Ausencia de `DEGRADED` inesperado | ningún paso de sync `DEGRADED` fuera de lo esperado | `fly logs \| grep failure_mode=` |
| No-corrupción de datos | verificada por spec (todo-o-nada en `team_prizes`) | test `test_team_prizes_atomic_replacement.py` (por cambio, no runtime) |
| Salud del release | `/health` = 200 tras cada deploy | smoke test del pipeline |

## SLO formal

- **NO-APLICA / diferido**: un SLO formal con **burn-rate** requiere métricas
  gestionadas de pago (CloudWatch/Grafana SLO). Se documenta la alternativa
  gratuita (SLI informal por `fly logs` + healthcheck) en vez de inventar
  infraestructura.
- Los crons toleran un fallo puntual (reintento en la siguiente ejecución
  programada), por lo que un objetivo de disponibilidad porcentual formal no
  aporta a coste 0 € para un proceso batch.

## Assumptions & Open Questions

None.
