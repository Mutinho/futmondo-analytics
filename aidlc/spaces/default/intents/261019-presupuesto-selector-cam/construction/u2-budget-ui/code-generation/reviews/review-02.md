## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T10:32:24Z
**Iteration:** 1

Revisión adversarial del estado FINAL reworkeado de `u2-budget-ui` (capa de
presentación SwiftUI del presupuesto + selector + detalle de equipo FR6). Se
intentó refutar cada reclamo del brief rastreando contratos, máquinas de estado,
seam F1, guardas de disponibilidad y accesibilidad. No se encontró ningún
defecto que bloquee: el código es implementable y coherente con U1/F1 y con los
contratos de inception y codekb.

### Rationale

- **FR6 consume el endpoint U1 con la misma garantía typed-error/no-leak.**
  `HTTPBudgetService.fetchTeamDetail` construye
  `GET /api/v1/analytics/balances/{team_id}?championship_id=<id>` sobre el mismo
  `NetworkClient`, con idéntico patrón `Result<…, NetworkError>` → `throw` que
  `fetchBalances`; el `NetworkError` tipado no hace eco de URL/query (SR1),
  reforzado por `BudgetServiceTests` 6–8 (decode de opcionales `from`/`to`, error
  propagado, y aserción explícita de no-fuga de `team_id`/`championship_id`). El
  endpoint y la forma `TeamDetailResponse`/`Transaction` están confirmados en el
  codekb `api-documentation.md`. Integración resuelta.
- **Máquinas de estado sanas.** `BudgetViewModel` fija `.loading` síncrono antes
  del `await`, va a `.error` **sin** tocar `activeStore` ante fallo de
  championships (FR4.2), persiste el activo sólo al cambiar (FR3.3), y cubre
  `emptyTeams`/`noChampionships`. `TeamDetailViewModel` guarda el caso sin activo
  y toma el error verbatim de U1 sin interpolar ids (SR1). Sin estados muertos.
- **Seam F1 y sesión intactos.** `SplashView.case .resumed` presenta
  `RootTabView`; el closure de logout ejecuta el mismo `viewModel.logout();
  phase = .noSession`. `runBootstrap`, `.onChange`, `.checking/.offline/.expired/
  .noSession` sin cambios. El `NetworkClient` HTTPS único se comparte a los
  servicios de presupuesto/detalle (AR8/SEC-N1); no se crea un segundo cliente.
- **Dark global.** `.preferredColorScheme(.dark)` en el contenido del
  `WindowGroup`, sin tocar lógica de auth.
- **Cards/botones/fondo en la dirección aprobada.** `NeonGlassCard` (negro 0.45
  sobre `.ultraThinMaterial`, borde/halo neón-verde), `DSGlassIcon` blanco en
  habilitado, `AuthenticatedBackground` vía `Bundle.module` con degradado sólido
  seguro si el recurso no resuelve (sin crash/blanco).
- **APIs iOS 18/26 y háptica guardadas.** Zoom (`matchedTransitionSource` /
  `navigationTransition(.zoom)`) bajo `#available(iOS 18)` con fallback a push;
  `Tab` API iOS 18 con fallback `tabItem`; `UIImpactFeedbackGenerator` bajo
  `#if canImport(UIKit)` dentro del floor iOS 17; `.contentTransition(.numericText())`
  iOS 16+ bajo el floor del struct.
- **`FutmondoKit.Transaction` cualificado** en `TeamDetailTransactionRow`,
  evitando el choque con `SwiftUI.Transaction`.
- **Sin deps SwiftPM nuevas.** `dependencies: []`; `Package.swift` sólo añadió
  `.iOS("26.0")` y el recurso `background.jpg`.
- **Accesibilidad preservada.** Labels VoiceOver compuestos (filas, summary,
  controles), foco a Reintentar, Dynamic Type vía `DSFont`, signo como portador
  no-cromático, Reduce Motion honrado, y contraste ≥4.5:1 validado por
  `testDarkNeonGlassCardTextMeetsContrast` sobre `cardSurfaceDark`.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | ios/Sources/FutmondoApp/Budget/BudgetViewModel.swift > selectChampionship(_:) | El método hace early-return si se vuelve a elegir el campeonato ya activo (no persiste ni recarga). Es una optimización razonable, pero el usuario no obtiene refresco si pulsa el campeonato activo tras un error previo; el spec describe "persiste + recarga" sin ese guard. | Confirmar en validación en dispositivo que, estando en `.error`, pulsar de nuevo el campeonato activo ofrece una vía de recarga (el botón Reintentar ya la cubre); si no, considerar permitir recarga aunque el id no cambie. No bloqueante. | Accepted risk |
| R-02 | Minor | ios/Tests/FutmondoKitTests/BudgetServiceTests.swift > FakeBudgetNetworkClient.send | El doble de red casa por prefijo con `handlers.first { … }` sobre un diccionario (orden no determinista); `"/api/v1/analytics/balances"` es prefijo de `"/api/v1/analytics/balances/"`, así que registrar ambas salidas a la vez podría enrutar la equivocada. Hoy cada test registra una sola salida, por lo que no hay fallo real. | Si en el futuro un test registra ambos prefijos, casar por el prefijo más largo (o por ruta exacta) para evitar ambigüedad. Sin acción obligatoria ahora. | New |
| R-03 | Minor | aidlc/spaces/default/codekb/futmondo-analytics/api-documentation.md > GET /api/v1/analytics/balances/{team_id} | El codekb anota que el cuerpo del handler de detalle no se transcribió campo a campo; la presencia de `success`/`initial_budget` en `TeamDetailResponse` se infiere del modelo Angular. El decode tolera ausencias sólo donde el campo es opcional (`from`/`to`); un `success`/`initial_budget` ausente en el wire real haría fallar el decode (que degrada limpio a `.error`, sin fuga). | Confirmar los campos requeridos contra el handler real del backend en la validación en dispositivo; si el servidor omite alguno, relajarlo a opcional en el DTO. Advisory. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| swift build (reportado) | Build complete; `canImport(SwiftUI)` verdadero → target `FutmondoApp` type-chequeado entero | Verificación de compilación fuerte del código nuevo de U2 (más allá del mínimo `FutmondoKit`) |
| swift test (reportado) | 105 tests, 0 failures (94 previos + 11 FR6) | Sin regresión de U1/F1; la lógica pura extraída (DTOs, fecha, contraste, presentación de orden) cubierta |

### Summary

El estado final de `u2-budget-ui` es sólido e implementable: FR6 se apoya en el
contrato U1 verificado con la misma garantía de no-fuga, las máquinas de estado
y el seam F1 son correctos, las APIs modernas están bien guardadas y la
accesibilidad/contraste se preservan. Las dos observaciones son advisory y no
bloquean.

**Verdict: READY**
