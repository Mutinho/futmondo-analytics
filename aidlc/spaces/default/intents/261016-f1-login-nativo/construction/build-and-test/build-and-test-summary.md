# Build and Test Summary — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Cierre de la construcción de F1. Idioma: castellano;
> identificadores/código en inglés.

## Resumen

Los 3 bolts de F1 están construidos, verificados y aprobados:
- **Bolt 1 `backend-refresh-transport`**: ajuste aditivo del transporte del refresh token
  (`auth/routes.py` + `auth/models.py`) + 8 tests. `pytest` **422 passed / 3 xfailed**, cobertura
  58,3% (> piso 27%), `ruff` limpio.
- **Bolt 2 `ios-network-client`**: `FutmondoKit` capa de red (URLSession, Bearer, errores tipados)
  + 14 XCTest. `swift test` **14 passed**.
- **Bolt 3 `ios-native-auth`**: Keychain + `AuthService` (actor, refresh coalescido, borrado
  doble) + ViewModel + Login/SplashView + 14 XCTest. `swift test` **28 passed** (acumulado con
  Bolt 2).

**Total automatizado: 451 tests verdes** (422 pytest + 29 swift test), 3 xfail legacy. El gate de
CI del repo (gitleaks + ruff + pytest + pip-audit + ng test + npm audit) sigue aplicando.

## Validación manual en iPhone (COMPLETADA)

`ios/scripts/install-app.sh` instaló la app en el iPhone 13 Pro y se validó el flujo F1:
**login → "Sesión iniciada" → cerrar y reabrir = auto-login directo (refresh token del Keychain) →
logout**. NFR-3 cubierto end-to-end.

## Fixes de dispositivo (post-review, re-verificados)

Fallos que solo afloran con el SDK/toolchain de Apple (no en `swift test` de Linux ni en revisión):
producto xtool (app como library + sin `main.swift`), Swift 6 `Sendable` en el build iOS, URL
malformada por `appendingPathComponent` (+ test de regresión), y la navegación del `SplashView`
ante login manual. Backend desplegado a Fly.io con D-01. Todos corregidos; `swift test` 29 passed.

## Higiene de repo

Añadidos a `.gitignore`: `.venv-*/` (venv efímeros de verificación) e `ios/.build/` + `.swiftpm/`.

## Consolidated Summary Confirmation

La confirmación y el checkpoint de resumen de esta etapa se registran en
`build-and-test-questions.md` (fuente de verdad del `[Answer]`).

## Sources
- [consumes] test-results.md, cross-unit-traceability.md, checkpoints de los 3 bolts.

## Assumptions & Open Questions
None.
