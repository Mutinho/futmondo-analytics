# Security Design — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

- **NFR2.4 (campo secure)**: el campo de contraseña mantiene `SecureField` por defecto; el toggle de visibilidad conmuta `SecureField`↔`TextField` con estado local `isPasswordVisible`, sin copiar ni persistir el valor (vive sólo en `viewModel.password`).
- **NFR2.5 (no tocar auth de F1)**: U2 sólo reemplaza vistas; `AuthService`, `KeychainTokenStore`, `TokenHolder` y el borrado de password (SEC-A3) de F1 quedan intactos. Diseño: U2 no importa ni modifica esos tipos, sólo bindea a `AuthViewModel`.
- **NFR2.6 (mensajes sin credenciales)**: `ErrorState` muestra `viewModel.state`'s message, producido por `AuthViewModel.message(for:)` de F1 (textos en castellano sin material de credencial).

Sin superficie de red ni persistencia nueva.

## Assumptions & Open Questions

None.
