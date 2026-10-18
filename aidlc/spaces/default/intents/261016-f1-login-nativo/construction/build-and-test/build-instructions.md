# Build Instructions — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Perspectiva de calidad. Idioma: castellano;
> identificadores/código en inglés. Consolida la construcción/verificación de los 3 bolts.

## Backend (`backend-refresh-transport`)

```bash
# venv efímero (coste 0, python3), excluyendo libsql-experimental
cd backend && python3 -m venv .venv-verify && . .venv-verify/bin/activate \
  && grep -v '^libsql-experimental' requirements.txt > /tmp/reqs-verify.txt \
  && pip install -q -r /tmp/reqs-verify.txt \
  && JWT_SECRET=ephemeral-not-a-real-one python -m pytest -q
```
Resultado verificado: **422 passed, 3 xfailed**. `ruff check` limpio en los ficheros nuevos.

## iOS — lógica (`ios-network-client` + `ios-native-auth`)

```bash
cd ios && swift test
```
Resultado verificado: **28 passed, 0 failures** (14 NetworkClient + 14 AuthService). Compila
`FutmondoKit` en Linux/WSL (las vistas SwiftUI quedan aisladas bajo `#if canImport(SwiftUI)`).

## iOS — app en el dispositivo (validación manual del propietario)

```bash
# vía recomendada: script de instalación de F1 (relay usbmuxd + xtool dev run)
cd ios/scripts && ./install-app.sh
# equivalente manual:
cd ios && xtool dev build    # construye/firma la app; luego instalar en el iPhone
```
`ios/scripts/install-app.sh` replica el flujo del spike F0 adaptado a F1 (product `FutmondoApp`,
bundle `com.futmondo.app`): recalcula el relay usbmuxd (gateway WSL:27015), verifica el dispositivo
y corre `xtool dev run` (build → sign → install → launch). Valida el Keychain real (`SecItem`), las
vistas y el flujo visual (login → auto-login → logout) — lo que `swift test` no cubre (deuda de
arnés de dispositivo P-1). Firma gratuita ~7 días: re-ejecutar el script para refrescar.

## Sources
- [consumes] code-generation-plan/unit-test-instructions/code-summary de los 3 bolts.

## Assumptions & Open Questions
None.
