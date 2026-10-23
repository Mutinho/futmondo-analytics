# NFR Requirements — Questions (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de NFR Requirements de U1:

- **Seguridad (NFR2)**: SR1 sin password/token en mensajes de error; SR2 `UserDefaults` sólo guarda el `championship_id` (no sensible); SR3 HTTPS (init del `NetworkClient` de F1 rechaza no-https); SR4 decode `Codable` estricto, opcionales tolerados.
- **Tech stack**: TS1 cero dependencias nuevas (`dependencies: []`); TS2 todo en `FutmondoKit` testeable con `swift test`, formato/resolución con lógica pura determinista (sin `NumberFormatter`/locale); TS3 `Sendable`/`async`, reutiliza el modelo de F1.
- U1 **no introduce superficie de seguridad nueva**; reutiliza auth/transporte de F1.

¿Does this all look correct?

[Answer]: Looks correct
