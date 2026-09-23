# Preguntas de diseño de contratos — Fiabilidad de la sync

> Conversation language: Spanish.

## Q1 — Contrato del payload de paso degradado (R-02)

- A. `{status: "degraded", reason: str, ...}` en `progress[step]`, válido in-memory y durable (aditivo).
- B. Otro contrato.
- X. Other (please specify)

[Answer]: A

## Q2 — Contrato del techo en `place_bid` (FR6)

- A. `price > PRICE_SANITY_CAP` → 422, junto al `price <= 0` existente; sin cambios de salida ni frontend.
- B. Otro.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumen de contratos, confirmado por el usuario:

- **CT1** helper `record_degraded_step(tm, task_id, step, reason, extra)`; **CT2** payload `{status: "degraded", reason, ...}` (aditivo, in-memory + durable); **CT3** `place_bid`: `price > PRICE_SANITY_CAP` → 422 junto al `<= 0` existente; **CT4** política except recuperable/fatal (semántica interna).

[Answer]: Looks correct