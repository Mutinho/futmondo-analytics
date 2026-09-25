# Intent Backlog — Fiabilidad backend (FR3.2 + FR4)

Proto-Units priorizados (MoSCoW), en orden dependencia-primero. Cada ítem es
aditivo, tras una capa/función estrecha testeable, sin ampliar los god-files. [Q2][Q3][memory:M1]

## Must Have

| ID | Proto-Unit | Descripción | Prioridad | Fuente |
|---|---|---|---|---|
| PU-1 | Taxonomía recuperable/fatal (capa de errores) | Definir e implementar la distinción recuperable→degradado / fatal→aborta-limpio; endurecer la primera oleada de broad-except de arranque (`main.py`) y migraciones (`scripts/migrate_*`) | Must | [Q1][Q3][desc] |
| PU-2 | Endurecimiento de `db_connection.py` | Sustituir capturas amplias/`pass` de la capa de conexión/arranque de BD por manejo recuperable/fatal (ya hace `rollback`+`raise` en transacciones; extender al resto) | Must | [Q1] |
| PU-3 | `futmondo_client.py` tipado y propagado | Eliminar el `return None` silencioso; excepciones tipadas por modo de fallo (timeout, respuesta heterogénea/no parseable), propagadas | Must | [Q1][Q2] |
| PU-4 | Detección de baneo/entrada fallida en estado | Ante baneo Sofascore / entrada fallida Futmondo, marcar el paso `degraded`/fallido vía `sync_step_status.py`, sin escribir datos parciales corruptos | Must | [Q1][Q2] |

## Should Have

| ID | Proto-Unit | Descripción | Prioridad | Fuente |
|---|---|---|---|---|
| PU-5 | Doc de contratos y modos de fallo | Documentar contratos y modos de fallo esperados de Sofascore (baneo IP, 403) y Futmondo (endpoints heterogéneos) | Should | [Q2][desc] |

## Could Have

| ID | Proto-Unit | Descripción | Prioridad | Fuente |
|---|---|---|---|---|
| PU-6 | Puntos de corrupción concretos en `data_sync_service.py` | Endurecer solo capturas puntuales de ese fichero donde un fallo silencioso corrompe datos, sin ampliar el god-file | Could | [Q2][memory:M1] |

## Won't Have (this time) — deuda registrada

| ID | Excluido | Destino | Fuente |
|---|---|---|---|
| WN-1 | Las 29 capturas completas de `data_sync_service.py` | Deuda / futura ronda | [Q6] |
| WN-2 | Resto de broad-except del backend fuera de la primera oleada | Deuda | [Q6] |
| WN-3 | Poda de config/Turso/SQLite muerta | Intent 2 | [Q6] |
| WN-4 | Descomposición de god-files | Intent 3 | [Q6] |

## Assumptions & Open Questions

None.
