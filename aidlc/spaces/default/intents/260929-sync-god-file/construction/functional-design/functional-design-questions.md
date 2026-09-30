# Functional Design — Preguntas de clarificación

Intent: `sync-god-file` (Oleada 3, FR13) · scope `refactor` · depth Minimal · backend-only.
Etapa de diseño: modela la descomposición DDD por dominio de `data_sync_service.py`. El patrón
objetivo (`analytics/`, `assistant/`, `prizes/`) y el contrato público ya están fijados por los
requisitos; estas preguntas resuelven las decisiones de forma de los módulos nuevos.

---

## Q1 — Forma del módulo por dominio (layering objetivo)

`analytics/`/`assistant/` usan 4 capas (`domain/ports.py` + `application/` + `infrastructure/*_adapter.py` + `facade.py`); `prizes/` usa una forma más ligera (cálculo puro + writer + `__init__`). ¿Qué forma adoptan los 9 dominios a extraer?

- A. **Layering completo por dominio** (`domain/ports.py`, `application/`, `infrastructure/*_adapter.py`, `facade.py`), replicando `analytics/`/`assistant/` para todos.
- B. **Forma proporcional al dominio**: layering completo donde hay cálculo/SQL sustancial; forma ligera estilo `prizes/` donde el dominio es casi passthrough de ingesta+persistencia.
- C. Estructura plana por dominio (un solo módulo `sync_<domain>.py` con funciones, sin subcarpetas domain/application/infrastructure).
- D. Sin preferencia — replicar el layering completo de `analytics/`/`assistant/` (A).
- X. Other (please specify)

[Answer]: B (forma proporcional al dominio: layering completo de 4 capas donde hay cálculo/SQL sustancial —p. ej. player_performance, rosters, prizes—; forma ligera estilo prizes/ donde el dominio es casi passthrough de ingesta+persistencia —p. ej. transactions, clauses, match_odds—. En AMBAS formas el SQL queda tras un adaptador/función estrecha testeable, nunca inline en el orquestador —FR3—.)

---

## Q2 — Alcance del port de datos por dominio

`analytics/` define un `Protocol` port consumer-owned con solo las operaciones que consume. ¿Cómo se modela el port de datos de cada dominio de sync?

- A. **Un port estrecho por dominio** (`<Domain>SyncDataPort`), declarando solo las operaciones de `DataManagerV2` (y los `cursor.execute` inline que hoy usa ese dominio) que ese dominio consume.
- B. Un único port compartido de sync para los 10 dominios.
- C. Sin port explícito: el adaptador de infraestructura envuelve `DataManagerV2` y la aplicación lo recibe por inyección sin `Protocol`.
- D. Sin preferencia — un port estrecho por dominio (A), como en `analytics/`.
- X. Other (please specify)

[Answer]: A (un port Protocol estrecho consumer-owned por dominio —`<Domain>SyncDataPort`—, declarando solo las operaciones de DataManagerV2 y los cursor.execute inline de hoy que ese dominio consume; en dominios de forma ligera el port puede ser de una o dos operaciones, pero sigue siendo la frontera testeable con fakes en memoria)

---

## Q3 — Ubicación de la ingesta externa (FutmondoClient/Sofascore) en el nuevo layering

Cada `sync_*` hoy hace ingesta desde `futmondo_client`/`sofascore_client` además de cálculo y persistencia. ¿Dónde vive la ingesta en el módulo de dominio?

- A. **La ingesta externa es infraestructura**: un adaptador de ingesta (o el mismo `*_adapter.py`) tras un port; la aplicación orquesta ingesta→cálculo→persistencia sin conocer el cliente concreto.
- B. La ingesta se queda en el facade/orquestador del dominio (como hoy en `sync_prizes`, que orquesta ingesta y delega solo cálculo y escritura), no tras un port.
- C. Sin preferencia — modelar la ingesta como infraestructura tras un port (A) para máxima testabilidad con fakes.
- D. Sin preferencia — seguir el patrón exacto de `sync_prizes` (B): orquestador fino que llama al cliente y delega cálculo/escritura.
- X. Other (please specify)

[Answer]: B (la ingesta externa se queda en el orquestador de aplicación del dominio, como en sync_prizes: el orquestador llama a FutmondoClient/Sofascore —ya inyectable en DataSyncService.__init__— y delega solo cálculo y persistencia; el bloque try/except Integration*Error envuelve esas llamadas y se preserva tal cual. Replica el patrón de referencia FR2.3; solo el SQL va tras port/adaptador, no la ingesta.)

---

## Q4 — Ubicación del manejo de errores tipados y el throttling

FR5.3 exige preservar el manejo de `Integration*Error` (recuperable/fatal, BR2.1–2.3) y el `time.sleep()` de throttling. ¿En qué capa quedan tras la extracción?

- A. **En el orquestador de aplicación del dominio**: el `try/except <Typed>: raise` antes del `except Exception` genérico y el throttling se mueven al punto de orquestación del dominio, preservando exactamente la semántica actual (recuperable degrada / fatal en punto de escritura propaga).
- B. En el facade delgado de `DataSyncService`, envolviendo la delegación a cada dominio.
- C. Sin preferencia — en el orquestador de aplicación del dominio (A), preservando la semántica byte-a-byte observable.
- X. Other (please specify)

[Answer]: A (el try/except Integration*Error —recuperable/fatal, BR2.1–2.3— y el time.sleep() de throttling viven en el orquestador de aplicación del dominio, viajando con la ingesta que envuelven; el facade de DataSyncService se mantiene delgado sin lógica de errores propia —FR1.2—; la semántica observable se preserva byte-a-byte —FR5.3—)

---

## Consolidated Summary Confirmation

Resumen de las decisiones de diseño antes de generar los artefactos:

- **Q1 — Forma del módulo (proporcional)**: layering completo de 4 capas (`domain/ports.py` + `application/` + `infrastructure/*_adapter.py` + facade) donde hay cálculo/SQL sustancial (p. ej. `player_performance`, `rosters`, `prizes`); forma ligera estilo `prizes/` donde el dominio es casi passthrough de ingesta+persistencia (p. ej. `transactions`, `clauses`, `match_odds`). En AMBAS formas el SQL queda tras un adaptador/función estrecha testeable, nunca inline (FR3).
- **Q2 — Port de datos (estrecho por dominio)**: un `Protocol` port consumer-owned por dominio (`<Domain>SyncDataPort`) con solo las operaciones que ese dominio consume; en dominios ligeros puede ser de una o dos operaciones, pero sigue siendo la frontera testeable con fakes.
- **Q3 — Ingesta externa (en el orquestador)**: la ingesta desde `FutmondoClient`/Sofascore se queda en el orquestador de aplicación del dominio (patrón `sync_prizes`, FR2.3), no tras un port; el cliente sigue inyectable vía `DataSyncService.__init__`.
- **Q4 — Errores tipados y throttling (en el orquestador)**: el `try/except Integration*Error` (BR2.1–2.3) y el `time.sleep()` viven en el orquestador de aplicación del dominio, viajando con la ingesta; el facade de `DataSyncService` queda delgado (FR1.2), sin lógica de errores propia.
- **Contrato preservado (de los requisitos)**: `DataSyncService` + los 10 `sync_*` + `sync_all()`; las 10 claves literales del dict de `sync_all()` (incluida `team_standings` para `rankings`); orden players-primero-por-FK; escritura atómica set-replacement de `prizes`; equivalencia funcional estricta (FR1, FR2.2, FR5).
- **Restricciones duras**: sin ampliar los god-files, sin reformateo masivo, sin relajar el piso `--cov-fail-under=27`, coste 0 €; characterization-first por dominio antes de trocear.
- **Artefactos a generar**: `entities.md` (value objects/entidades del sync por dominio), `rules.md` (reglas `BRx.y`: equivalencia, orden, errores, escritura atómica), `functional-spec.md` (workflow de `sync_all` y de un `sync_*` genérico + máquina de estados de un paso de sync + diagrama derivado), `traceability.json`. NO se genera `frontend-components.md` (refactor backend-only, sin UI).

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
