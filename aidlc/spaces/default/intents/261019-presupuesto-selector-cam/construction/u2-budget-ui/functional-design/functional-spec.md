# Functional Design — Spec (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui` (app `FutmondoApp`, SwiftUI). Idioma: castellano; tokens técnicos verbatim en inglés.
> Consume U1 (`FutmondoKit/Budget/`) + DesignSystem de F1. Todo bajo `#if canImport(SwiftUI)`. Validación en dispositivo.

## Componentes (en `FutmondoApp/Budget/`)

### `RootTabView`
- `TabView` con una pestaña "Presupuesto" (icono dinero), que contiene un `NavigationStack` con `BudgetView`. Material del sistema (Liquid Glass iOS 26) automático. (FR5.1)
- **Integración con F1**: sustituye el cuerpo de `SplashView.content` → `case .resumed` (hoy `authenticatedPlaceholder`). Recibe el `BudgetViewModel` ya compuesto y un callback de logout. **Re-aloja el logout** de F1: expone "Cerrar sesión" que invoca el mismo `AuthViewModel.logout()` y fija `phase = .noSession` vía el callback/binding de `SplashView`. No cambia `runBootstrap`, `.onChange(of: viewModel.state)` ni las demás fases.

### `BudgetViewModel` (`@MainActor @Observable`)
- Depende por inyección de `BudgetService`, `ChampionshipService`, `ActiveChampionshipStore` (protocolos de U1) + `TeamBudgetSort`/`ActiveChampionshipResolver`.
- Estado: `enum BudgetState { case loading, loaded([TeamBudget]), emptyTeams, noChampionships, error(String) }`, `championships: [Championship]`, `activeChampionship: Championship?`, `sortKey: SortKey = .balance`.
  - `emptyTeams`: hay campeonato activo pero `teams` vacío → mensaje "Este campeonato no tiene equipos aún."; el selector sigue habilitado.
  - `noChampionships`: la lista de campeonatos está vacía → mensaje "No tienes campeonatos."; el selector queda **deshabilitado**.
- Acciones: `load()` (carga campeonatos; si `fetchChampionships()` lanza → estado `error`, sin alterar el activo persistido, FR4.2; si la lista está vacía → `noChampionships`; si no, resuelve el activo con `ActiveChampionshipResolver`, persiste vía `setActive` si cambió — owner FR3.3 — luego carga balances → `loaded`/`emptyTeams`/`error`); `selectChampionship(_:)` (persiste + recarga); `setSort(_:)` (reordena con `TeamBudgetSort` **sólo cuando el estado es `loaded`**; en otros estados guarda `sortKey` para la próxima carga, sin efecto visible). (FR1.1, FR2.1, FR3.2, FR4.1, FR4.2)

### `BudgetView`
- Dentro de `NavigationStack`; `.toolbar` con el título = menú selector (`ChampionshipMenu`) y el menú de orden. Cuerpo según estado: `LoadingState` / `ErrorState` (componentes F1) / `emptyTeams` (mensaje "Este campeonato no tiene equipos aún.") / `noChampionships` (mensaje "No tienes campeonatos." + selector deshabilitado) / `List` de `BudgetRow`. (US1, FR4)

### `BudgetRow`
- Fila por equipo: `team_name` (DSFont h3), `balance` y `performance` con `DSColor.moneyPositive/Negative` vía `MoneyFormatter.format(signed:)`, `max_bid` y `prizes` secundarios. Label VoiceOver compuesto. (FR1.2, FR1.3, NFR5)

### `ChampionshipMenu`
- `Menu` en el título de la navigation bar: lista de campeonatos (activo con ✓); al elegir llama `viewModel.selectChampionship`. Deshabilitado si la lista está vacía. (FR3.1)

## Verificación

- `swift build` compila (guardado con `#if canImport(SwiftUI)`); no hay XCTest de vistas en WSL (cobertura no fiable). Validación de render/accesibilidad/fidelidad en iPhone 13 Pro (NFR3, NFR4, NFR5).
- La lógica orquestada por el VM que sea pura se apoya en U1 (ya testeada); el VM es fino.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/components.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/refined-mockups/{mockups.md,interaction-spec.md,design-system-mapping.md,accessibility-checklist.md}`
- `ios/Sources/FutmondoKit/Budget/*` (U1), `ios/Sources/FutmondoApp/DesignSystem/*` (F1)

## Assumptions & Open Questions

None.
