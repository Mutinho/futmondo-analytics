# Feasibility Assessment — Spike de la cadena `xtool` (B-01)

> Fase: ideación. Entregable de análisis (prosa). Estimaciones conservadoras y supuestos
> marcados conforme a los guardarraíles de ideación. Hereda el GO condicionado del estudio
> previo (`261016-ios-native-feasibility`); aquí se evalúa la viabilidad **del spike concreto**.

## 1. Resumen ejecutivo (go/no-go)

**GO.** La cadena `xtool` (build SwiftPM → firma con Apple ID gratuito → instalación en iPhone)
está documentada como soportada en Linux/WSL por el proyecto `xtool`, y el entorno base (WSL2)
ya existe. [desc] El spike es la validación en vivo de ese GO condicionado: su coste de
equivocarse es bajo (app desechable, proyecto personal sin plazo) y la decisión es reversible.
El principal desconocido es operativo (montar toolchain + USB passthrough al iPhone), no de
diseño. [desc] [Q1] [Q2]

## 2. Viabilidad técnica por eslabón

| Eslabón de la cadena | Viabilidad | Nota |
|----------------------|-----------|------|
| WSL2 operativo | Confirmada | Detectado por inspección directa: Ubuntu 26.04 LTS, kernel `6.18.x-microsoft-standard-WSL2`. [Q1] |
| Toolchain Swift 6.4 | Plausible con riesgo | Swift y usbip NO instalados hoy; el spike los monta. Riesgo: binarios oficiales de Swift se publican para 22.04/24.04, no necesariamente 26.04 → ver RAID R-02. [Q1] |
| `xtool` (build + firma + install) | Plausible | Reemplazo cross-platform de Xcode; construye SwiftPM en `.app`, firma e instala. Config vía `xtool.yml`. [desc] |
| USB passthrough WSL→iPhone | Plausible, eslabón más frágil | Vía `usbipd-win` (lado Windows) + cliente `usbip` (Linux) + `usbmuxd`/libimobiledevice para hablar con el iPhone → ver RAID R-01. [Q2] |
| Firma Apple ID gratuita | Plausible con fricción conocida | Prefijo de bundle ID automático y caducidad ~7 días (fuera de foco aquí). Coste 0 € estricto. [memory:M1] |
| Instalación + arranque en iPhone 13 Pro | Objetivo del spike | DONE = app trivial abierta en el dispositivo; evidencia manual + receta de smoke. [Q3] |

## 3. Alcance y verificación

- **Alcance**: solo la cadena de toolchain con una app Swift/SwiftUI trivial. Fuera: red,
  pantallas reales, auth/Keychain, `/auth/refresh`, CI/distribución (confirmado en
  intent-capture). [desc]
- **Verificación**: evidencia manual (la app aparece y se abre mostrando una pantalla trivial,
  capturada como foto/log de `xtool`) **más** una receta de smoke repetible (reinstalar y
  abrir) en el runbook. [Q3]
- **Entregables**: app desechable en `spikes/ios-xtool/`; nota de hallazgos + runbook en
  `docs/spikes/ios-xtool.md`. [Q4]

## 4. Viabilidad por dimensiones

- **Técnica**: plausible; el riesgo se concentra en el montaje (toolchain en 26.04 + USB
  passthrough del iPhone), no en el diseño. [Q1] [Q2]
- **Económica**: 0 € recurrente; firma gratuita estricta, sin compra del Apple Developer
  Program en este spike. [Q7-intent-capture] [memory:M1]
- **De esfuerzo**: media-baja; una app trivial más fontanería de entorno. Sin plazo. [Q5]
- **De entorno**: WSL2 ya operativo; el resto del toolchain se instala y documenta. [Q1]

## 5. Recomendación

Proceder con el spike. Atacar primero el eslabón más frágil (toolchain Swift en 26.04 y USB
passthrough del iPhone): si alguno no cuaja, se documenta como hallazgo y la decisión de ruta
alternativa (toolchain 24.04, o reconsiderar `xtool`) se toma con datos, sin coste hundido.

## Assumptions & Open Questions

- [assumption] Se dispone de Apple ID gratuito y de un cable/condiciones para conectar el
  iPhone 13 Pro al PC con WSL. [Q5]
- [assumption] `xtool` soporta la versión de Swift que se logre instalar en 26.04; si exige una
  versión concreta no disponible, se usa `swiftly`/toolchain 24.04 por compatibilidad. [Q1]
