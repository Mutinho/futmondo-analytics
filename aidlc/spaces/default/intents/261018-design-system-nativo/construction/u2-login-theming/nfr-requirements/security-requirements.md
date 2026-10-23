# Security Requirements — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> Revestimiento del login; la seguridad de auth vive en F1 (AuthService/Keychain), U2 no la toca.

| ID | Requisito | Fuente |
|----|-----------|--------|
| NFR2.4 | El campo de contraseña sigue usando `SecureField` (texto oculto por defecto); el toggle de visibilidad es acción local del usuario, sin registrar ni persistir el valor. | FR4.2 / security-design U1 |
| NFR2.5 | U2 NO modifica el manejo de credenciales ni tokens de F1: `AuthService`, `KeychainTokenStore` y el borrado de password tras login/logout (SEC-A3) quedan intactos. Se preserva la regla durable de no credenciales en claro. | memory:project.md |
| NFR2.6 | El mensaje de error mostrado (`ErrorState`) usa los textos de `AuthViewModel.message(for:)` de F1, que no incluyen material de credencial. | memory:project.md |

## Assumptions & Open Questions

None.
