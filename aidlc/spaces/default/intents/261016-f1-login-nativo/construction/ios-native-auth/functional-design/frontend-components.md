# Functional Design — Frontend Components (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés. Único bolt con UI (kind
> `ui`). Fuente: refined-mockups (mockups/interaction-spec/design-system-mapping/accessibility).

## `SplashView`
- Estados (interaction-spec): checking / resumed / expired / offline / no-session.
- Logo con `matchedGeometryEffect(id:"logo")`; `ProgressView` + "Recuperando sesión…"; en fallo de
  red muestra banner breve y cae a Login (no cuelga).
- Observa `AuthViewModel`/`AuthService.bootstrap()` al aparecer.

## `LoginView`
- Campos: `TextField` email (`.textContentType(.username)`, teclado email), `SecureField`
  contraseña (`.textContentType(.password)`, toggle de visibilidad con `symbolEffect`).
- Botón "Iniciar sesión": deshabilitado en idle (campos vacíos) o loading; `ProgressView` inline;
  `.sensoryFeedback` success/error; shake del formulario en error (suprimido con Reduce Motion).
- Banner de error accionable (del `detail` del backend). Tarjeta `.ultraThinMaterial`.
- `@FocusState` Email → Contraseña; accesibilidad A1–A9 (labels, Dynamic Type, VoiceOver, Reduce
  Motion, contraste WCAG AA, error no solo por color, táctiles ≥44pt).

## `AuthViewModel`
- `@Observable` (o `ObservableObject`): `state: AuthState`, `email`, `password`.
- `submitLogin()` → `AuthService.login`; refleja estado; **no reintenta** (ADR-4).
- `logout()` → `AuthService.logout`.

## Logout en F1
Sin pantalla propia (B-08/navegación es F2); punto de entrada provisional que invoca
`AuthViewModel.logout()`.

## Sources
- [consumes] refined-mockups (mockups.md, interaction-spec.md, design-system-mapping.md,
  accessibility-checklist.md), components.md (C4, C5), requirements.md (FR-8).

## Assumptions & Open Questions
None.
