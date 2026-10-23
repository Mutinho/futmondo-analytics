# Infrastructure Design — Questions (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Infrastructure Design de U2:

- **NO-APLICA infra / CI-CD / monitorización nuevos**: U2 es UI SwiftUI cliente; no despliega ni provisiona nada, no toca Fly.io/Neon ni los workflows. El gate de CI existente aplica al PR tal cual.
- **Verificación**: `cd ios && swift build` + validación de UI en iPhone 13 Pro (`xtool`). Sin runner Swift en CI (coste 0 €, deuda aceptada ya registrada en U1).

¿Does this all look correct?

[Answer]: Looks correct
