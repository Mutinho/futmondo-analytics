# Preguntas de análisis de requisitos — Fiabilidad de la sync

> Conversation language: Spanish. Decisiones de requisitos derivadas del alcance
> ya confirmado (Opción C). Se registran como confirmación.

## Q1 — Estado "degradado" como estado explícito

¿FR3.1 introduce un `status` explícito `degraded` (distinto de `done`)?

- A. Sí, `degraded` explícito con contrato tipado (`status`, `reason`).
- B. Mantener `done` con un campo `error` (statu quo).
- X. Other (please specify)

[Answer]: A

## Q2 — Techo de `price` (FR6)

¿El techo es un límite estable documentado, sin llamada de red?

- A. Sí, límite fijo documentado (múltiplo holgado del presupuesto máximo plausible).
- B. Rango dinámico del mercado (fuera de alcance).
- X. Other (please specify)

[Answer]: A

## Q3 — Alcance de FR3.2

- A. Arranque/migraciones + camino de sync; sin purga masiva.
- B. Todos los `except` del backend.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumen de requisitos (Opción C), confirmado por el usuario:

- **FR3.1** — Estado `degraded` explícito (distinto de `done`) + log estructurado para `prizes`/`phantoms`, vía helper estrecho fuera del god-file; contrato tipado del estado (locus real: `sync.py:143-164`).
- **FR3.2** — Acotar `except` de arranque/migraciones + camino de sync (recuperable vs fatal); sin purga masiva.
- **FR6** — Techo de sanidad del `price` en `place_bid` (422), límite estable documentado; positividad ya en `main`.
- NFR: fiabilidad observable, mantenibilidad (sin god-files), testabilidad (specs significativas), coste 0 €, seguridad. Backend-only.

[Answer]: Looks correct
