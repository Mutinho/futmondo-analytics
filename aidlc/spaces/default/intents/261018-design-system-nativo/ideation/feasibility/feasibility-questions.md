# Feasibility & Constraints — Preguntas de clarificación

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, xtool, WSL, Apple HIG, Google Stitch, iOS Keychain) verbatim en inglés.
> Adaptado al stack real (app nativa iOS Swift/SwiftUI construida con `xtool` desde WSL, coste 0 €), NO a AWS. Rellena cada `[Answer]:`.

## Q1. ¿Con qué debe integrarse / sobre qué se apoya este sistema de diseño?

- A. Es una capa nueva **autocontenida** dentro del proyecto iOS existente (el que ya tiene el login F1): sólo depende del SDK de Apple (SwiftUI) y se consume desde las pantallas; no integra con sistemas externos.
- B. Además debe encajar con la estructura/convenciones del código iOS de F1 (módulos, `xtool.yml`, organización SwiftPM).
- C. Varias de las anteriores.
- X. Other (please specify)

[Answer]: C. A+B (capa autocontenida sobre SDK de Apple/SwiftUI, sin integraciones externas, pero encajando con la estructura SwiftPM/`xtool.yml` y convenciones del código iOS de F1)

## Q2. ¿Hay requisitos regulatorios o de compliance (PCI, HIPAA, SOC2, residencia de datos)?

- A. No: una capa de diseño (tokens + componentes visuales) no maneja datos personales ni de pago; sin requisitos regulatorios. Se preserva la regla durable de no almacenar credenciales en claro (no afectada por esta capa).
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. No: capa de diseño sin datos personales ni de pago; sin requisitos regulatorios. Se preserva la regla durable de no almacenar credenciales en claro (no afectada por esta capa).

## Q3. ¿Cuál es el stack y el perfil de habilidades disponible?

- A. Swift/SwiftUI nativo, construido con `xtool` desde WSL (cadena ya validada en F1, con firma gratuita); único desarrollador/mantenedor. Se reproduce en SwiftUI un diseño de referencia de Google Stitch.
- B. Igual que A pero con experiencia aún limitada en SwiftUI (curva de aprendizaje a considerar como riesgo).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: B. Stack Swift/SwiftUI nativo con `xtool` desde WSL (validado en F1, firma gratuita), único mantenedor, reproduciendo un diseño de Google Stitch; con experiencia aún limitada en SwiftUI → curva de aprendizaje registrada como riesgo.

## Q4. ¿Restricciones de presupuesto y plazo?

- A. Coste 0 € recurrente (sólo SDK de Apple, sin dependencias de pago); sin plazo (proyecto personal). La excepción acotada de coste de publicación nativa (Apple Developer Program) NO se activa en este intent.
- B. Igual que A pero con algún plazo blando.
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. Coste 0 € recurrente (sólo SDK de Apple, sin dependencias de pago); sin plazo; la excepción de publicación nativa NO se activa en este intent.

## Q5. ¿Bloqueadores organizativos (change freeze, prioridades en conflicto)?

- A. Ninguno: proyecto personal, un único decisor.
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. Ninguno: proyecto personal, un único decisor.

## Q6. Servicios AWS / cuentas en uso (pregunta estándar de la etapa)

- A. NO-APLICA: el stack es Fly.io + Neon (backend) y app nativa iOS con `xtool`; no se usa AWS. Esta capa de diseño es puramente cliente iOS y no toca infraestructura.
- X. Other (please specify)

[Answer]: A. NO-APLICA: stack Fly.io + Neon + app nativa iOS con `xtool`; sin AWS. Capa de diseño puramente cliente iOS, no toca infraestructura.

## Q7. Incertidumbre técnica principal a vigilar (RAID) — ¿cuál es el riesgo dominante?

- A. **Fidelidad de traducción**: reproducir en SwiftUI el diseño de Google Stitch cuando el export puede estar incompleto o no ser 1:1 con SwiftUI; lo que falte se cubre con Apple HIG.
- B. **Transversalidad de claro/oscuro + Dynamic Type**: garantizar que todos los componentes base responden correctamente a ambos sin reglas ad-hoc por pantalla.
- C. **Revestir F1 sin regresión**: aplicar la capa al login ya construido sin cambiar su comportamiento.
- D. Varias de las anteriores (indica cuáles).
- X. Other (please specify)

[Answer]: D. A+B+C, pero con la referencia de diseño CAMBIADA (ver Q8): se descarta Google Stitch; el riesgo dominante pasa a ser la fidelidad de reproducir en SwiftUI el tema de Angular Material (paleta verde/violeta, claro/oscuro, tokens semánticos). Siguen B (transversalidad claro/oscuro + Dynamic Type) y C (revestir F1 sin regresión). Los tres van al RAID.

## Q8. Cambio de fuente de referencia del diseño (decisión del propietario, 2026-10-18)

El propietario descarta Google Stitch ("no me gusta lo que me propone"). De momento el sistema de diseño nativo debe **adaptar al 100% el estilo y tema que ya usa el frontend Angular** (colores y estilo). ¿Qué referencia se adopta?

- A. Reproducir en SwiftUI el tema del frontend Angular existente: Material 3 con paleta primaria **verde** (`mat.$green-palette`) y terciaria violeta (`mat.$violet-palette`), tipografía Roboto, modo claro/oscuro (`body.dark-theme`), y los tokens semánticos propios (`money-positive`/`money-negative`, escala `h1/h2/h3`, gradiente de splash verde) definidos en `angular-app/src/styles.scss`.
- B. Inspiración ligera en Angular; definir el resto con Apple HIG.
- X. Other (please specify)

[Answer]: A. Adaptar al 100% el tema de Angular (`angular-app/src/styles.scss`): paleta verde/violeta Material 3, Roboto, claro/oscuro y tokens semánticos propios, reproducidos en SwiftUI con SDK de Apple (coste 0 €). Google Stitch queda descartado.

## Consolidated Summary Confirmation

Resumen de tus respuestas de Feasibility & Constraints:

- **Veredicto**: GO — capa de diseño nativa altamente plausible con SwiftUI + SDK de Apple a coste 0 €.
- **Integración (Q1=C)**: capa autocontenida que encaja con la estructura SwiftPM/`xtool.yml` y convenciones de F1.
- **Compliance (Q2=A)**: ninguno; no maneja datos sensibles; se preserva la regla de credenciales.
- **Stack/habilidades (Q3=B)**: Swift/SwiftUI con `xtool`/WSL (validado en F1); curva de aprendizaje SwiftUI como riesgo.
- **Presupuesto/plazo (Q4=A)**: coste 0 €, sin plazo; excepción de publicación nativa no activada.
- **Bloqueadores (Q5=A)**: ninguno; un único decisor.
- **AWS (Q6)**: NO-APLICA (stack Fly.io+Neon / iOS nativo xtool).
- **Riesgo dominante (Q7=D)** y **referencia de diseño (Q8=A)**: se **descarta Google Stitch**; la referencia pasa a ser el **tema del frontend Angular** (`angular-app/src/styles.scss`: Material 3 paleta verde/violeta, Roboto, claro/oscuro, tokens semánticos), reproducido al 100% en SwiftUI; lo que no tenga equivalente 1:1 se cubre con Apple HIG. Riesgos al RAID: fidelidad de reproducción (dominante), transversalidad claro/oscuro+Dynamic Type, revestir F1 sin regresión.

¿Está todo correcto?

[Answer]: Looks correct
