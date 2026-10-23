# Developer Scan Handoff — Reverse Engineering (F2)

> Pipeline handoff del link `aidlc-developer-agent`. Idioma: castellano; tokens técnicos verbatim en inglés.
> Intent: `261019-presupuesto-selector-cam`. Fecha: 2026-10-19. Tipo: refresco incremental (focused scan).

## Alcance del escaneo

Refresco incremental del codekb existente `aidlc/spaces/default/codekb/futmondo-analytics/` (no reconstrucción), enfocado en la **capa nativa iOS** añadida por F1 y en las **áreas Budget/championship** que F2 reproduce. Los 9 artefactos del codekb se actualizaron; el timestamp se reescribió a 2026-10-19.

## Artefactos actualizados

- `code-structure.md`, `component-inventory.md` — añadido el árbol `ios/` (FutmondoKit: Networking/Auth/DesignSystem; FutmondoApp: vistas + DesignSystem SwiftUI; Tests) y áreas de interés F2.
- `architecture.md` — el cliente nativo iOS pasa a componente real que consume el backend por HTTPS (Bearer + `X-Refresh-Token`).
- `technology-stack.md` — Swift 6 / SwiftUI / SwiftPM / xtool / Keychain / XCTest + restricciones del toolchain WSL.
- `api-documentation.md` — endpoints de F2 con contrato verificado.
- `business-overview.md`, `dependencies.md`, `code-quality-assessment.md` — actualizados sólo donde la capa iOS cambia.
- `reverse-engineering-timestamp.md` — fecha 2026-10-19, refresco incremental, scope `partial`.

## Hechos clave de la capa `ios/` (base de F2)

- SwiftPM `swift-tools-version:6.0`, sólo SDK de Apple, `dependencies: []`; xtool (`bundleID com.futmondo.app`, `product FutmondoApp`).
- Productos: `FutmondoKit` (library testeable) + `FutmondoApp` (SwiftUI bajo `#if canImport(SwiftUI)`). El testTarget sólo depende de `FutmondoKit` → `swift test` compila en WSL sin SwiftUI.
- Networking: `URLSessionNetworkClient` (init throwing rechaza base URL no-https, inyecta `Authorization: Bearer`, mapea status→`NetworkError`). Base prod `https://futmondo-api.fly.dev`.
- Auth: `AuthService` actor; access token en memoria + refresh coalescido; refresh token en Keychain (`com.futmondo.app.auth`, `AfterFirstUnlockThisDeviceOnly`) enviado como header `X-Refresh-Token`.
- DesignSystem: tokens light/dark Material 3 (primary verde, moneyPositive/Negative), escala tipográfica, espaciado, contraste WCAG; componentes PrimaryButton/TextInputField/Card/LoadingState/ErrorState + CatalogView.
- Restricciones WSL: color sets en código (no `Assets.xcassets`); cobertura llvm-cov no fiable (vistas validadas en iPhone 13 Pro).

## Endpoints de los que depende F2 (verificados en el backend)

- `GET /api/v1/analytics/balances?championship_id=` (`balances.py`): `{success, championship_id, initial_budget, teams:[{team_id, team_name, balance, initial_budget, total_spent, total_income, purchases_count, sales_count, team_value, performance, max_bid, prizes}]}`; `performance = team_value + balance - initial_budget`; fallback `INITIAL_BUDGET = 200_000_000`. SQL-en-endpoint (patrón heredado, NO ampliar).
- `GET /api/v1/analytics/balances/{team_id}` → `TeamDetailResponse` (altas/bajas).
- `GET /api/v1/user/championships` (`user.py`): `{success, championships:[{championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank}]}`. Bearer requerido.
- `GET /api/v1/championships` (legacy, `championships.py`): subconjunto; **fallback** del `ChampionshipService`.
- Contrato de consumo a replicar: `BudgetService` pasa `championship_id` como query param; `ChampionshipService` carga `/user/championships` con fallback a `/championships` y persiste el activo en `localStorage` (`futmondo_active_championship`) → el selector nativo lo replica con `UserDefaults`.

## Concerns / notas para fases siguientes

- El modelo de championship trae más campos de los que la web Budget usa (bonos/puntos/ranking): insumo para domain/contract-design, no necesariamente todos en la vista de Presupuesto de F2.
- `UserMe` en `FutmondoKit` es un DTO smoke mínimo de F1; los DTOs de datos de Presupuesto/championship son trabajo nuevo de F2.
