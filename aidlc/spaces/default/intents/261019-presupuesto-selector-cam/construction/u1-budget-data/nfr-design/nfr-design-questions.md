# NFR Design — Questions (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de NFR Design de U1:

- **Seguridad**: SR1 errores con `status` + `path` (nunca URL/query), con test de no-fuga de `championship_id`/token; SR2 `UserDefaults` sólo el id; SR3 HTTPS heredado del `NetworkClient` de F1; SR4 decode `Codable` estricto. Sin superficie de amenaza nueva.
- **Componentes lógicos**: nueva subcarpeta `FutmondoKit/Budget/` (DTOs, `MoneyFormatter`, `TeamBudgetSort`, servicios, store, resolver); tests en `Tests/FutmondoKitTests/Budget*Tests.swift`. No se tocan `Networking/`/`Auth/`/`DesignSystem/` salvo consumo.
- **Rendimiento**: NO-APLICA carga (listas cortas, O(n)); la fluidez de render es de U2 (NFR4).

¿Does this all look correct?

[Answer]: Looks correct
