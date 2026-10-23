# Reverse Engineering — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Reverse Engineering (refresco incremental del codekb):

- **Refresco incremental** (no reconstrucción) de `aidlc/spaces/default/codekb/futmondo-analytics/`, enfocado en la capa iOS de F1 y en Budget/championship. Timestamp a 2026-10-19.
- **Capa iOS capturada**: `FutmondoKit` (Networking/Auth/DesignSystem, sin deps externas) + `FutmondoApp` (SwiftUI); auth con access token en memoria + refresh en Keychain vía header `X-Refresh-Token`; restricciones WSL (color sets en código, cobertura no fiable).
- **Endpoints de F2 verificados**: `GET /api/v1/analytics/balances?championship_id=` (+`/{team_id}`), `GET /api/v1/user/championships` (fallback `GET /api/v1/championships`). `performance = teamValue + balance - initial_budget`; `INITIAL_BUDGET` por defecto 200.000.000.
- **Hallazgo útil**: championships expone más campos de los modelados (`money_per_point`, `money_per_ranking`, `dream_team_bonus`, `mvp_bonus`, `ranking_mode`, `users_to_rank`) — insumo para domain/contract-design.
- **Patrón a reproducir**: `ChampionshipService` persiste el campeonato activo en `localStorage`; el selector nativo lo replica con `UserDefaults`.

¿Does this all look correct?

[Answer]: Looks correct
