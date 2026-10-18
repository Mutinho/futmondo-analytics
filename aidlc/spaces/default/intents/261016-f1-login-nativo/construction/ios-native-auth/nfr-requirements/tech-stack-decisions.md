# NFR — Tech Stack Decisions (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## TSD-A1 — Solo SDK de Apple + FutmondoKit
`Security` (Keychain Services), `SwiftUI`, `Foundation`, Swift concurrency (`actor`), y el
`FutmondoKit.NetworkClient` del Bolt 2. **Cero** dependencias SPM externas (NFR-2/P-3).
`LocalAuthentication` (Face ID) **diferido**, fuera de F1.

## TSD-A2 — Swift concurrency
`AuthService` es un `actor`; el estado de UI usa `@Observable` (iOS 17+) u `ObservableObject`
según el target mínimo del paquete (se fija en code-generation). El snapshot del token para el
provider del `NetworkClient` usa un holder con lock (`OSAllocatedUnfairLock` o equivalente).

## TSD-A3 — Verificación swift test + manual
`swift test` cubre `AuthService` con dobles de `NetworkClient` y `KeychainStore` in-memory
(ejecutado por el propietario en WSL, como el Bolt 2). El `KeychainTokenStore` real (`SecItem`) y
la UI se validan en el iPhone 13 Pro con xtool.

## Sources
- [consumes] technology-stack.md, functional-spec.md, team-practices (P-1, P-3).

## Assumptions & Open Questions
None.
