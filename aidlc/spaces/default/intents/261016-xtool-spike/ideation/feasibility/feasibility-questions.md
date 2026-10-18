# Feasibility & Constraints — Preguntas de clarificación

> Spike B-01: viabilidad de la cadena `xtool` (build Swift/SwiftUI → firma gratuita →
> instalación en el iPhone 13 Pro desde WSL). El estudio previo
> (`261016-ios-native-feasibility`) ya dio GO condicionado; aquí afinamos lo específico del spike.

## Sources

- [desc] Initial description: "Spike de la cadena xtool end-to-end: validar en vivo build de una app Swift/SwiftUI mínima, firma con cuenta Apple ID gratuita e instalación en el iPhone 13 Pro desde WSL (Windows). Es el proto-Unit B-01 del backlog del intent de viabilidad iOS nativo (261016-ios-native-feasibility), el camino crítico risk-first que valida el riesgo R-01 antes de reescribir el cliente. Dependencias: D-02 (WSL + Swift 6.4 + usbmuxd), D-03 (Apple ID). Nuevo intent de construccion/spike partiendo del codigo Angular existente como especificacion de referencia."
- [scope] Workflow-selected scope: `bugfix` (plan custom `ios-xtool-spike`).
- [memory:M1] `aidlc/spaces/default/memory/project.md#Mandated`: "ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); descartar toda mejora o dependencia con gasto recurrente."

## Q1. Distribución WSL y versión de SO

¿Sobre qué entorno WSL concreto corremos el spike? (determina paquetes y pasos del runbook)

- A. **Ubuntu 22.04 LTS** sobre WSL2 (lo más documentado para toolchains Swift en Linux).
- B. **Ubuntu 24.04 LTS** sobre WSL2.
- C. Otra distro Linux (Debian/Fedora/…) sobre WSL2.
- D. Not identified (el spike elige y documenta la que funcione).
- X. Other (please specify)

[Answer]: X. **Ubuntu 26.04 LTS (Resolute Raccoon) sobre WSL2** (detectado por inspección directa: `/etc/os-release` VERSION_ID=26.04; kernel `6.18.x-microsoft-standard-WSL2`). Swift y usbip no están instalados aún → los monta el spike. Riesgo: los binarios oficiales de Swift suelen publicarse para 22.04/24.04; en 26.04 puede hacer falta `swiftly` o el toolchain de 24.04 por compatibilidad (a registrar en RAID).

## Q2. Mecanismo de USB passthrough WSL → iPhone

El punto más frágil de la cadena. ¿Tienes preferencia o lo descubre el spike?

- A. **`usbipd-win`** (el mecanismo estándar de USB passthrough de WSL2 a Windows); el spike lo instala y documenta.
- B. Ya tienes un mecanismo de passthrough funcionando y el spike solo lo usa.
- C. Not identified (el spike investiga y documenta la vía que funcione, `usbipd-win` como primera hipótesis).
- X. Other (please specify)

[Answer]: A. **`usbipd-win`** (mecanismo estándar de USB passthrough de WSL2 ↔ Windows); el spike lo instala y documenta. Confirmado que hoy no hay `usbip` en el PATH.

## Q3. Criterio de verificación del "arranca en el dispositivo"

El DONE es que la app arranque en el iPhone 13 Pro (de intent-capture Q1). ¿Cómo lo damos por verificado?

- A. **Evidencia manual**: la app aparece en el iPhone y se abre mostrando una pantalla trivial (p. ej. un texto "xtool OK"); se captura en la nota de hallazgos (foto/log de `xtool`).
- B. Igual que A, y además dejar un **script/receta de smoke** repetible (reinstalar y abrir) documentado en el runbook.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: B. **Evidencia manual** (la app aparece y se abre mostrando una pantalla trivial, capturada en la nota de hallazgos como foto/log de `xtool`) **más una receta de smoke repetible** (reinstalar y abrir) documentada en el runbook.

## Q4. Ubicación de los entregables en el repo

¿Dónde viven la app desechable, la nota de hallazgos y el runbook? (de intent-capture Q5)

- A. En una carpeta nueva dedicada del repo, p. ej. **`spikes/ios-xtool/`** (app Swift) y **`docs/spikes/ios-xtool.md`** (hallazgos + runbook).
- B. Todo bajo **`docs/spikes/ios-xtool/`** (incluida la app como material de referencia).
- C. Fuera del repo (carpeta local), solo se commitea la nota + runbook.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. Carpeta nueva dedicada: **`spikes/ios-xtool/`** (app Swift desechable) y **`docs/spikes/ios-xtool.md`** (nota de hallazgos + runbook).

## Q5. Restricciones / bloqueos a registrar

¿Hay algún bloqueo o restricción organizativa que deba constar en el constraint register, más allá del coste 0 € ya afirmado [memory:M1]?

- A. **Ninguno adicional**: proyecto personal, sin plazo, sin change-freeze; única restricción dura es coste 0 € (firma gratuita).
- B. Hay restricciones de tiempo/disponibilidad del dispositivo o del PC con WSL (especificar en Other).
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. **Ninguno adicional**: proyecto personal, sin plazo, sin change-freeze; única restricción dura es coste 0 € (firma gratuita).

## Assumption Confirmation

Los artefactos conservan estos supuestos (no confirmados como hechos):

1. [assumption] Se dispone de Apple ID gratuito y de condiciones para conectar el iPhone 13 Pro por USB al PC con WSL. [Q5]
2. [assumption] `xtool` soporta la versión de Swift que se logre instalar en Ubuntu 26.04; si exige una versión no disponible, se usa `swiftly`/toolchain 24.04 por compatibilidad. [Q1]

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions
