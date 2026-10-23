# Logical Components — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

U2 no introduce componentes lógicos nuevos: modifica `LoginView` (FutmondoApp) para consumir la librería `DesignSystem` (U1).

```
FutmondoApp
└── LoginView.swift (modificado in-place)
    ├── import de DesignSystem (U1): DSColor, DSFont, DSSpacing, PrimaryButton, TextInputField, ErrorState, Card
    ├── mantiene @Bindable AuthViewModel (F1) y estado local isPasswordVisible
    └── sin cambios en AuthViewModel / AuthService / Keychain (F1)
```

## Resolución de NFR por diseño

| NFR | Cómo se cumple |
|-----|----------------|
| NFR4.1/4.2 | vistas SwiftUI ligeras de U1; loading derivado del estado del viewModel |
| NFR2.4 | SecureField + toggle local |
| NFR2.5 | U2 no importa ni modifica AuthService/Keychain |
| NFR2.6 | mensajes de `AuthViewModel.message(for:)` de F1 |

## Assumptions & Open Questions

None.
