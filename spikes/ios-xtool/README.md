# XToolSpike — Spike de la cadena `xtool` (B-01)

App Swift/SwiftUI **mínima** cuyo único fin es **validar el toolchain `xtool`**
de extremo a extremo: build → firma gratuita → instalación → arranque en un
**iPhone 13 Pro** desde WSL (Ubuntu). No es una app de producto; si la pantalla
`xtool OK` + versión aparece en el dispositivo, el toolchain funciona.

## Estructura

- `Package.swift` — manifiesto SwiftPM (producto ejecutable iOS `XToolSpike`).
- `Sources/XToolSpike/XToolSpikeApp.swift` — `@main App` de SwiftUI.
- `Sources/XToolSpike/ContentView.swift` — vista trivial (evidencia de arranque).
- `xtool.yml` — config de `xtool` (`version`, `bundleID`, `product`).
- `scripts/setup-wsl.sh` — setup idempotente del entorno WSL (Swift, `usbmuxd`,
  notas de `usbipd-win`).
- `scripts/smoke.sh` — cadena repetible build/firma/instalación.

## Cómo correrlo

Desde la raíz del repo, en WSL con el iPhone conectado:

```bash
# 1. Preparar el entorno (una vez; idempotente)
spikes/ios-xtool/scripts/setup-wsl.sh

# 2. Atachar el iPhone a WSL con usbipd-win (ver runbook), luego:
spikes/ios-xtool/scripts/smoke.sh
```

Guía completa (prerequisitos, `usbipd-win`, firma gratuita, smoke manual y notas
de hallazgos): **[`docs/spikes/ios-xtool.md`](../../docs/spikes/ios-xtool.md)**.
