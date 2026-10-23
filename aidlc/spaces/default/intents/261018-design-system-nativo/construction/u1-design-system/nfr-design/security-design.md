# Security Design — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> Diseño de seguridad de una librería de presentación SwiftUI in-process. Deriva de security-requirements (NFR2.1–2.3).

## Diseño

- **Sin superficie de red ni persistencia**: la librería no abre sockets, no escribe a disco ni a Keychain, no lee variables de entorno ni secretos. No hay vector que diseñar más allá de mantener esa ausencia. (NFR2.2) [security-requirements]
- **Campo secure (`TextInputField`, isSecure)**: se implementa con `SecureField` de SwiftUI; el texto vive sólo en el `Binding` que provee el consumidor. El toggle de visibilidad conmuta entre `SecureField` y `TextField` sin registrar ni copiar el valor a ningún almacén. (NFR2.3 → FR4.2) [security-requirements]
- **Dependencias**: cero dependencias externas; sólo SDK de Apple. No hay cadena de suministro que endurecer en esta Unit. (NFR2.1)

## No aplica

Autenticación, autorización, cifrado en reposo/tránsito, gestión de secretos: ninguno aplica a una capa de presentación. El login (U2) reutiliza la auth de F1 sin cambios; la regla durable de no credenciales en claro se preserva y no la toca esta Unit.

## Assumptions & Open Questions

None.
