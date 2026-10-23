# Code Summary — U2 `u2-login-theming`

> Fase: construcción. Idioma: prosa en castellano; identificadores/comentarios en INGLÉS.
> Unit UI-only: reviste `LoginView` de F1 con la librería `DesignSystem` (U1) SIN cambiar comportamiento, layout ni la API pública.

## Ficheros modificados

| Fichero | Cambio |
|---------|--------|
| `ios/Sources/FutmondoApp/LoginView.swift` | Revestido in-place con componentes y tokens de U1. Única modificación de código. |

No se tocó `AuthViewModel.swift`, `AuthService`, `KeychainTokenStore`, `TokenHolder` ni ningún tipo de `FutmondoKit` (NFR2.5). No se tocó la API pública de U1 (`DesignSystem`).

## Equivalencia aplicada (antes → después)

| Elemento F1 (antes) | Componente/token U1 (después) | Comportamiento |
|---------------------|-------------------------------|----------------|
| `TextField("Email")` inline | `TextInputField(label:"Email", icon: envelope)` + modifiers de F1 | idéntico (binding `viewModel.email`) |
| `SecureField`/`TextField` password + botón ojo | campo F1 re-skinned con tokens U1 (ver nota de contrato) | idéntico (binding `viewModel.password`, toggle local) |
| `.buttonStyle(.borderedProminent)` | `PrimaryButton(title:isLoading:isEnabled:action:)` | idéntico (`isEnabled=canSubmit`, `isLoading=(state==.loading)`, `submitLogin`) |
| banner de error `.red` ad-hoc | `ErrorState(message:)` (icono+texto, token) | idéntico (muestra `message` de `.error`) |
| card `.ultraThinMaterial` | `Card { ... }` (superficie con token `surface`) | mismo rol de contenedor |
| `.font(.title2.bold())` título | `DSFont.h1` | token de tipografía |
| espaciados literales (`20`, `16`, `24`) | `DSSpacingSwiftUI.lg` / `.md` / `.sm` | tokens de espaciado |
| colores implícitos | `DSColor.primary` / `.onSurface` / `.onSurfaceVariant` | tokens de color (claro/oscuro auto) |

## Comportamiento preservado EXACTAMENTE (F1)

- API pública intacta: `public init(viewModel: AuthViewModel, logoNamespace: Namespace.ID)`.
- Logo `sportscourt.fill` con `matchedGeometryEffect(id:"logo", in: logoNamespace)`.
- `ShakeEffect` en error, suprimido bajo Reduce Motion (no se anima `shakeTrigger`).
- `sensoryFeedback(.success / .error)` bajo `#if os(iOS)`.
- Focus email→password con `@FocusState private var focusedField` y `submitLabel`/`onSubmit`.
- `textContentType`, `keyboardType(.emailAddress)`, `textInputAutocapitalization(.never)`, `disableAutocorrection(true)`.
- Labels de accesibilidad ("Email", "Contraseña", "Iniciar sesión", toggle del ojo).
- Guards `#if canImport(SwiftUI) && canImport(Observation)` conservados.
- NO se añadió fondo de gradiente ni subtítulo (F1 no los tiene).

## Notas de contrato U1 ↔ U2 (desviaciones justificadas, sin cambiar la API de U1)

1. **Campo password — toggle de visibilidad conservado de F1.** La superficie pública de U1 `TextInputField(label, text, icon, isSecure, errorMessage?)` encapsula su **propio** `@FocusState` interno y, en modo `isSecure`, su **propio** botón de visibilidad (estado interno `isRevealed`). F1 necesita: (a) un `@FocusState` externo compartido para la cadena email→password→submit, (b) el toggle local `isPasswordVisible`, y (c) `.onSubmit` que dispara `submitLogin()`. Enrutar el password por `TextInputField(isSecure:)` duplicaría el botón ojo y rompería el focus/submit externos. Por tanto, **priorizando preservar el comportamiento de F1** (tal como indica la nota de contrato del functional-spec) y **sin cambiar la API pública de U1**, el campo de contraseña mantiene el patrón de F1 (`SecureField`↔`TextField` según `isPasswordVisible` + botón ojo), re-skinned con tokens U1 (`DSFont.body`, `DSColor`, `DSSpacingSwiftUI`, borde con `cornerRadius 8` como el de `TextInputField`). Mejora futura fuera de alcance: ampliar `TextInputField` de U1 con binding de visibilidad/focus externos.

2. **Campo email — modifiers de F1 aplicados sobre el componente U1.** El `TextInputField` de U1 no expone `keyboardType`/`textContentType`/autocorrección/`@FocusState`/`submitLabel`/`onSubmit`. Esas afordancias de F1 se preservan aplicando los modifiers SwiftUI **sobre** el `TextInputField`. **RIESGO ABIERTO (verificable sólo en dispositivo)**: el `TextField` interno del `TextInputField` tiene su propio `@FocusState` privado; que `.focused`/`.submitLabel`/`.onSubmit` aplicados sobre el componente compuesto enlacen con ese campo interno y conserven la cadena de foco email→password→submit (FR6.2) NO es verificable con `swift test` en WSL y debe confirmarse en el iPhone 13 Pro. Si en dispositivo la cadena de foco no funciona, la mejora es exponer un binding de foco externo en la API de `TextInputField` de U1 (fuera de alcance de este intent). No se cambió la API pública de U1.

## Verificación

- `cd ios && swift build` → **Build complete** (compila `FutmondoApp/LoginView.swift`).
- `cd ios && swift test` → **43 tests, 0 fallos** (29 F1 + 14 U1), **sin regresión**.
- La no-regresión funcional del login (login → auto-login Keychain → logout) y el aspecto claro/oscuro + Dynamic Type se validan manualmente en dispositivo (iPhone 13 Pro): la cobertura line vía llvm-cov no es medible de forma fiable en WSL y las vistas SwiftUI se validan en dispositivo (aprendizaje durable del proyecto).

## Testing Contract

test-after; sin tests nuevos (UI-only, `AuthViewModel` ya cubierto por F1). Obligación: suite existente en verde. No se relajó ningún umbral/piso.
