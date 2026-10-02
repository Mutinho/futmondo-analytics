# Functional Design — Preguntas

> Intent `261001-sync-god-file-resto` (scope `refactor`, profundidad Minimal).
> Diseño funcional del patrón de extracción por dominio. El patrón objetivo
> (orchestrator + domain port + infrastructure adapter) y la equivalencia
> estricta ya están fijados en `requirements.md` (FR1-FR7). Estas preguntas sólo
> cierran decisiones de diseño genuinamente abiertas. Idioma: castellano.

---

## Q1 — Forma del domain port por dominio

El piloto `match_odds` usa un `typing.Protocol` consumer-owned en
`domain/ports.py` que declara sólo las operaciones de persistencia que el
orchestrator consume (p. ej. `save_match_odds`, `update_sync_metadata`),
reflejando la superficie de `DataManagerV2` verbatim. ¿Cómo modelamos el port de
cada dominio nuevo?

- A. Un `Protocol` por dominio que declara EXACTAMENTE los métodos de `DataManagerV2` que ese `sync_*` invoca hoy (nombres y firmas verbatim), ni más ni menos. El adapter los implementa delegando 1:1.
- B. Un `Protocol` por dominio con métodos de intención de dominio (p. ej. `save_clauses(...)`) que internamente mapean a uno o varios métodos de `DataManagerV2`, permitiendo renombrar en la frontera del port.
- C. Otro (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — Protocol por dominio con los métodos de `DataManagerV2` que ese `sync_*` invoca hoy, verbatim; adapter delega 1:1.

---

## Q2 — Punto de corte entre orchestrator e ingesta/throttling

Hoy cada `sync_*` entrelaza llamadas a `FutmondoClient`, `time.sleep` de
throttling y mapeo de rondas. ¿Cómo queda el orchestrator?

- A. El orchestrator aloja TODA la orquestación hoy inline (ingesta vía `FutmondoClient` inyectado, throttling con `time.sleep`, mapeo de rondas, manejo de errores) y delega SÓLO la persistencia al port — igual que `MatchOddsSyncOrchestrator`. El `FutmondoClient` se inyecta en el constructor.
- B. Igual que A, pero extraer también el throttling a una utilidad compartida reutilizable entre dominios.
- C. Otro (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — orchestrator aloja la orquestación inline de hoy (ingesta vía `FutmondoClient` inyectado, throttling `time.sleep`, mapeo de rondas, errores) y delega sólo persistencia al port; sin extraer throttling (equivalencia verbatim).

---

## Q3 — Entidades a modelar en `entities.md`

Este es un refactor de equivalencia estricta sin nuevo modelo de datos
persistente (el esquema de Neon no cambia). ¿Qué registra `entities.md`?

- A. Modelar las **entidades de dominio observables del sync** como estructuras lógicas: el `SyncResult` por dominio (con sus claves exactas por dominio) y las entidades de datos que cada dominio ingesta/persiste (clauses, transactions, etc.) a nivel lógico, SIN inventar esquema físico nuevo (se refleja el existente). El `SyncResult` por dominio es el contrato observable a congelar.
- B. Igual que A, pero además modelar los componentes de software nuevos (orchestrator/port/adapter) como entidades estructurales.
- C. Otro (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — modelar el `SyncResult` por dominio (contrato observable a congelar) y las entidades de datos ingestadas/persistidas a nivel lógico, reflejando el esquema existente sin inventar nuevo.

---

## Q4 — Alcance de las máquinas de estado / flujos en `functional-spec.md`

- A. `functional-spec.md` documenta el **flujo de una operación `sync_*` extraída** (ingesta → mapeo → persistencia vía port/adapter → `SyncResult`) y la clasificación de errores recoverable/fatal como transiciones de estado del paso (`OK`/`DEGRADED`/fallo fatal) preservadas verbatim; más el flujo de delegación fina del método público. Un único flujo canónico parametrizado por dominio (los 8 comparten forma), notando las diferencias de `SyncResult` por dominio.
- B. Un flujo/máquina de estado separado y completo por cada uno de los 8 dominios.
- C. Otro (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — un flujo canónico parametrizado por dominio (ingesta → mapeo → persistencia vía port/adapter → `SyncResult`), con la clasificación recoverable/fatal como transiciones (`OK`/`DEGRADED`/fatal) preservadas verbatim, más el flujo de delegación fina del método público; se notan las diferencias de `SyncResult` por dominio.

---

## Consolidated Summary Confirmation

Resumen de las decisiones de diseño (recomendación del conductor aplicada por indicación del usuario):

- Q1 — Domain port por dominio como `Protocol` consumer-owned que declara los métodos de `DataManagerV2` que ese `sync_*` invoca hoy, verbatim; el adapter delega 1:1.
- Q2 — El orchestrator aloja la orquestación inline de hoy (ingesta vía `FutmondoClient` inyectado, throttling `time.sleep`, mapeo de rondas, errores) y delega sólo la persistencia al port; sin extraer el throttling (equivalencia verbatim).
- Q3 — `entities.md` modela el `SyncResult` por dominio (contrato observable a congelar) y las entidades de datos ingestadas/persistidas a nivel lógico, reflejando el esquema existente sin inventar nuevo.
- Q4 — `functional-spec.md` documenta un flujo canónico parametrizado por dominio (ingesta → mapeo → persistencia vía port/adapter → `SyncResult`) con la clasificación recoverable/fatal como transiciones (`OK`/`DEGRADED`/fatal) preservadas verbatim, más el flujo de delegación fina del método público; se notan las diferencias de `SyncResult` por dominio.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
