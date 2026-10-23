# Security Test Instructions — Sistema de diseño nativo iOS

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

La capa de diseño no maneja datos ni credenciales; el login revestido (U2) NO modifica `AuthService`/`KeychainTokenStore` de F1. Los NFR de seguridad son de preservación (NFR2.4 SecureField, NFR2.5 no tocar auth de F1, NFR2.6 mensajes sin credenciales).

## Verificación

- **SecureField (NFR2.4)**: inspección de código — el campo password usa `SecureField` por defecto; el toggle de visibilidad es estado local, sin persistir el valor.
- **Auth de F1 intacto (NFR2.5)**: el `source-manifest.json` de U2 lista SÓLO `LoginView.swift`; `AuthService`/`KeychainTokenStore`/`AuthViewModel` no aparecen (no modificados). La suite de auth de F1 (29 tests) sigue verde.
- **Mensajes (NFR2.6)**: los mensajes de error provienen de `AuthViewModel.message(for:)` de F1 (sin material de credencial).
- **Supply chain**: cero dependencias nuevas en `Package.swift` (sólo SDK de Apple).

Sin SAST/DAST de pago (coste 0 €); la verificación es inspección + suite existente.

## Assumptions & Open Questions

None.
