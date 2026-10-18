# Intent Capture — Preguntas de clarificación

> Spike B-01: validación en vivo de la cadena `xtool` (build Swift/SwiftUI → firma gratuita →
> instalación en el iPhone 13 Pro desde WSL). Responde en los `[Answer]:` o pídeme el modo guiado.

## Sources

- [desc] Initial description: "Spike de la cadena xtool end-to-end: validar en vivo build de una app Swift/SwiftUI mínima, firma con cuenta Apple ID gratuita e instalación en el iPhone 13 Pro desde WSL (Windows). Es el proto-Unit B-01 del backlog del intent de viabilidad iOS nativo (261016-ios-native-feasibility), el camino crítico risk-first que valida el riesgo R-01 antes de reescribir el cliente. Dependencias: D-02 (WSL + Swift 6.4 + usbmuxd), D-03 (Apple ID). Nuevo intent de construccion/spike partiendo del codigo Angular existente como especificacion de referencia."
- [scope] Workflow-selected scope: `bugfix` (plan custom `ios-xtool-spike`).
- [memory:M1] `aidlc/spaces/default/memory/project.md#Mandated`: "ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); descartar toda mejora o dependencia con gasto recurrente."

## Q1. Problema / objetivo del spike

¿Cuál es el resultado concreto que valida el spike como "éxito"? (define el DONE binario)

- A. Que una app Swift/SwiftUI mínima **arranque en el iPhone 13 Pro físico**, construida+firmada+instalada íntegramente con `xtool` desde WSL, con firma de Apple ID gratuita.
- B. Igual que A, pero basta con **llegar a instalar el `.app`** aunque no se abra (validar hasta el paso de instalación).
- C. Igual que A, y además **medir/documentar la caducidad real** (~7 días) y el flujo de refirmado.
- D. Validar **solo el build** (compilar el `.app` con `xtool`), dejando firma e instalación en dispositivo para después.
- E. Not yet defined.
- X. Other (please specify)

[Answer]: A. Que una app Swift/SwiftUI mínima **arranque en el iPhone 13 Pro físico**, construida+firmada+instalada íntegramente con `xtool` desde WSL, con firma de Apple ID gratuita.

## Q2. ¿Dónde falla hoy / qué incertidumbre resuelve?

¿Cuál es el desconocido principal que más te preocupa validar primero (risk-first)?

- A. Que la **cadena `xtool` end-to-end funcione desde WSL** (toolchain Swift 6.4 + usbmuxd + USB passthrough al iPhone).
- B. Que la **firma con Apple ID gratuita** baste para instalar en dispositivo (certificado/provisioning, prefijo de bundle ID).
- C. La **fricción de la caducidad ~7 días** y lo pesado que sea el refirmado/reinstalación.
- D. Todas por igual; el spike debe tocarlas de principio a fin.
- E. Not yet defined.
- X. Other (please specify)

[Answer]: D. Todas por igual; el spike debe tocarlas de principio a fin.

## Q3. Entorno y dependencias (D-02, D-03)

¿Qué piezas del entorno das ya por disponibles y cuáles habría que preparar dentro del spike?

- A. **Todo listo**: WSL operativo, Swift 6.4 instalable, usbmuxd/libimobiledevice y USB passthrough resueltos, Apple ID gratuito disponible.
- B. **WSL listo**, pero Swift 6.4 / usbmuxd / USB passthrough **se instalan y documentan dentro del spike**.
- C. **WSL listo y Apple ID disponible**, el resto del toolchain se instala en el spike.
- D. Not identified (hay que descubrirlo durante el spike).
- X. Other (please specify)

[Answer]: C. **WSL listo y Apple ID disponible**, el resto del toolchain (Swift 6.4, usbmuxd/libimobiledevice, USB passthrough) se instala y documenta en el spike.

## Q4. ¿Quién es el usuario / para qué sirve el resultado?

¿Para quién es este spike y qué decisión habilita?

- A. **Para ti como único mantenedor**: habilita la decisión go/no-go de reescribir el cliente nativo (B-02…B-08) sobre `xtool` + firma gratuita.
- B. Igual que A, y además **sirve de guía reproducible** (runbook) para montar el entorno en el futuro.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: B. **Para ti como único mantenedor**: habilita la decisión go/no-go de reescribir el cliente nativo (B-02…B-08), y además sirve de **guía reproducible (runbook)** para montar el entorno en el futuro.

## Q5. Entregables del spike (además del "funciona")

¿Qué quieres conservar como salida del spike, más allá de ver la app en el iPhone?

- A. **La app mínima desechable** (código Swift/SwiftUI + `xtool.yml`/`Package.swift`) y una **nota de hallazgos** (qué funcionó, pasos, bloqueos, límites de cuenta gratuita observados).
- B. Solo la **nota de hallazgos** (la app es throwaway y no se conserva).
- C. A, y además un **runbook paso a paso** reproducible del entorno WSL+`xtool`.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: C. La **app mínima desechable** (código Swift/SwiftUI + `xtool.yml`/`Package.swift`), una **nota de hallazgos** (qué funcionó, pasos, bloqueos, límites de cuenta gratuita observados) y un **runbook paso a paso** reproducible del entorno WSL+`xtool`.

## Q6. Qué deja fuera esta primera versión (límite de producto)

El spike NO reescribe el cliente ni toca el backend. ¿Confirmas qué queda explícitamente fuera?

- A. **Fuera**: cualquier pantalla real (login, mercado, presupuesto…), la capa de red hacia `/api/v1/*`, el auth con Keychain, el ajuste de `/auth/refresh` (D-01), CI/distribución. El spike es solo la cadena de toolchain con una app de prueba trivial.
- B. Igual que A, pero **dentro** entra además un **"hola mundo" de red** (una llamada HTTP trivial) para validar conectividad desde la app nativa.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. **Fuera**: cualquier pantalla real (login, mercado, presupuesto…), la capa de red hacia `/api/v1/*`, el auth con Keychain, el ajuste de `/auth/refresh` (D-01), CI/distribución. El spike es solo la cadena de toolchain con una app de prueba trivial.

## Q7. Coste y cuenta Apple

El mandato es coste 0 € [memory:M1], con la excepción acotada del Apple Developer Program solo para distribución. Para este spike:

- A. **Estrictamente firma gratuita** (Apple ID sin pago); si no basta, el spike lo documenta como hallazgo y **no** se compra nada.
- B. Firma gratuita primero, pero **autorizas de antemano** valorar el Apple Developer Program (~99 €/año) como salida si la fricción es inasumible.
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. **Estrictamente firma gratuita** (Apple ID sin pago); si no basta, el spike lo documenta como hallazgo y **no** se compra nada.

## Assumption Confirmation

Los artefactos conservan estos supuestos (no confirmados como hechos):

1. [assumption] Se dispone de un Apple ID gratuito y de WSL operativo; el resto del toolchain (Swift 6.4, usbmuxd/libimobiledevice, USB passthrough) se instala y documenta dentro del spike. [Q3]
2. [assumption] La caducidad ~7 días de la firma gratuita y el flujo de refirmado quedan fuera del foco de este spike (materia del proto-Unit B-09); aquí solo se observa y anota si aflora. [Q2]

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions
