# Integration Test Instructions — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Idioma: castellano; identificadores/código en inglés.

## Integración cubierta por tests automáticos

- **Backend (pytest)**: login/refresh/logout por **ambos canales** (cookie y header/body),
  precedencia observable, borde cookie-revocada, revocación en logout — con `TestClient` de
  FastAPI (integración HTTP real contra el router de auth).
- **iOS (swift test)**: `NetworkClient` con `URLProtocol` stub (integración del pipeline HTTP);
  `AuthService` con dobles de `NetworkClient` y `KeychainStore` (integración de la orquestación de
  sesión: login→Keychain, bootstrap, refresh coalescido, logout).

## Integración end-to-end real (validación manual del propietario, en el iPhone)

El flujo completo app nativa ↔ backend (login real contra `futmondo-api`, refresh por header,
logout) se valida en el dispositivo con `xtool dev build`. Requiere el backend desplegado con el
ajuste D-01 y la app firmada. Es la verificación de integración E2E que cierra NFR-3; el arnés E2E
automatizado queda como deuda (P-1).

## Sources
- [consumes] test-instructions de los bolts; functional-spec de cada bolt.

## Assumptions & Open Questions
None.
