# Preguntas de definición de alcance — Fiabilidad de la sync

> Conversation language: Spanish. Las decisiones de alcance ya se resolvieron en
> intent-capture (recomendaciones punto a punto + Opción C). Se registran aquí
> como confirmación del alcance.

## Q1 — Límite del alcance de FR3.1/FR3.2

¿El alcance se ciñe a `prizes`/`phantoms` + arranque/migraciones + camino de sync?

- A. Sí, ceñido (helper reutilizable; sin purga masiva; sin ampliar god-files).
- B. Ampliar a todos los pasos y a todos los `except` del backend.
- X. Other (please specify)

[Answer]: A

## Q2 — Tratamiento de FR6 en este intent

- A. Solo el techo de sanidad + test; positividad ya en `main`; rango dinámico y frontend fuera.
- B. Incluir rango dinámico del mercado.
- X. Other (please specify)

[Answer]: A

## Q3 — Backend-only

¿Se confirma que no se toca el frontend?

- A. Sí, backend-only.
- B. Incluir cambios de frontend.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumen del alcance (Opción C), confirmado por el usuario:

- **IN**: FR3.1 (helper `record_degraded_step` + estado "degradado" en tarea para `prizes`/`phantoms`), FR3.2 (acotar `except` de arranque/migraciones + camino de sync), FR6 remate (techo de sanidad del `price` + test). Specs `pytest` significativas.
- **OUT**: frontend, rango dinámico del mercado, purga masiva de `except`, reescritura de god-files, demás pasos non-critical.
- Restricciones: backend-only, coste 0 €, no ampliar god-files, gate de CI verde antes de merge.

[Answer]: Looks correct
