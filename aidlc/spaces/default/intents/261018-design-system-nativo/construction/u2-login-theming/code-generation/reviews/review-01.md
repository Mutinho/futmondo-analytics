## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T10:08:36Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | ios/Sources/FutmondoApp/LoginView.swift > emailField | El `.focused($focusedField, equals: .email)`, `.submitLabel(.next)` y `.onSubmit` se aplican sobre la vista compuesta `TextInputField`, no sobre el `TextField` interno (que tiene su propio `@FocusState private var isFocused` privado en `TextInputField.swift`). En SwiftUI el modifier `.focused` sólo enlaza con primitivas focusables reales (`TextField`/`SecureField`), no con un contenedor; el campo email puede no quedar enlazado a la cadena de foco email→password ni disparar `.onSubmit`, a diferencia del login de F1 donde los modifiers iban sobre el `TextField` desnudo. La nota de contrato nº2 (code-summary) afirma como hecho que "SwiftUI los propaga al `TextField` interno a través del entorno y la responder chain": esa propagación no está garantizada por la semántica de `.focused`/`@FocusState`. Es un riesgo de regresión de comportamiento (FR6.2) sólo verificable en dispositivo. | Verificar en dispositivo (iPhone 13 Pro) que al pulsar "next" en el email el foco salta a password; si no, exponer en la API pública de U1 `TextInputField` un binding de `@FocusState` externo (o `submitLabel`/`onSubmit`) para que el email entre en la cadena de foco, o degradar la nota de contrato nº2 a riesgo abierto en vez de afirmarla como hecho. | New |
| R-02 | Minor | ios/Sources/FutmondoApp/LoginView.swift > passwordField | El campo password re-skinned usa `cornerRadius 8` y borde focus/neutral replicando a mano el tratamiento de `TextInputField`; cualquier cambio futuro de token de borde en U1 no se propagará a este campo (duplicación de estilo). Honestamente documentado en la nota de contrato nº1 como límite de la API de U1, no oculta incumplimiento. | Registrar como deuda la mejora futura ya anotada (ampliar `TextInputField` de U1 con foco/visibilidad externos) para evitar la divergencia de estilo del borde. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| swift build (cd ios) | PASS: Build complete! | El revestimiento compila; `LoginView.swift` y los componentes U1 resuelven sus símbolos. |
| swift test (cd ios) | PASS: 43 tests, 0 failures | Sin regresión sobre la suite existente (29 F1 + 14 U1). Coincide con lo afirmado en code-summary (43/0). |
| git status / diff (ios) | Sólo `LoginView.swift` modificado | AuthViewModel/AuthService/KeychainTokenStore/TokenHolder intactos (NFR2.5); el resto de ficheros U1 son untracked de la unidad previa, no tocados por U2. |

### Summary

El revestimiento de U2 es honesto y de bajo riesgo: usa realmente `Card`, `ErrorState`, `PrimaryButton`, `TextInputField` (email) y los tokens `DSColor`/`DSFont`/`DSSpacingSwiftUI` con las APIs públicas de U1 verbatim; preserva la API pública (`init(viewModel:logoNamespace:)`), `AuthViewModel`, focus, `ShakeEffect` bajo Reduce Motion, `sensoryFeedback`, `matchedGeometryEffect` y labels de accesibilidad; no añade gradiente ni subtítulo; no toca AuthService/Keychain; `source-manifest.json` lista `LoginView.swift`; y `swift build` + `swift test` 43/0 se verificaron localmente. La única reserva arquitectónica es la propagación de `.focused`/`.onSubmit` sobre el `TextInputField` compuesto del email (riesgo de regresión de la cadena de foco, sólo verificable en dispositivo, y afirmada como hecho en una nota de contrato): un Major que no bloquea (un único Major, cero Critical).

READY
