# Unit Test Instructions — `ios-native-auth` (Bolt 3 de F1)

> Fase: construcción (code-generation). Idioma: castellano; identificadores/código en inglés.

## Verificación

`swift test` (ejecutado por el propietario en WSL, Swift 6.4) cubre la lógica de `AuthService` con
dobles de `NetworkClient` y `KeychainStore` in-memory + `TokenHolder` (NSLock) — sin iPhone. El
`KeychainTokenStore` real (`SecItem`), las vistas SwiftUI y el flujo visual se validan en el iPhone
13 Pro con `xtool dev build`.

```bash
cd ios && swift test        # verificacion real del bolt (logica de AuthService)
cd ios && xtool dev build   # validacion end-to-end en el iPhone (UI, Keychain real, flujo)
```

## Tests (XCTest, ejecutables con swift test)

`AuthServiceTests.swift` con dobles:
- `login` OK → access en memoria + holder + refresh guardado en el KeychainStore doble; 401 →
  `.invalidCredentials` (password no retenido).
- `bootstrap`: con refresh en Keychain y refresh 200 → `.authenticated`; 401/revocado → borra
  Keychain → `.unauthenticated`; red/5xx → preserva Keychain → `.offlinePreserved`; sin token →
  `.unauthenticated`.
- `refresh` ante 401 con reintento único; **coalescing**: dos llamadas concurrentes comparten una
  sola operación de refresh (el doble de `NetworkClient` cuenta las invocaciones).
- `logout`: borra Keychain + access token en **ambas** ubicaciones (actor y `TokenHolder`); red
  caída → estado local limpio + `pendingLogoutRevocation == true`.
- `TokenHolder`: get/set bajo lock devuelve el último valor; nil tras logout.

## Testing Contract

Methodology: test-after. La lógica de `AuthService` cumple el piso de cobertura vía `swift test`;
las vistas y el Keychain real se validan en el dispositivo (deuda de arnés de dispositivo, P-1).
Solo SDK de Apple.

## Sources
- [consumes] functional-spec.md, requirements.md (NFR-3), team-practices (P-1).

## Assumptions & Open Questions
None.
