# Test Results — Spike de la cadena `xtool` (B-01)

## Build status

**Cadena validada end-to-end en vivo (2026-10-16).** La app `XToolSpike`
construida, firmada (Apple ID gratuito) e instalada con `xtool` desde WSL
(Ubuntu 26.04) **arranca en el iPhone 13 Pro físico** y muestra
`xtool OK version 1.0.0`. `xtool dev run` terminó con exit=0 (Provisioning,
Signing, Packaging, Installing, Verifying todos 100%).

## Resultados de test

- Unit tests nuevos: 0 (spike de toolchain, sin código de app).
- Smoke manual en dispositivo: **PASÓ** (app abierta en el iPhone, pantalla
  `xtool OK version 1.0.0` confirmada por el usuario).
- Suite existente del repo: **sin regresiones** (no se tocó `backend/` ni
  `angular-app/`; verificado por `git status`).

## Target Verification Matrix (finalizada)

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| T1-suite-green | Testing Contract (keep existing suite green) | Sin regresiones | 0 cambios en código de app | `git status --porcelain` | build-and-test | Met |
| T2-scripts-syntax | code-summary (scripts bash) | Sin errores de sintaxis | `bash -n` OK en ambos | salida `bash -n` | build-and-test | Met |
| T3-chain-live | intent-capture Q1 (app arranca en iPhone vía xtool) | Cadena end-to-end verificada en dispositivo | **App arranca en el iPhone 13 Pro mostrando "xtool OK version 1.0.0"** | `xtool dev run` exit=0 (Install/Verify 100%) + confirmación visual del usuario | build-and-test | **Met** |

## Hallazgos de la ejecución en vivo (deuda/aprendizaje capturado)

El spike corrigió múltiples incompatibilidades reales de Ubuntu 26.04 y
descubrió la secuencia de versiones correcta; todo documentado en
`docs/spikes/ios-xtool.md` (Hallazgos, Bloqueos y flujo recurrente). Resumen:
toolchain Swift **6.4.0** (no 6.0.3/6.4.1), SDK **regenerado con 6.4.0 activo**,
fixes `libncurses6`/`libxml2.so.2`→`.16`/`zip`/paquetes renombrados, `xtool.yml`
`version:1` + `Package.swift` library product, y **relay del usbmuxd de Apple
(Windows) por TCP 27015** para sortear el `muxError` de usbipd.
