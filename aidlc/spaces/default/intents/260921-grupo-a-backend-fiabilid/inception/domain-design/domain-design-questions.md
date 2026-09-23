# Preguntas de diseño de dominio — Fiabilidad de la sync

> Conversation language: Spanish. Decisiones de diseño derivadas de los requisitos
> (Opción C). Registradas como confirmación.

## Q1 — `degraded` como valor de `progress[step].status` (ADR-1)

- A. Sí, valor de paso `degraded` (aditivo, sin nuevo estado de Tarea, sin migración BD).
- B. Nuevo estado de Tarea `DEGRADED`.
- X. Other (please specify)

[Answer]: A

## Q2 — Helper `record_degraded_step` fuera del god-file (ADR-2)

- A. Sí, módulo estrecho reutilizable fuera de `data_sync_service.py`.
- B. Inline en cada `except`.
- X. Other (please specify)

[Answer]: A

## Q3 — Techo de `price` como constante documentada (ADR-3)

- A. Sí, `PRICE_SANITY_CAP` fijo documentado, sin red.
- B. Rango dinámico del mercado.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumen del diseño de dominio (Opción C), confirmado por el usuario:

- **ADR-1**: estado de paso `degraded` como valor de `progress[step].status` (aditivo, sin nuevo estado de Tarea ni migración de BD).
- **ADR-2**: helper estrecho `record_degraded_step` fuera del god-file, reutilizable; cablea `prizes`/`phantoms` en `sync.py:148-164`.
- **ADR-3**: techo `PRICE_SANITY_CAP` documentado en `place_bid` (422), sin red; valor exacto en functional-design.
- **ADR-4**: `except` acotados recuperable/fatal en arranque/migraciones + camino de sync; sin purga masiva.

[Answer]: Looks correct