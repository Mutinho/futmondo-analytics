# Contract Design — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Contract Design:

- **Backend (consumo, sin cambios)**: `GET /api/v1/analytics/balances?championship_id=` → `BalancesResponse` (con `TeamBudget` de 9 campos; `performance = team_value + balance - initial_budget`); `GET /api/v1/user/championships` con fallback a `/championships` → `ChampionshipsResponse`. Campos extra de `Championship` como opcionales para tolerar el endpoint legacy.
- **U1 (superficie pública)**: protocolos `BudgetService`, `ChampionshipService` (fallback interno), `ActiveChampionshipStore` (persiste en `UserDefaults`); `MoneyFormatter`, `TeamBudgetSort`; tipos `Codable`. Errores como `NetworkError` tipado.
- **U2 (consumo)**: `BudgetViewModel` con inyección por protocolo (testable); estado `BudgetState { loading, loaded, empty, error }`; `BudgetRow` usa `MoneyFormatter` + `DSColor`/`DSFont` de F1.
- **Invariantes**: sin credenciales en las APIs (NFR2), cero dependencias nuevas (NFR1), sin cambios de backend.

¿Does this all look correct?

[Answer]: Looks correct
