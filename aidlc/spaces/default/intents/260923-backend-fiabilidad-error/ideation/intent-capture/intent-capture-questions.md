# Intent Capture — Preguntas de aclaración

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "Intent 1 del plan de mejoras (docs/BACKLOG-plan-intents.md), derivado del intent de analisis 260911-analisis-mejoras: FR3.2 + FR4. FR3.2 - reducir los except Exception/bare-except (159+6) del backend, empezando por los except: pass de arranque y migraciones, distinguiendo error recuperable de fatal; continuacion natural de FR3.1 (ya hecho). FR4 - robustez de integraciones externas: documentar contratos y modos de fallo esperados de Sofascore (API no oficial via curl_cffi, baneo de IP) y Futmondo (endpoints heterogeneos); ante baneo/entrada fallida el sistema lo detecta, no corrompe datos (enlaza con FR2 ya hecho) y lo refleja en el estado. Scope feature, brownfield futmondo-analytics. Restricciones: mantener stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin reescrituras grandes, NO ampliar los god-files (data_sync_service.py, data_manager_v2.py) ni el patron SQL-en-router - el codigo nuevo va tras una capa/funcion estrecha testeable; test-after con specs significativas; gate de CI bloqueante (gitleaks + pytest + ng test) antes de merge a main; coste 0 EUR (tiers gratuitos). Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER ampliar los god-files existentes (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router."
- [memory:M2] `aidlc/spaces/default/memory/project.md#Mandated`: "ALWAYS pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción."
- [memory:M3] `aidlc/spaces/default/memory/project.md#Corrections`: "ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11)"

---

## Q1. Problema de negocio — ¿cuál es el dolor principal que resuelve este intent?

El backend tiene hoy ~194 capturas amplias de excepción (7 `bare-except` + 187 `except Exception`), muchas con `pass`, que enmascaran fallos: un sync puede "terminar bien" habiendo tragado un error, o un baneo de Sofascore puede corromper datos silenciosamente. ¿Cuál es el dolor que más te importa cerrar?

- A. **Fallos silenciosos**: hoy no me entero de que algo ha ido mal (un `except: pass` se come el error) hasta que veo datos incoherentes en la app.
- B. **Corrupción de datos**: un baneo/respuesta parcial de una integración externa deja la BD en estado inconsistente.
- C. **Diagnóstico lento**: cuando algo falla, no puedo saber qué paso ni por qué desde los logs / el estado del sync.
- D. **Las tres por igual** (fiabilidad general del backend).
- E. Not yet defined.
- X. Other (please specify)

[Answer]: D. Las tres por igual (fiabilidad general del backend).

## Q2. Cliente / usuario afectado — ¿quién sufre el problema?

Este es un proyecto de un solo mantenedor con usuarios finales de la PWA. ¿Sobre quién recae hoy el dolor?

- A. **Tú como operador/mantenedor**: eres quien depura los fallos silenciosos y limpia los datos corruptos.
- B. **Los usuarios finales de la app**: ven datos incoherentes o desactualizados cuando un sync falla a medias.
- C. **Ambos**: el operador pierde tiempo y los usuarios ven datos malos.
- D. Not identified.
- X. Other (please specify)

[Answer]: C. Ambos: el operador pierde tiempo y los usuarios ven datos malos.

## Q3. ¿Cómo se ve el éxito? — métricas medibles del intent

¿Qué resultado observable te haría decir "esto está hecho"? (puedes marcar la que mejor lo capture)

- A. **Reducción medible de broad-except**: bajar los `except Exception`/bare-except desde ~194, empezando por los `except: pass` de arranque/migraciones, con cada captura restante justificada (recuperable vs fatal).
- B. **Detección de baneo/fallo de integración reflejada en estado**: ante un baneo de Sofascore o entrada fallida de Futmondo, el sync marca el paso como `degraded`/fallido (no `ok`) y no escribe datos parciales corruptos.
- C. **Contratos documentados**: existe documentación de los contratos y modos de fallo esperados de Sofascore y Futmondo (qué devuelven, cómo fallan, cómo se detecta el baneo).
- D. **Las tres** como definición conjunta de hecho (con specs significativas que lo prueben).
- E. Not yet defined.
- X. Other (please specify)

[Answer]: D. Las tres como definición conjunta de hecho (con specs significativas que lo prueben).

## Q4. Alcance de FR3.2 — ¿hasta dónde llega la reducción de broad-except en ESTE intent?

Hay ~194 capturas amplias repartidas por todo el backend (29 solo en `data_sync_service.py`, 9 en `db_connection.py`). Reescribir las 194 sería una intervención enorme y chocaría con "sin reescrituras grandes" y con no ampliar los god-files [memory:M1]. ¿Qué recorte prefieres para este intent?

- A. **Solo la primera oleada segura**: `except: pass` de arranque (`main.py`) y migraciones (`scripts/migrate_*`), más los puntos donde un fallo silencioso corrompe datos; el resto queda como deuda registrada.
- B. **Primera oleada + `db_connection.py`**: añadir la capa de conexión/arranque de BD (9 capturas) por ser crítica para la integridad.
- C. **Toda la ruta de sync**: incluir `data_sync_service.py` (29) — mayor impacto pero roza el god-file (se haría solo endureciendo capturas existentes, sin ampliar el fichero).
- D. Not yet defined (que lo decida el análisis de alcance posterior).
- X. Other (please specify)

[Answer]: B. Primera oleada + `db_connection.py`: añadir la capa de conexión/arranque de BD (9 capturas) por ser crítica para la integridad.

## Q5. Alcance de FR4 — ¿qué entregable de "contratos de integración" esperas?

FR4 habla de documentar contratos y modos de fallo de Sofascore (API no oficial, baneo IP) y Futmondo (endpoints heterogéneos) y de detectar el fallo sin corromper datos. Los clientes externos hoy tienen poco broad-except (Sofascore 2, Futmondo 0), así que el peso está en detección+estado, no en limpiar `except`. ¿Qué esperas producir?

- A. **Documentación + detección en código**: un documento de contratos/modos de fallo Y el código que detecta baneo/entrada fallida y lo refleja en el estado del sync (sin escribir datos corruptos).
- B. **Solo detección en código**: lo importante es que el sistema detecte y marque el fallo; la documentación es secundaria.
- C. **Solo documentación**: por ahora basta documentar los contratos y modos de fallo; la detección se implementa en un intent posterior.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. Documentación + detección en código: un documento de contratos/modos de fallo Y el código que detecta baneo/entrada fallida y lo refleja en el estado del sync (sin escribir datos corruptos).

## Q6. Semántica de "recuperable vs fatal" — ¿cómo debe comportarse el sistema ante cada tipo?

FR3.2 pide distinguir error recuperable de fatal. ¿Cuál es tu expectativa de comportamiento?

- A. **Recuperable = continuar degradado; fatal = abortar limpio**: un paso no crítico que falla marca `degraded` y el sync sigue; un fallo fatal (p. ej. BD caída, baneo total) aborta sin dejar datos a medias y lo refleja en el estado.
- B. **Todo se registra y se refleja, nada aborta**: incluso lo fatal se marca en estado pero el proceso intenta terminar; prioridad a la observabilidad.
- C. **Aún no lo tengo claro**: que el diseño proponga la taxonomía recuperable/fatal.
- D. Not applicable.
- X. Other (please specify)

[Answer]: A. Recuperable = continuar degradado; fatal = abortar limpio: un paso no crítico que falla marca `degraded` y el sync sigue; un fallo fatal (p. ej. BD caída, baneo total) aborta sin dejar datos a medias y lo refleja en el estado.

## Q7. Disparador — ¿por qué ahora?

- A. **Continuación natural**: FR3.1 (pasos non-critical visibles) ya está hecho y este es el siguiente paso lógico del mismo eje de fiabilidad (AX3).
- B. **Dolor recurrente**: los fallos silenciosos / datos corruptos me están molestando ahora mismo en producción.
- C. **Preparar el terreno**: quiero endurecer la fiabilidad antes de abordar la descomposición de god-files (Intent 3).
- D. Not applicable.
- X. Other (please specify)

[Answer]: A. Continuación natural: FR3.1 (pasos non-critical visibles) ya está hecho y este es el siguiente paso lógico del mismo eje de fiabilidad (AX3).

## Q8. Interesados y decisor — ¿quién decide alcance y prioridad?

- A. **Solo tú**: eres el único mantenedor; decides alcance, prioridad y das el visto bueno en cada gate. No hay reporte a terceros.
- B. Hay otros interesados (indícalos en Other).
- C. Not identified.
- X. Other (please specify)

[Answer]: A. Solo tú: eres el único mantenedor; decides alcance, prioridad y das el visto bueno en cada gate. No hay reporte a terceros.

## Q9. Requisitos de comunicación / cadencia de reporte

- A. **Ninguno**: no hace falta cadencia de reporte ni comunicación formal; los gates de AI-DLC son suficientes.
- B. **Registro escrito**: quiero que las decisiones queden documentadas en los artefactos del intent (ya es el caso), sin nada adicional.
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. Ninguno: no hace falta cadencia de reporte ni comunicación formal; los gates de AI-DLC son suficientes.

## Q10. Confirmación de scope — el flujo arrancó con scope `feature`

El scope `feature` [scope] ejecuta el ciclo completo (ideación → inception → construcción) con profundidad estándar y piso de cobertura. El plan de intents también clasifica este Intent 1 como `feature`. ¿Confirmas ese límite de producto, o el alcance real es otro?

- A. **Confirmo `feature`**: intervención acotada y aditiva sobre manejo de errores y contratos, con specs significativas y el ciclo estándar.
- B. **Es más pequeño (`bugfix`/`refactor`)**: en realidad es un endurecimiento acotado sin diseño nuevo.
- C. **Es más grande**: implica más de lo que sugiere `feature` (descríbelo en Other).
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. Confirmo `feature`: intervención acotada y aditiva sobre manejo de errores y contratos, con specs significativas y el ciclo estándar.

## Consolidated Summary Confirmation

Resumen de lo capturado (antes de fijar los artefactos):

- **Problema**: fiabilidad general del backend — ~194 capturas amplias de excepción enmascaran fallos (silenciosos, corrupción de datos, diagnóstico lento). (Q1=D)
- **Afectados**: operador único (depuración/limpieza) y usuarios finales (datos incoherentes). (Q2=C)
- **Éxito**: las tres métricas juntas — reducir broad-except (1ª oleada), detección de baneo/fallo reflejada en estado, y contratos documentados — con specs significativas. (Q3=D)
- **Alcance FR3.2**: 1ª oleada segura = `except: pass` de arranque (`main.py`) + migraciones (`scripts/migrate_*`) + `db_connection.py` (9 capturas); `data_sync_service.py` (29) queda como deuda salvo puntos de corrupción, sin ampliar el god-file. (Q4=B)
- **Alcance FR4**: documentación de contratos/modos de fallo (Sofascore, Futmondo) + detección en código reflejada en estado, sin datos corruptos. (Q5=A)
- **Semántica error**: recuperable → degradado y sigue; fatal → aborta limpio sin datos a medias. (Q6=A)
- **Disparador**: continuación natural de FR3.1 (eje AX3). (Q7=A)
- **Decisor**: solo tú, mantenedor único; sin reporte a terceros. (Q8=A)
- **Comunicación**: sin cadencia; gates de AI-DLC suficientes. (Q9=A)
- **Scope**: `feature` confirmado. (Q10=A)
- **Transversal**: stack actual, sin reescrituras grandes, test-after + gate CI bloqueante, coste 0 €.

[Answer]: Looks correct
