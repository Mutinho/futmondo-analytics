# Security Test Instructions — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Idioma: castellano; identificadores/código en inglés.

## Verificaciones de seguridad automatizadas

- **Backend (pytest)**: el ajuste reutiliza la cripto (HS256, revocación por hash) sin cambios; el
  refresh token no viaja en URL/query; los tests cubren que la precedencia es determinista y que la
  revocación en logout invalida el token. Gate de CI: `gitleaks` (sin secretos), `pip-audit`.
- **iOS (swift test)**: `URLSessionNetworkClient` rechaza una base URL no-`https` (test
  `testThrowingInitRejectsInsecureBaseURL`); `AuthService`/`TokenHolder` borran el access token en
  ambas ubicaciones en logout (test de logout); el refresh token solo se guarda vía
  `KeychainStore` (doble in-memory en test; `KeychainTokenStore` real en el dispositivo).

## Verificaciones de seguridad manuales (iPhone, propietario)

- El refresh token reside en el **Keychain** (`AfterFirstUnlockThisDeviceOnly`, sin iCloud) — se
  comprueba que no aparece en `UserDefaults`/plist.
- Tras logout, ni el access token ni el refresh token quedan accesibles.
- TLS real contra el backend (sin ATS override en `Info.plist`).

## Guardarraíles (gate de CI bloqueante del repo)

`gitleaks` + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit` siguen bloqueando a
`main`; el cambio de backend de F1 pasa el gate. Ningún secreto/token real en el repo.

## Sources
- [consumes] security-requirements/security-design de los bolts; team.md (gate de CI).

## Assumptions & Open Questions
None.
