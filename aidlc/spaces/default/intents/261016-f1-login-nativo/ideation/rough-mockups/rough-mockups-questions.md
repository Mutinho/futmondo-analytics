# Rough Mockups — Preguntas (F1: Login nativo)

> Idioma: castellano; tokens técnicos verbatim en inglés. La UI de F1 se limita a la pantalla de
> Login y el Splash de auto-login (el resto de F1 no tiene UI). Los wireframes espejan la PWA en
> controles nativos SwiftUI.

## Q1 — ¿Los wireframes y los flujos de auth son correctos para F1?

- A. **Correctos** — login + splash de auto-login + flujos (login, refresh ante 401 con un
  reintento, logout) tal como se describen (recomendado).
- B. Correctos con un ajuste (especifícalo: p. ej. añadir biometría/FaceID para desbloquear el
  Keychain, o un recordatorio de sesión).
- C. Replantear la UX (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar rough-mockups, confirma la UX de F1:

- **Pantallas**: Splash de recuperación de sesión (auto-login por refresh token del Keychain) y
  Login (email/password, estados de carga/error, toggle de visibilidad de contraseña).
- **Flujos**: arranque/auto-login; login manual; refresh ante 401 con un reintento y re-login si
  el refresh falla; logout (revoca en backend + borra Keychain + vuelve a Login).
- **Polish nativo (dentro de F1, SwiftUI puro, 0 dependencias externas)**: animaciones
  (`matchedGeometryEffect`, `symbolEffect`, transiciones), inputs con autorrelleno de contraseña
  (`.textContentType`) y foco (`@FocusState`), feedback háptico (`.sensoryFeedback`), materiales
  (`.ultraThinMaterial`), respetando Reduce Motion / Dynamic Type / VoiceOver.
- **Face ID / Touch ID**: mejora opcional **diferida** (fuera de F1); amplía B-03 y se decide en
  un intent posterior.
- **Alcance de UI**: sólo login/splash; el resto de F1 (cliente de red, Keychain, ajuste de
  backend) no tiene UI; las pantallas de datos son F2.
- **Accesibilidad**: labels por campo, contraste suficiente, toggle con etiqueta accesible, orden
  de foco Email → Contraseña → Iniciar sesión.

¿Está todo correcto?

[Answer]: Looks correct
