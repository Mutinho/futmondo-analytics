## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T07:52:39Z
**Iteration:** 1

### Rationale

Revisión adversarial del código generado de `u2-budget-ui` contra el `code-generation-plan`,
el `functional-spec` y los `nfr-design`. Entré asumiendo máquina de estados incompleta,
corrupción del activo persistido ante fallo, fuga de credenciales en el string de error, y
un seam de `SplashView` que rompiera la lógica de sesión de F1. Tracé el flujo completo
(login → resumed → budget → cambio/orden → vacío/error → logout) y verifiqué cada símbolo
cruzado de U1/F1. No encontré ningún defecto bloqueante: el código coincide con el plan
aprobado y las specs, la integración del seam preserva F1 verbatim, y el cliente HTTPS único
se hilvana sin segundo cliente inseguro.

### Hallazgos verificados (sin findings bloqueantes)

- **(a) Máquina de estados** — `BudgetState` cubre `loading/loaded/emptyTeams/noChampionships/error`
  (`BudgetViewModel.swift`). `state = .loading` se fija síncrono ANTES de todo `await` en `load()`
  y `selectChampionship()`. El `catch` de `fetchChampionships()` va a `.error(error.localizedDescription)`
  con `return` inmediato, SIN tocar `activeStore` (FR4.2). El string de error es el `localizedDescription`
  del `NetworkError` tipado de U1, verbatim, sin interpolar `championship_id` ni tokens (SR1); `NetworkError`
  no transporta material de credencial.
- **(b) load() resolución + persistencia condicional** — usa `ActiveChampionshipResolver.resolve(activeId:in:)`
  y persiste vía `activeStore.setActive` sólo cuando `ActiveChampionshipPersistence.shouldPersist(resolvedId:storedId:)`
  es `true` (resuelto no-nil y distinto del almacenado). FR3.3 correcto; un fallo transitorio que no cambia la
  resolución no churnea `UserDefaults`.
- **(c) selectChampionship / setSort** — `selectChampionship` persiste (`setActive`) y recarga (`loadBalances`);
  `setSort` reordena in-place con `TeamBudgetSort.sorted` SÓLO en `case .loaded`, en otros estados sólo guarda la
  clave. Correcto.
- **(d) BudgetRow / menús** — `performance` con `MoneyFormatter.format(signed: true)`, `balance/maxBid/prizes` con
  `signed: false` (`prizes==0 → "-"`); color de dinero vía `DSColor.moneyPositive/Negative`; label VoiceOver compuesto
  con `.accessibilityElement(children: .ignore)`; el signo acompaña siempre (palabras "positivo/negativo" + signo en el
  string), el color no es portador único (A7/NFR5). `ChampionshipMenu` con `.disabled(championships.isEmpty)` y checkmark
  en el activo. `SortMenu` expone las 6 claves de `SortKey` (coincide con las 6 `case` del enum) con checkmark.
- **(e) RootTabView** — `TabView` de una sola pestaña "Presupuesto" → `NavigationStack(BudgetView)`, recibe el VM y el
  closure `onLogout`; no toca lógica de sesión directamente.
- **(f) Seam de SplashView** — sólo el cuerpo de `case .resumed` cambia a `RootTabView`; el closure de logout ejecuta
  `await viewModel.logout()` + `phase = .noSession` (mismo seam F1). `runBootstrap()`, `.onChange(of: viewModel.state)`
  y los casos `.checking/.offline/.expired/.noSession` quedan intactos. El MISMO `NetworkClient` HTTPS construido en
  `FutmondoApp.init` se pasa a `SplashView(authService:networkClient:)` y se inyecta a `HTTPBudgetService`/`HTTPChampionshipService`;
  no se crea segundo cliente ni se debilita https-only (AR8/SEC-N1).
- **(g) Dependencias / ficheros intactos** — el `source-manifest.json` sólo escribe los 10 ficheros declarados; no toca
  `Package.swift`, `Networking/`, `Auth/`, `DesignSystem/`, `AuthViewModel` ni `LoginView`. Sin dependencias SwiftPM nuevas.
- **(h) Tests** — `ActiveChampionshipPersistenceTests` (5) aseveran efectos reales de `shouldPersist` (distinto, nil almacenado,
  iguales, nil resuelto, ambos nil); no son `assert True`.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | ios/Sources/FutmondoApp/Budget/BudgetViewModel.swift > selectChampionship(_:) | El método hace early-return si se vuelve a elegir el campeonato ya activo (no persiste ni recarga). Es una optimización razonable, pero el usuario no obtiene refresco si pulsa el campeonato activo tras un error previo; el spec describe "persiste + recarga" sin ese guard. | Confirmar en validación en dispositivo que, estando en `.error`, pulsar de nuevo el campeonato activo ofrece una vía de recarga (el botón Reintentar ya la cubre); si no, considerar permitir recarga aunque el id no cambie. No bloqueante. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| swift build && swift test (code-summary) | PASS: 87 tests, 0 failures | Compila la capa SwiftUI bajo `#if canImport(SwiftUI)` y no regresa los 82 tests de U1/F1; los 5 nuevos del helper de persistencia pasan. |
| cross-reference de símbolos U1/F1 | PASS | `SortKey` (6 casos), `MoneyFormatter.format(_:signed:)`, `TeamBudget`, `Championship.championshipId`, `ActiveChampionshipResolver.resolve`, `ActiveChampionshipStore.setActive/activeId`, `BudgetService.fetchBalances`, `ChampionshipService.fetchChampionships`, `BalancesResponse.teams`, `DSColor.moneyPositive/Negative`, `AuthViewModel.logout` resuelven a la forma reclamada. |

### Summary

El código de `u2-budget-ui` implementa fielmente el plan y las specs: máquina de estados completa con
`loading` síncrono y sin corromper el activo ante fallo, error verbatim sin fuga, persistencia condicional
(FR3.3), seam de `SplashView` que preserva la sesión F1 y reutiliza el único cliente HTTPS. Sólo un Minor
no bloqueante sobre el guard de reselección del campeonato activo. Sin Critical ni Major.

**Verdict: READY**
