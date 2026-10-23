# Frontend Components — U2 `u2-login-theming` (SwiftUI)

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés. Nivel de diseño. Reviste `LoginView` de F1 sin cambiar layout ni comportamiento.

## Jerarquía (LoginView revestido — misma estructura que F1)

```
LoginView (F1, revestido — misma API pública: init(viewModel:logoNamespace:))
├── logo (sportscourt.fill, matchedGeometryEffect, sin cambios)
├── Title "Futmondo Analytics" → DSFont.h1
└── Card (U1, sustituye .ultraThinMaterial)
    ├── ErrorState (U1) — visible si state == .error
    ├── TextInputField (U1) — Email (icono, teclado email, autofill)
    ├── password field — TextInputField(isSecure:) de U1 + botón ojo conservado de F1 (isPasswordVisible local)
    └── PrimaryButton (U1) — "Iniciar sesión" (isEnabled=canSubmit, isLoading)
```

No se añade fondo de gradiente (F1 no lo tiene) ni subtítulo. Se conservan `ShakeEffect`, `sensoryFeedback`, focus, autofill.

## Props / estado

- `LoginView` conserva su init, su `@Bindable AuthViewModel` y su estado local `isPasswordVisible` (para el botón ojo, no cubierto por la superficie de U1).
- Componentes de U1: `TextInputField(label, text: binding, icon, isSecure, errorMessage?)`, `PrimaryButton(title, action, isLoading, isEnabled)`, `ErrorState(message)`, `Card { ... }`.

## Flujos de interacción

Idénticos a F1: focus email→password, submit (`submitLogin`), toggle de visibilidad (botón ojo de F1), shake en error bajo Reduce Motion, haptics. Sólo cambia la capa visual (tokens + componentes).

## Validación de formularios

`canSubmit` lo aporta `AuthViewModel` (F1); `TextInputField` sólo presenta `errorMessage`. Sin cambios de lógica.

## Integración con API

Ninguna nueva: `submitLogin()`/`logout()` de F1 intactos.

## Assumptions & Open Questions

- [assumption] El botón de visibilidad del password se conserva con el patrón de F1 (la superficie pública de U1 no lo expone). [contract-summary]
