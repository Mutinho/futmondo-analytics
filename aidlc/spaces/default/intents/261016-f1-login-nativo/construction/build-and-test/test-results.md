# Test Results — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Resultados reales verificados por el engine. Idioma:
> castellano; identificadores/código en inglés.

## Backend (`backend-refresh-transport`)

- Comando: `pytest -q` (venv efímero, `JWT_SECRET` efímero).
- Resultado: **422 passed, 3 xfailed** (los 3 xfail son LEGACY preexistentes, no de F1).
- Cobertura: 58,3% (sobre el piso heredado 27%; el ratchet solo sube).
- `ruff check`: limpio en los ficheros nuevos.
- Checkpoint de unidad: verificado y aprobado por el engine (exit 0).

## iOS lógica (`ios-network-client` + `ios-native-auth`)

- Comando: `cd ios && swift test`.
- Resultado: **28 passed, 0 failures** (14 NetworkClient + 14 AuthService).
- Checkpoints de unidad: ambos verificados y aprobados por el engine ejecutando `swift test`
  (exit 0).

## iOS dispositivo (validación manual — COMPLETADA por el propietario)

- `xtool dev build` + instalación en el iPhone 13 Pro vía `ios/scripts/install-app.sh`:
  **app instalada y arrancada correctamente**.
- Flujo F1 validado en dispositivo real: **login manual → "Sesión iniciada"**; **cerrar y
  reabrir la app → auto-login directo** (refresh token leído del Keychain, sin re-login) →
  **logout → vuelve a login**. FR-1/FR-3/FR-5/FR-6 confirmados end-to-end; NFR-3 cubierto.

### Fixes descubiertos al compilar/ejecutar con el SDK de Apple (post-review)

Estos fallos solo afloran con el toolchain/SDK de Apple (no en `swift test` de Linux ni en la
revisión por lectura); se corrigieron y re-verificaron (`swift test` 29 passed):
1. **Producto xtool**: `FutmondoApp` pasó de `.executable` a **`.library`** product (contrato de
   xtool: la app es una library) y se eliminó `main.swift` (su presencia forzaba target ejecutable).
2. **Swift 6 strict concurrency (build iOS)**: `NetworkClient`/`KeychainStore` marcados `Sendable`;
   `URLSessionNetworkClient` `@unchecked Sendable` + provider `@Sendable`; eliminado un duplicado de
   conformidad.
3. **URL malformada ("no se pudo conectar")**: `URLSessionNetworkClient` ya no usa
   `appendingPathComponent` (percent-encodeaba el path); construye `baseURL + path` normalizando la
   barra. **Test de regresión añadido** (`testRequestURLJoinsBaseAndPathCorrectly`).
4. **Navegación**: `SplashView` ahora reacciona al login manual (`AuthViewModel.state == .success`
   → `phase = .resumed`); antes se quedaba en el formulario tras un login correcto.
- Backend desplegado a Fly.io con el ajuste D-01 (`refresh_token` en el body del login) — hecho por
  el propietario; sin él el login nativo no podía completar.

## Totales

- **Automatizado**: 422 (pytest) + 29 (swift test, incluido el test de regresión de URL) =
  **451 tests verdes**, 3 xfailed legacy.
- **Validación manual en iPhone 13 Pro**: login → auto-login → logout, COMPLETADA.

## Sources
- Evidencia de los checkpoints de construcción de los 3 bolts (proof_path en `.aidlc-construction-checkpoints/`).

## Assumptions & Open Questions
None.
