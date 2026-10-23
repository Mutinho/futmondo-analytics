# Security Test Instructions — F2

> Fase: construcción (build-and-test). Idioma: castellano; tokens técnicos verbatim en inglés.

## Verificaciones (ejecutables)

- **No-fuga de credenciales** (NFR2): los tests de U1 (`BudgetServiceTests`/`ChampionshipServiceTests`) aseveran que la descripción de error ante fallo NO contiene `championship_id` ni tokens (cubren `NetworkError` y `DecodingError`). U2 reexpone ese mensaje verbatim (sin interpolar), por lo que la garantía se mantiene.
- **HTTPS forzado** (SEC-N1): heredado del `URLSessionNetworkClient` de F1 (init lanza si la base URL no es https); U2 reutiliza el MISMO cliente HTTPS (sin cliente nuevo inseguro).
- **`UserDefaults` sin secretos**: sólo el `championship_id` activo.
- **Sin secretos hardcodeados**: gitleaks (gate de CI) escanea el árbol; el código nuevo no introduce tokens.

## Comando

`cd ios && swift test` (incluye las aserciones de no-fuga de U1).

## Assumptions & Open Questions

None.
