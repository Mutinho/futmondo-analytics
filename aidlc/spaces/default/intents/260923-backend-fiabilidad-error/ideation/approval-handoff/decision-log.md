# Decision Log — Ideación (Fiabilidad backend FR3.2 + FR4)

Registro de decisiones tomadas durante la fase de Ideación. [scope]

## Intent Capture

| # | Decisión | Fuente |
|---|---|---|
| D-IC1 | Problema = fiabilidad general del backend (fallos silenciosos + corrupción + diagnóstico) | intent-capture Q1 |
| D-IC2 | Afectados = operador único + usuarios finales | intent-capture Q2 |
| D-IC3 | Éxito = las tres métricas juntas (reducir broad-except, detección en estado, contratos doc) | intent-capture Q3 |
| D-IC4 | Alcance FR3.2 = arranque + migraciones + `db_connection.py`; resto deuda | intent-capture Q4 |
| D-IC5 | FR4 = doc + detección en código reflejada en estado | intent-capture Q5 |
| D-IC6 | Semántica error: recuperable→degradado; fatal→aborta limpio | intent-capture Q6 |
| D-IC7 | Scope confirmado = `feature` | intent-capture Q10 |

## Feasibility

| # | Decisión | Fuente |
|---|---|---|
| D-FE1 | Patrón FR4 = excepción tipada por modo de fallo, propagada (extiende `SofascoreIPBanError`) | feasibility Q1 |
| D-FE2 | Estado = reusar/extender `sync_step_status.py` (FR3.1) | feasibility Q2 |
| D-FE3 | Sin marco regulatorio formal; controles de seguridad como restricciones internas | feasibility Q3 |
| D-FE4 | Stack fijo, sin dependencias de pago, coste 0 € | feasibility Q4 |
| D-FE5 | Incertidumbres a diseño: clasificar recuperable/fatal + punto de corte "no corromper datos" | feasibility Q7 |

## Scope Definition

| # | Decisión | Fuente |
|---|---|---|
| D-SC1 | Alcance = las dos patas completas (FR3.2 primera oleada + FR4) | scope-definition Q1 |
| D-SC2 | MoSCoW: Must (Futmondo tipado, detección en estado, primera oleada); Should (doc); Could (corrupción `data_sync_service`); Won't (resto) | scope-definition Q2 |
| D-SC3 | Dependencia: FR3.2 habilita FR4; secuencia dependencia-primero con corrupción priorizada | scope-definition Q3, Q4 |
| D-SC4 | Exclusiones explícitas: 29 capturas completas, resto broad-except, poda (Intent 2), god-files (Intent 3) | scope-definition Q6 |

## Etapas omitidas (con justificación)

| Etapa | Motivo |
|---|---|
| Market Research | Fiabilidad interna brownfield; sin posicionamiento de mercado ni build-vs-buy |
| Team Formation | Mantenedor único; sin composición de equipo ni mob |
| Rough Mockups | Backend-only; sin UI nueva de cara al usuario |

## Approval & Handoff

| # | Decisión | Fuente |
|---|---|---|
| D-AH1 | Intent y alcance confirmados | approval-handoff Q1 |
| D-AH2 | Riesgos reconocidos con mitigación aceptable | approval-handoff Q2 |
| D-AH3 | Compromiso de recursos = tiempo del mantenedor, coste 0 € | approval-handoff Q3 |
| D-AH4 | GO a Inception | approval-handoff Q4 |

## Assumptions & Open Questions

None.
