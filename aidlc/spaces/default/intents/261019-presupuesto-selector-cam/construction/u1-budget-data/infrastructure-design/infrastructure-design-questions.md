# Infrastructure Design — Questions (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Infrastructure Design de U1:

- **NO-APLICA infra/CI-CD nuevo**: U1 es código de librería cliente iOS; no despliega, no toca Fly.io/Neon ni los workflows (`ci.yml`/`fly-deploy.yml`). El gate de CI bloqueante existente aplica al PR tal cual.
- **Verificación**: `cd ios && swift build && swift test` en WSL (local). No se añade runner Swift al CI (coste 0 €, fuera de alcance; sería un intent aparte si se quisiera).

¿Does this all look correct?

[Answer]: Looks correct
