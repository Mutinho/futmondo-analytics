## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T07:32:21Z
**Iteration:** 1

### Rationale

Revisión adversarial del NFR Design de `u2-budget-ui` (security-design +
performance-design + logical-components) contra SR1-SR3 / PR1-PR2 y contra la
integración real con F1 en `ios/Sources/FutmondoApp/`.

El diseño de **seguridad** es sólido y verificable: el `BudgetViewModel` depende
sólo de los protocolos públicos de U1 (`BudgetService`, `ChampionshipService`,
`ActiveChampionshipStore`), todos confirmados como tipos públicos reales. El
`HTTPBudgetService` sí lleva `championship_id` en el query de la ruta, pero la
no-fuga la garantiza el `NetworkError` tipado de U1 (no eco de URL/query) y el
VM reexpone el `localizedDescription` **verbatim sin interpolar** datos de
petición — SR1 se sostiene sin reabrir la cadena en U2. SR2 (`UserDefaults` sólo
el id vía `UserDefaultsActiveChampionshipStore`) y SR3 (sin superficie de red
nueva; todo pasa por el `NetworkClient` de F1) se cumplen. **No encuentro ruta
residual de fuga de credenciales** por el VM ni por el `ErrorState`.

El diseño de **performance** (lazy `List`/`LazyVStack`, `state = .loading`
síncrono en `@MainActor` antes del `await`) es correcto para PR1-PR2 y la
verificación en dispositivo (iPhone 13 Pro) es honesta dado que la cobertura no
es fiable en WSL.

El bloqueo está en **logical-components**: la afirmación de integración no se
corresponde con el punto de costura real de F1 y deja sin especificar la
preservación del logout.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/logical-components.md > sección "Ubicación", viñeta "la raíz pasa a RootTabView tras el login" | El diseño dice que la raíz (`FutmondoApp.swift`) pasa a `RootTabView` tras el login, pero la raíz real arranca en `SplashView` y la pantalla autenticada se decide dentro de `SplashView.content`, en el caso `.resumed`, que hoy muestra `authenticatedPlaceholder`. El diseño no nombra esa costura concreta, así que un desarrollador tendría que adivinar dónde y cómo inyectar `RootTabView` sin tocar `FutmondoApp.swift`. | Documentar que la integración sustituye el contenido del caso `.resumed` de `SplashView` (hoy `authenticatedPlaceholder`) por `RootTabView`, dejando intactos `runBootstrap()`, la transición `onChange(state == .success → phase = .resumed)` y los casos `.offline/.expired/.noSession`. | New |
| R-02 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/logical-components.md > viñeta "reutilizando AuthViewModel/SplashView de F1 sin cambiar la lógica de sesión" | El único punto de entrada al logout (`viewModel.logout()` seguido de `phase = .noSession`) vive hoy dentro de `authenticatedPlaceholder`, la misma vista que `RootTabView` reemplazaría. El diseño afirma "sin cambiar la lógica de sesión" pero no explica cómo se preserva ese camino de logout al introducir el `TabView`; omitirlo rompería el cierre de sesión de F1. | Especificar que el camino de logout se re-ubica dentro de la UI de `RootTabView` (o se expone al VM/vista contenedora), invocando el mismo `AuthViewModel.logout()` y la misma vuelta a `phase = .noSession`, de modo que el cierre de sesión de F1 siga operativo tras la integración. | New |
| R-03 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/performance-design.md > sección "Verificación" | PR1/PR2 se verifican sólo por observación en dispositivo ("scroll sin jank"; "aparición inmediata del spinner"), sin criterio comprobable registrado; es aceptable dado WSL, pero queda como afirmación no medible. | Registrar el criterio de validación en dispositivo de forma explícita (p. ej. ausencia de dropped frames en el scroll y spinner visible en el primer frame tras la acción) como checklist de validación manual, o marcarlo TBD con responsable. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|

### Summary

Seguridad y performance son sólidas y sin ruta de fuga; el bloqueo es la
integración con F1: logical-components describe una costura (`FutmondoApp.swift`
→ `RootTabView`) que no coincide con el punto real (`SplashView.content` caso
`.resumed`) y no especifica cómo se preserva el logout hoy alojado en
`authenticatedPlaceholder`, lo que es riesgo de integración de sesión.
