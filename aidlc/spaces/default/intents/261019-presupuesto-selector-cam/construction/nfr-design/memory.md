<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T17:56Z — NFR Design U1: diseño de seguridad (SR1 error sin URL/query, test de no-fuga; SR2 UserDefaults sólo id; SR3 HTTPS heredado; SR4 decode estricto), sin superficie nueva. Componentes lógicos en `FutmondoKit/Budget/` (12 ficheros) sin tocar Networking/Auth/DesignSystem salvo consumo. Rendimiento NO-APLICA (listas cortas O(n)); fluidez de render es de U2.
- 2026-10-20T09:28Z — NFR Design U2: performance (List/LazyVStack render perezoso 60fps; loading síncrono `@MainActor` antes del await <100ms); seguridad (VM depende sólo de protocolos públicos de U1, nunca NetworkClient/AuthService; error verbatim de U1 sin interpolar; UserDefaults vía store de U1; sin red nueva). Componentes en `FutmondoApp/Budget/` (6 ficheros), integrados con `FutmondoApp.swift` (raíz → RootTabView tras login, AuthViewModel/SplashView de F1 intactos); impls de U1 inyectadas en el punto de entrada.
- 2026-10-20T09:30Z — Review adversarial U2 nfr-design iteración 1 = NOT-READY (2 Major de integración + 1 Minor). Tras LEER `FutmondoApp.swift`/`SplashView.swift` reales: corregido el seam exacto (la raíz es `SplashView`; la superficie autenticada es `case .resumed` → hoy `authenticatedPlaceholder`; F2 sustituye ese cuerpo por `RootTabView`, dejando runBootstrap/onChange/otras fases intactas) y el re-homing del logout (mismo `AuthViewModel.logout()` + `phase=.noSession` vía callback). Minor: criterio de performance comprobable (observación + opcional Instruments). functional-spec de `RootTabView` actualizado en consecuencia. Re-pase iteración 2.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
