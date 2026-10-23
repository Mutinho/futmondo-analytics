## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T07:34:46Z
**Iteration:** 2

### Rationale

Segunda pasada (final) adversarial del NFR Design de `u2-budget-ui`
(logical-components + security-design + performance-design) más la
functional-spec, contrastada contra la fuente real
`ios/Sources/FutmondoApp/SplashView.swift`. La iteración 1 fue NOT-READY por dos
findings Major de integración y uno Minor; verifico cada uno contra el código F1.

**Costura de integración (Major #1) — Fixed.** El código real confirma que la
raíz es `SplashView` (no `FutmondoApp.swift`), que la superficie autenticada se
decide en `content` → `case .resumed`, y que ese caso hoy renderiza
`authenticatedPlaceholder`. logical-components y functional-spec ahora nombran
esa costura exacta: F2 sustituye **el cuerpo de `case .resumed`** por
`RootTabView`, dejando intactos `runBootstrap()`, el
`.onChange(of: viewModel.state)` que enruta `.success → .resumed` y las demás
fases (`.checking`, `.offline`, `.expired`, `.noSession`). Coincide con la
fuente carácter por carácter; un desarrollador no tiene que adivinar.

**Re-homing del logout (Major #2) — Fixed.** El código confirma el único punto
de logout dentro de `authenticatedPlaceholder`
(`await viewModel.logout(); phase = .noSession`). Ambos artefactos ahora
re-alojan ese camino dentro de `RootTabView`, invocando **el mismo**
`AuthViewModel.logout()` y fijando `phase = .noSession` vía callback/binding
desde `SplashView`. La lógica de sesión de F1 (bootstrap, auto-login, logout)
queda intacta; sólo cambia dónde se aloja el botón. Riesgo de integración de
sesión resuelto.

**Criterio de performance (Minor #3) — Fixed.** performance-design ahora
expone un criterio comprobable en dispositivo (iPhone 13 Pro): (a) scroll sin
frames perdidos perceptibles como proxy de 60 fps (contrastable con el FPS debug
gauge de Instruments), (b) spinner visible antes de ~100 ms tras tocar un
campeonato distinto, registrado en Performance Validation. Honesto dado que la
medición numérica no es fiable en WSL.

Seguridad (SR1-SR3) se mantiene sólida y sin cambios respecto a la pasada 1:
el VM depende sólo de los protocolos públicos de U1, reexpone el
`localizedDescription` verbatim sin interpolar datos de petición, y no abre
superficie de red nueva. Sin ruta residual de fuga de credenciales.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/logical-components.md > sección "Ubicación", viñeta "la raíz pasa a RootTabView tras el login" | El diseño dice que la raíz (`FutmondoApp.swift`) pasa a `RootTabView` tras el login, pero la raíz real arranca en `SplashView` y la pantalla autenticada se decide dentro de `SplashView.content`, en el caso `.resumed`, que hoy muestra `authenticatedPlaceholder`. El diseño no nombra esa costura concreta, así que un desarrollador tendría que adivinar dónde y cómo inyectar `RootTabView` sin tocar `FutmondoApp.swift`. | Documentar que la integración sustituye el contenido del caso `.resumed` de `SplashView` (hoy `authenticatedPlaceholder`) por `RootTabView`, dejando intactos `runBootstrap()`, la transición `onChange(state == .success → phase = .resumed)` y los casos `.offline/.expired/.noSession`. | Resolved (reviewer) |
| R-02 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/logical-components.md > viñeta "reutilizando AuthViewModel/SplashView de F1 sin cambiar la lógica de sesión" | El único punto de entrada al logout (`viewModel.logout()` seguido de `phase = .noSession`) vive hoy dentro de `authenticatedPlaceholder`, la misma vista que `RootTabView` reemplazaría. El diseño afirma "sin cambiar la lógica de sesión" pero no explica cómo se preserva ese camino de logout al introducir el `TabView`; omitirlo rompería el cierre de sesión de F1. | Especificar que el camino de logout se re-ubica dentro de la UI de `RootTabView` (o se expone al VM/vista contenedora), invocando el mismo `AuthViewModel.logout()` y la misma vuelta a `phase = .noSession`, de modo que el cierre de sesión de F1 siga operativo tras la integración. | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/performance-design.md > sección "Verificación" | PR1/PR2 se verifican sólo por observación en dispositivo ("scroll sin jank"; "aparición inmediata del spinner"), sin criterio comprobable registrado; es aceptable dado WSL, pero queda como afirmación no medible. | Registrar el criterio de validación en dispositivo de forma explícita (p. ej. ausencia de dropped frames en el scroll y spinner visible en el primer frame tras la acción) como checklist de validación manual, o marcarlo TBD con responsable. | Resolved (reviewer) |

> R-01 Reviewer note: logical-components + functional-spec nombran la costura exacta (`SplashView.content` → `case .resumed`, hoy `authenticatedPlaceholder`, sustituido por `RootTabView`); coincide con `SplashView.swift` real, con `runBootstrap`/`onChange`/otras fases intactas.

> R-02 Reviewer note: Logout re-alojado en `RootTabView` invocando el mismo `AuthViewModel.logout()` y `phase = .noSession` vía callback/binding desde `SplashView`; preserva el camino de sesión F1.

> R-03 Reviewer note: performance-design fija criterio comprobable en dispositivo (scroll sin jank perceptible + spinner <~100 ms), con gauge de Instruments opcional; registrado en Performance Validation.

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|

### Summary

Los dos Major de integración (costura `.resumed` y re-homing del logout) y el
Minor de performance quedan resueltos y verificados contra el `SplashView.swift`
real; sin Critical ni Major abiertos, el diseño es implementable sin guía
arquitectónica adicional.
