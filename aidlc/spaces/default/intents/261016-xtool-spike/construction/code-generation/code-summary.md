# Code Summary — Spike de la cadena `xtool` (B-01)

## Ficheros creados

| Fichero | Propósito |
|---------|-----------|
| `spikes/ios-xtool/Package.swift` | Manifiesto SwiftPM (`swift-tools-version:6.0`), un producto ejecutable iOS `XToolSpike`, plataforma `.iOS(.v17)`, sin deps/extensiones/tests. |
| `spikes/ios-xtool/Sources/XToolSpike/XToolSpikeApp.swift` | `@main App` SwiftUI con un único `WindowGroup`. |
| `spikes/ios-xtool/Sources/XToolSpike/ContentView.swift` | Vista trivial: muestra "xtool OK" + versión (`CFBundleShortVersionString`, fallback "unknown") como evidencia de arranque. |
| `spikes/ios-xtool/xtool.yml` | Config `xtool`: `version`, `bundleID` (placeholder `com.example.xtoolspike`), `product: XToolSpike`; comentario sobre prefijo de bundle ID y validez ~7 días de la cuenta gratuita. |
| `spikes/ios-xtool/scripts/setup-wsl.sh` | Setup idempotente del entorno WSL: detecta Ubuntu, instala Swift (vía `swiftly` preferente, fallback toolchain 24.04 por R-02), instala `usbmuxd`/libimobiledevice, imprime notas de `usbipd-win` del lado Windows. Falla ruidoso; sin secretos. |
| `spikes/ios-xtool/scripts/smoke.sh` | Cadena repetible `xtool dev build` (build→sign→install) + recordatorio de abrir y confiar el certificado; re-ejecutable tras caducidad ~7 días. Checks de prerequisitos con errores claros. |
| `spikes/ios-xtool/README.md` | README corto (castellano) con propósito, estructura y cómo correr los scripts; enlaza al runbook. |
| `docs/spikes/ios-xtool.md` | Runbook en castellano (prerequisitos, setup, device link, build/sign/install, smoke) + secciones vacías `## Hallazgos` y `## Bloqueos observados` para la ejecución en vivo. |

## Decisiones de implementación clave

- **Instalación de Swift en dos vías**: `swiftly` como preferente (version-agnostic, oficial) y
  fallback al toolchain etiquetado 24.04 fijado a `swift-6.0.3-RELEASE`, por el riesgo R-02 (no
  hay binario oficial para Ubuntu 26.04). PATH persistido idempotentemente en `.bashrc`.
- **Separación Windows/WSL explícita**: `usbipd-win` se documenta como paso del host Windows
  (PowerShell elevado), no dentro de WSL; el script imprime los comandos `bind`/`attach`.
- **Sin secretos**: la firma usa tu Apple ID introducido interactivamente por `xtool`; ningún
  script almacena credenciales (cumple la regla de no-secretos-en-claro).
- **`bundleID` como placeholder**: documentado que la cuenta gratuita lo prefija en firma.

## Cobertura de tests

Sin suite automatizada nueva (spike de toolchain; verificación manual en dispositivo). La suite
existente del repo (`backend/` `pytest`, `angular-app/` `ng test`) **no se toca** y permanece
verde trivialmente. El "test" del spike es el smoke manual documentado en el runbook.

## Desviaciones del plan

- **Step 7** (verificar suite existente verde): sin tick de código; su ejecución efectiva es
  trabajo de Build and Test. Confirmado que no se tocó `backend/` ni `angular-app/`.
- **Package.swift** fija `.iOS(.v17)` y el fallback a `swift-6.0.3-RELEASE ubuntu24.04` como
  valores concretos razonables para el spike; se ajustarán si el entorno en vivo pide otro pin.
- **smoke.sh** asume que `xtool dev build` hace build→sign→install en un paso; un comentario
  avisa de ajustarlo si la versión instalada de `xtool` separa los subcomandos.
