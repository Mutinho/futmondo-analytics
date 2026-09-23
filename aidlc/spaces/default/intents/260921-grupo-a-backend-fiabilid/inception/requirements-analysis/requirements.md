# Requisitos — Fiabilidad de la sync de 11 pasos

> Conversation language: Spanish. Scope: `feature`. Brownfield futmondo-analytics.
> Traduce `intent-statement.md` y `scope-document.md` en requisitos técnicos
> trazables, anclados en el código real de `main` (verificado 2026-09-21).
> Backend-only, coste 0 €, sin ampliar god-files.

## Análisis de intención

Hacer observables y acotados los fallos silenciosos de la sincronización, de modo
que un paso que falla deje de reportarse como éxito, reduciendo además el manejo
de errores demasiado amplio que enmascara la causa. Remate menor de seguridad:
techo de sanidad del `price` de puja.

## Requisitos funcionales

### FR3.1 — Estado "degradado" observable para pasos non-critical

Hoy, en `backend/app/api/v1/endpoints/sync.py` (~líneas 143-164), cuando
`sync_prizes()` o `_check_phantoms()` lanzan, el `except` marca el paso como
`{"status": "done", ..., "error": str(err)}`: el paso queda como **`done`**
(éxito) pese al fallo. El consumidor que lee `status` no distingue un éxito real
de un fallo degradado.

- Prioridad: **Crítico** (fiabilidad observable) · Esfuerzo: S
- **FR3.1.1**: Introducir un helper estrecho reutilizable
  (p. ej. `record_degraded_step(tm, task_id, step, reason)`), **fuera del god-file**,
  que marque el paso con un estado explícito **`degraded`** (distinto de `done`) y
  emita un **log estructurado** con el `step` y el motivo.
- **FR3.1.2**: Cablear `prizes` y `phantoms` a ese helper en su rama `except`.
- **FR3.1.3 (R-02)**: El estado degradado tiene un **contrato tipado** (p. ej.
  `status: "degraded"`, `reason: str`), coherente entre el `TaskManager`
  in-memory y el `task_service` durable, de modo que un test pueda aseverar el
  estado, no solo el log.
- Criterios de aceptación:
  - Dado que `sync_prizes()` lanza, cuando termina la sync, entonces el paso
    `prizes` figura con `status == "degraded"` (no `done`) y un `reason`, y hay un
    log estructurado del fallo.
  - Ídem para `phantoms` cuando `_check_phantoms()` lanza.
  - Un paso que NO falla sigue marcándose `done` (sin regresión de comportamiento).

### FR3.2 — Acotar el `except Exception`/bare-except silencioso

Reducir los `except` demasiado amplios que silencian fallos, empezando por
arranque/migraciones (`backend/app/services/db_connection.py`,
`backend/app/auth/token_store.py` y equivalentes) y los `except` del camino de
sync tocado por FR3.1.

- Prioridad: **Importante** · Esfuerzo: M
- **FR3.2.1**: En los puntos en alcance, distinguir error **recuperable**
  (log + continuar/reintentar) de **fatal** (propagar). Prohibido capturar-y-silenciar.
- **FR3.2.2**: Alcance acotado: NO purga masiva de los ~159 `except` del backend.
- Criterios de aceptación:
  - Dado un fallo fatal en arranque/migración en alcance, cuando ocurre, entonces
    se propaga (no se traga) con contexto en el log.
  - Dado un fallo recuperable en esos puntos, entonces se registra y el flujo
    continúa de forma definida.

### FR6 — Techo de sanidad del `price` de puja

La positividad ya está en `main`: `market.py::place_bid` rechaza `price <= 0`
con HTTP 422 antes de proxyar a Futmondo. Falta un límite superior.

- Prioridad: **Importante** · Esfuerzo: S
- **FR6.1**: Añadir un **techo de sanidad** al `price` (rechazo con 422 si supera
  el límite), sin llamada de red adicional.
- **FR6.2 (R-03)**: El límite es un criterio **estable y documentado** (p. ej.
  múltiplo holgado del presupuesto máximo plausible), para que el test asevere un
  umbral fijo.
- Criterios de aceptación:
  - Dado un `price` por encima del techo enviado a `POST /api/v1/market/bid`,
    cuando llega al backend, entonces se rechaza con 422 antes de proxyar.
  - La validación existente de `price <= 0` se mantiene intacta.

## Requisitos no funcionales

- **NFR1 — Fiabilidad observable**: el estado de la tarea refleja con fidelidad el
  resultado de cada paso; un fallo parcial no se presenta como éxito.
- **NFR2 — Mantenibilidad**: el nuevo código vive tras funciones estrechas
  testeables; no se amplían los god-files ni el patrón SQL-en-router.
- **NFR3 — Testabilidad**: specs `pytest` significativas (aserciones reales de
  estado, log y rechazo), nunca `assert True`.
- **NFR4 — Coste**: coste 0 €; solo herramientas ya presentes (`pytest`).
- **NFR5 — Seguridad**: la validación de entrada del `price` se refuerza en el
  backend (defensa en profundidad), independientemente del frontend.

## Constraints

- Backend-only; sin tocar frontend. Sin reescrituras grandes.
- Gate de CI bloqueante (gitleaks + `pytest` + `ng test`) verde antes de merge.
- Formateo brownfield quirúrgico.

## Sources

- [desc] Reencuadre Opción C confirmado por el usuario.
- Consume `ideation/intent-capture/intent-statement.md`, `ideation/scope-definition/scope-document.md`, y el codekb (`business-overview`, `architecture`, `code-structure`).
- Código verificado en `main` (2026-09-21): `backend/app/api/v1/endpoints/sync.py:143-164` (degradación prizes/phantoms), `backend/app/api/v1/endpoints/market.py:122-186` (place_bid, validación FR6 existente), `backend/app/services/db_connection.py` y `auth/token_store.py` (except de arranque).
- Hallazgos R-01/R-02/R-03 de la revisión advisory de intent-capture.

## Assumptions & Open Questions

- [assumption] El contrato tipado del estado "degraded" se puede añadir de forma aditiva al `TaskManager` y `task_service` sin cambio de esquema de BD mayor; se confirma en domain/functional design.
- El valor exacto del techo de `price` se fija en diseño.
