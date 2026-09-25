# SLO Report — Feedback & Optimization (FR3.2 + FR4)

Informe de nivel de servicio del intent de fiabilidad, coherente con
`observability-setup/slo-config.md`. A coste 0 €, el reporte es cualitativo
(no hay métricas gestionadas de burn-rate).

## SLI observados (postura, no medición gestionada)

| SLI | Objetivo (informal) | Estado tras el intent |
|---|---|---|
| Ausencia de `DEGRADED` inesperado | los fallos recuperables se marcan y no rompen el sync | **Mejorado**: antes los fallos se enmascaraban (`None`/`except: pass`); ahora son visibles como `DEGRADED`/`ERROR` en `fly logs` |
| No-corrupción de datos | `team_prizes` todo-o-nada ante fallo | **Mejorado**: reemplazo transaccional atómico (antes el `DELETE ... NOT IN` tragaba el fallo y dejaba estado mixto) |
| Salud del release | `/health` = 200 tras deploy | Sin cambio (pipeline existente) |
| Señal de baneo | baneo Sofascore visible y no corrompe | **Mejorado**: `IntegrationBanError` fatal propagada + log `failure_mode=ban` |

## SLO formal

- **NO-APLICA / diferido**: SLO con burn-rate requiere métricas gestionadas de
  pago. Alternativa gratuita en uso: SLI informal por `fly logs` + healthcheck.

## Resultado del intent

El objetivo — que los fallos **no se enmascaren ni corrompan datos** — se cumple:
excepciones tipadas propagadas, taxonomía recuperable/fatal observable, y
no-corrupción verificada por spec. Cobertura de tests de fiabilidad añadida
(suite 203 passed).

## Assumptions & Open Questions

None.
