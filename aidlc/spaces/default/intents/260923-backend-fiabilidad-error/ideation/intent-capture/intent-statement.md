# Intent Statement — Fiabilidad backend: manejo de errores + contratos de integración

## Problem Statement

El backend de `futmondo-analytics` captura errores de forma demasiado amplia:
la revisión midió **194 capturas amplias** (7 `bare-except` + 187
`except Exception`), muchas con `pass`, que enmascaran fallos. [Q1] Un sync puede
"terminar bien" habiendo tragado un error y un baneo/entrada fallida de una
integración externa puede dejar la base de datos en estado inconsistente sin que
nadie se entere. [desc][Q1] El intent ataca la **fiabilidad general del backend**
en tres frentes acoplados: fallos silenciosos, corrupción de datos y diagnóstico
lento. [Q1]

Deriva del plan de mejoras (`docs/BACKLOG-plan-intents.md`) como **Intent 1**,
cubriendo los requisitos **FR3.2** (reducir `except Exception`/bare-except,
empezando por los `except: pass` de arranque y migraciones, distinguiendo error
recuperable de fatal) y **FR4** (robustez de integraciones externas: contratos y
modos de fallo de Sofascore y Futmondo; detección de baneo/entrada fallida
reflejada en el estado sin corromper datos). [desc]

## Target Customer

- **Operador / mantenedor único**: hoy es quien depura los fallos silenciosos y
  limpia los datos corruptos a mano; pierde tiempo diagnosticando a ciegas. [Q2][Q8]
- **Usuarios finales de la PWA**: ven datos incoherentes o desactualizados
  (presupuesto, mercado, finanzas) cuando un sync falla a medias. [Q2]

El beneficio es doble: proteger la integridad de datos de cara al usuario y
ahorrar al operador el trabajo de depuración manual. [Q2]

## Success Metrics

La definición de "hecho" combina las tres métricas, cada una verificable con
specs significativas: [Q3]

| Métrica | Criterio observable | Fuente |
|---|---|---|
| Reducción de broad-except | Bajar los `except Exception`/bare-except desde 194 en la primera oleada (arranque + migraciones + `db_connection.py`), con cada captura restante justificada como recuperable o fatal | [Q3][Q4] |
| Detección reflejada en estado | Ante baneo de Sofascore o entrada fallida de Futmondo, el sync marca el paso como `degraded`/fallido (no `ok`) y no escribe datos parciales corruptos | [Q3][Q5][Q6] |
| Contratos documentados | Existe documentación de los contratos y modos de fallo esperados de Sofascore (API no oficial vía `curl_cffi`, baneo de IP) y Futmondo (endpoints heterogéneos) | [Q3][Q5][desc] |

Semántica de error objetivo: un fallo **recuperable** (paso no crítico) marca
`degraded` y el sync continúa; un fallo **fatal** (BD caída, baneo total) aborta
limpio sin dejar datos a medias y lo refleja en el estado. [Q6]

## Initiative Trigger

Continuación natural del eje de fiabilidad (AX3): FR3.1 (pasos non-critical
visibles del sync) ya está cerrado y este es el siguiente paso lógico del mismo
eje y las mismas zonas de código, según el plan de intents. [Q7][desc]

## Initial Scope Signal

- **Scope seleccionado por el flujo**: `feature` (workflow-selected). [scope]
- **Límite de producto confirmado por el usuario**: `feature` — intervención
  acotada y aditiva sobre manejo de errores y contratos de integración, con
  specs significativas y el ciclo estándar; hay diseño real que hacer (taxonomía
  recuperable/fatal, contratos + detección), por lo que un scope menor
  (`bugfix`/`refactor`) se quedaría corto. [Q10]

**Frontera de alcance para FR3.2 en este intent** (acotada para no ampliar los
god-files): primera oleada de `except: pass` de arranque (`main.py`) y
migraciones (`scripts/migrate_*`), más la capa `db_connection.py` (9 capturas)
por ser crítica para la integridad; las 29 capturas de `data_sync_service.py`
quedan como deuda registrada salvo los puntos concretos donde un fallo silencioso
corrompe datos. [Q4][memory:M1]

**Entregable de FR4**: documentación de contratos/modos de fallo **y** el código
que detecta baneo/entrada fallida y lo refleja en el estado del sync sin escribir
datos corruptos. [Q5]

## Restricciones transversales

- Mantener el stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin
  reescrituras grandes; código nuevo tras una capa/función estrecha testeable;
  NO ampliar los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni el
  patrón SQL-en-router. [desc][memory:M1]
- Test-after con specs significativas; gate de CI bloqueante (gitleaks + `pytest`
  + `ng test`) antes de fusionar a `main`. [desc][memory:M2]
- Coste 0 € (solo tiers gratuitos: Neon free, Fly.io free allowance, GitHub
  Actions free). [desc][memory:M3]

## Assumptions & Open Questions

None.
