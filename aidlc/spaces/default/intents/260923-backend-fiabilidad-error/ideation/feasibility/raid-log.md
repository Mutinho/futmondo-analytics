# RAID Log — Fiabilidad backend (FR3.2 + FR4)

## Risks (Riesgos)

| ID | Riesgo | Prob. | Impacto | Mitigación | Fuente |
|---|---|---|---|---|---|
| R-1 | Regresión funcional al endurecer capturas: sustituir un `except Exception: pass` por manejo estricto rompe un flujo que hoy "funciona" tragando el error | Media | Alto | Characterization-first en las zonas tocadas; gate CI bloqueante (`pytest`) antes de merge | [Q6] |
| R-2 | Baneo real de Sofascore al ejercitar la detección de baneo en pruebas | Baja | Medio | Tests con dobles/mocks, sin red (patrón de los specs existentes); nunca golpear la API real en CI | [Q6] |
| R-3 | Clasificación errónea recuperable/fatal: marcar como recuperable algo que debía abortar (o viceversa), dejando datos a medias | Media | Alto | Diseño explícito de la taxonomía; punto de corte "no corromper datos" definido antes de codificar; specs por rama | [Q7] |
| R-4 | Alcance de FR3.2 se desborda hacia `data_sync_service.py` (god-file) al perseguir capturas | Media | Medio | Frontera fijada en intent-capture (arranque + migraciones + `db_connection.py`); resto como deuda; guardarraíl [memory:M1] | [memory:M1] |

## Assumptions (Suposiciones)

| ID | Suposición | Estado | Fuente |
|---|---|---|---|
| A-1 | FR3.1 (pasos non-critical visibles) está efectivamente entregado y `sync_step_status.py` es reusable como anclaje de estado | Asumido (verificado en código: helper presente) | [Q2] |
| A-2 | La stdlib de Python basta; no hace falta librería de reintentos/errores | Asumido | [Q4] |
| A-3 | No hay obligación regulatoria formal; los controles de seguridad son internos | Asumido | [Q3] |

## Issues (Incidencias abiertas)

| ID | Incidencia | Fuente |
|---|---|---|
| I-1 | `futmondo_client.py` traga excepciones y devuelve `None` (fallo silencioso) — es el anti-patrón que FR4 debe corregir | [Q1] |
| I-2 | Ramas muertas Turso/SQLite en `db_connection.py` mezcladas con las capturas a endurecer (poda pertenece a Intent 2, no a este) | [desc] |

## Dependencies (Dependencias)

| ID | Dependencia | Fuente |
|---|---|---|
| D-1 | Precedente FR2.1 (`SofascoreIPBanError`) y FR2 (reemplazo transaccional atómico) ya entregados: el patrón de fallo tipado y la no-corrupción se apoyan en ellos | [desc][Q1] |
| D-2 | Helper `sync_step_status.py` de FR3.1 como superficie de estado | [Q2] |
| D-3 | Gate de CI existente (gitleaks + `pytest` + `ng test`) para verificar sin regresiones | [desc] |

## Assumptions & Open Questions

None.
