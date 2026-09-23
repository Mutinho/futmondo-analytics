# Preguntas de diseño funcional — U1 sync-reliability

> Conversation language: Spanish.

## Q1 — Ubicación de StepStatus y helper (R-02)

- A. Módulo nuevo `sync_step_status.py` con `StepStatus` + `record_degraded_step`.
- B. Otro sitio.
- X. Other (please specify)

[Answer]: A

## Q2 — Tipo del parámetro tm (R-01)

- A. `Protocol` (`ProgressSink`) que cubre `TaskManager` y `TaskService` (real: `TaskService`).
- B. `TaskManager` (incorrecto).
- X. Other (please specify)

[Answer]: A

## Q3 — Valor de PRICE_SANITY_CAP (R-03)

- A. `5_000_000_000` (múltiplo holgado, documentado), rechazo 422.
- B. Otro valor.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumen del diseño funcional de U1, confirmado por el usuario:

- **FS1**: `StepStatus` + `record_degraded_step` en `sync_step_status.py`; `tm` tipado como `Protocol ProgressSink` (real: `TaskService`) — R-01/R-02.
- **FS2**: cablear `prizes`/`phantoms` en `sync.py:143-164` al helper (estado `degraded`, no `done`).
- **FS3**: `PRICE_SANITY_CAP = 5_000_000_000` en `market.py`, rechazo 422 junto al `<= 0` — R-03.
- **FS4**: tabla `except` recuperable/fatal por locus (BR5).

[Answer]: Looks correct