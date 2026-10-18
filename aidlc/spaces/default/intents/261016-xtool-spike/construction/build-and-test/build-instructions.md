# Build Instructions — Spike de la cadena `xtool` (B-01)

## Naturaleza

El "build" del spike es la propia cadena `xtool` (compilar el paquete SwiftPM en un `.app`
iOS). No es un build de CI del repo: ocurre en WSL contra un dispositivo físico y no es
automatizable a coste 0 €. Estas instrucciones documentan cómo ejecutarlo; su ejecución real
es interactiva (requiere iPhone + Apple ID + USB passthrough).

## Prerequisitos

- WSL2 operativo (verificado: Ubuntu 26.04 LTS).
- Lado Windows: `usbipd-win` instalado (`winget install --exact dorssel.usbipd-win`).
- iPhone 13 Pro conectado por USB y attach-eado a WSL (`usbipd bind` + `usbipd attach --wsl`).
- `xtool` instalado según su documentación upstream.

## Instalación de dependencias (dentro de WSL)

```bash
spikes/ios-xtool/scripts/setup-wsl.sh
```

Instala (idempotente): toolchain Swift (vía `swiftly`, fallback toolchain 24.04 por el riesgo
R-02 en Ubuntu 26.04), `usbmuxd`/libimobiledevice, e imprime los pasos del lado Windows para
`usbipd-win`. Falla ruidoso si falta un prerequisito.

## Comandos de build / firma / instalación

```bash
spikes/ios-xtool/scripts/smoke.sh
```

Envuelve `xtool dev build` (build → firma con Apple ID interactivo → instalación en el
dispositivo). Re-ejecutable tras la caducidad ~7 días de la firma gratuita.

## Verificación del build

- La app `XToolSpike` aparece instalada en el iPhone 13 Pro.
- Al abrirla (tras confiar el certificado en Ajustes), muestra "xtool OK" + versión.

## Troubleshooting

- `idevice_id -l` vacío → revisar `usbipd attach --wsl` y que `usbmuxd` corra en WSL.
- `xtool dev build` falla por firma → re-ejecutar `smoke.sh` (refresca la firma caducada).
- Swift no instala en 26.04 → el fallback a toolchain 24.04 de `setup-wsl.sh` cubre R-02.
