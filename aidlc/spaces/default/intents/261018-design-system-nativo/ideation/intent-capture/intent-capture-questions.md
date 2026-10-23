# Intent Capture & Framing — Preguntas de clarificación

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, iOS Keychain, Angular, FastAPI) verbatim en inglés.
> Rellena cada `[Answer]:` con la letra (A-E) o `X. Other` + tu texto. Las preguntas se centran en el **problema/oportunidad**, no en la implementación.

## Sources

- [desc] Initial description: "Sistema de diseño / theming nativo iOS (SwiftUI) que precede a F2: tokens de color claro/oscuro, tipografía con Dynamic Type, espaciado y componentes SwiftUI base (botones, campos, tarjetas, estados de carga/error), solo con SDK de Apple (coste 0 €). Reviste el login de F1 ya construido y alimenta la construcción de las pantallas de datos de F2."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Mandated`: "ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en"
- [memory:M2] `aidlc/spaces/default/memory/project.md#Corrections`: "ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11)"

## Q1. ¿Qué problema de producto resuelve este sistema de diseño nativo?

La descripción plantea una capa de diseño reutilizable (tokens + componentes SwiftUI base) que precede a F2 y reviste el login de F1. ¿Cuál es el problema central que te mueve a hacerlo ahora?

- A. Evitar retrabajo: construir F2/F3 sin una base común obligaría a repasar todas las pantallas después.
- B. Coherencia visual: que todas las pantallas nativas se vean y se comporten igual (iguales colores, tipografía, espaciado, estados).
- C. Velocidad de construcción: dar a F2 piezas ya hechas (botones, campos, tarjetas) para codificar pantallas más rápido.
- D. Soporte nativo de claro/oscuro y accesibilidad (Dynamic Type) de serie, sin reinventarlo por pantalla.
- E. Varias de las anteriores (indica cuáles en el texto).
- X. Other (please specify)

[Answer]: E. A+B+C+D (evitar retrabajo + coherencia visual + velocidad de construcción + soporte nativo claro/oscuro y Dynamic Type)

## Q2. ¿Quién es el beneficiario/usuario y qué dolor experimenta hoy?

- A. Tú como usuario único de la app en el iPhone 13 Pro (proyecto personal): la experiencia visual debe ser consistente y cómoda.
- B. Tú como desarrollador/mantenedor: el dolor es el coste de mantener estilos dispersos pantalla a pantalla.
- C. Ambos (usuario final y mantenedor).
- D. Not yet defined.
- X. Other (please specify)

[Answer]: C. Ambos (usuario final y mantenedor)

## Q3. ¿Qué aspecto tiene el éxito? ¿Qué resultado medible o verificable esperas?

- A. F2 se puede construir usando sólo los componentes/tokens del sistema (ninguna pantalla define estilos propios ad-hoc).
- B. El login de F1 queda revestido con el sistema sin cambios de comportamiento (sólo capa visual), verificable en el iPhone 13 Pro.
- C. Soporte claro/oscuro y Dynamic Type funcionan en todos los componentes base (demostrable con una pantalla de catálogo/preview).
- D. Coste 0 €: sólo SDK de Apple, ninguna dependencia de pago ni servicio recurrente.
- E. Varias de las anteriores (indica cuáles).
- X. Other (please specify)

[Answer]: E. A+B+C+D (F2 se construye sólo con el sistema + login F1 revestido sin cambios de comportamiento + claro/oscuro y Dynamic Type en todos los componentes, demostrable en catálogo/preview + coste 0 € sólo SDK de Apple)

## Q4. ¿Cuál es el disparador de hacerlo AHORA (y no antes o después)?

- A. Decisión ya tomada al cerrar F1 (2026-10-18): el momento óptimo es **antes de F2** porque la alimenta y reviste F1 con coste marginal.
- B. Presión de evitar deuda: hacerlo tras F2/F3 ya construidas obligaría a retrabajo.
- C. Aprendizaje: consolidar el patrón de theming nativo antes de multiplicar pantallas.
- D. Not applicable / sin disparador concreto.
- X. Other (please specify)

[Answer]: A. Decisión ya tomada al cerrar F1 (2026-10-18): precede a F2, la alimenta y reviste F1 con coste marginal

## Q5. ¿Quiénes son los stakeholders clave y qué le importa a cada uno?

- A. Un único stakeholder: tú (propietario, desarrollador y usuario final a la vez).
- B. Tú + algún revisor/colaborador ocasional.
- C. Not identified.
- X. Other (please specify)

[Answer]: A. Un único stakeholder: tú (propietario, desarrollador y usuario final a la vez)

## Q6. ¿Quién decide el alcance y la prioridad de este intent?

- A. Tú, en solitario (proyecto personal, decisión unilateral).
- B. Tú con validación de un tercero.
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. Tú, en solitario (proyecto personal, decisión unilateral)

## Q7. ¿Hay requisitos de comunicación o cadencia de reporte?

- A. Ninguno: proyecto personal, sin reporte formal.
- B. Sólo el registro AI-DLC (decision log / artefactos) como traza.
- C. Not applicable.
- X. Other (please specify)

[Answer]: B. Sólo el registro AI-DLC (decision log / artefactos) como traza

## Q8. El scope de workflow ya está elegido (`feature`). ¿Qué debe dejar FUERA esta primera versión del sistema de diseño?

(No se pregunta si el scope es correcto; sólo qué queda fuera del producto en esta primera entrega.)

- A. Dejar fuera componentes complejos específicos de pantalla (tablas de datos ricas, gráficos Chart.js nativos, navegación/tab bar): sólo tokens + componentes base (botones, campos, tarjetas, estados de carga/error).
- B. Dejar fuera la aplicación del sistema a las pantallas de F2 (eso lo hace F2); este intent sólo entrega la capa + revestir F1.
- C. Dejar fuera animaciones/transiciones avanzadas y microinteracciones.
- D. Dejar fuera temas adicionales más allá de claro/oscuro (p. ej. alto contraste, temas de marca personalizables).
- E. Varias de las anteriores (indica cuáles).
- X. Other (please specify)

[Answer]: E. A+B+C+D (fuera: componentes complejos de pantalla incl. tab bar nativa B-08 → F2; aplicación del sistema a las pantallas de F2; animaciones/microinteracciones avanzadas; temas más allá de claro/oscuro)

## Q9. Diseño de referencia externo (Google Stitch) — seguimiento

Indicaste que estás generando el diseño con **Google Stitch** y que proporcionarás lo que la herramienta te deje exportar (imágenes, código, etc.); será "casi completo" probablemente, pero **no está garantizado**. ¿Cómo debe tratar este intent ese material?

- A. El sistema de diseño nativo debe **reproducir en SwiftUI el diseño de Stitch** (tokens de color/tipografía/espaciado y componentes base derivados de ese diseño), no inventarlo de cero; el material de Stitch (imágenes y, si lo hay, código/CSS) entra como **input en las etapas de mockups** (rough/refined), donde lo proporcionarás.
- B. El diseño de Stitch es sólo **inspiración ligera**; el sistema se define principalmente desde cero con las guías de Apple (HIG).
- C. Not yet defined (lo decides al llegar a mockups).
- X. Other (please specify)

[Answer]: A. Reproducir en SwiftUI el diseño de Stitch; el material (imágenes/código) entra como input en las etapas de mockups, con la salvedad de que la completitud del export no está garantizada y lo que falte se cubre con las guías de Apple (HIG) a coste 0 €

## Assumption Confirmation

El `intent-statement.md` contiene este supuesto (sin confirmar como hecho):

- [assumption] Existe un diseño de referencia en curso generado con **Google Stitch** que el usuario aportará como export (imágenes y, si la herramienta lo permite, código/CSS); el sistema de diseño nativo debe reproducir ese diseño en SwiftUI y el material entrará como input en las etapas de mockups (rough/refined). La completitud del export no está garantizada; lo que falte se cubre con Apple HIG a coste 0 €.

Opciones:

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions

## Consolidated Summary Confirmation

Resumen de tus respuestas de Intent Capture & Framing:

- **Problema (Q1=E)**: sin capa de diseño común, construir F2+ causa retrabajo, incoherencia visual y lentitud, y reinventa claro/oscuro + Dynamic Type por pantalla.
- **Beneficiario (Q2=C)**: tú, como usuario final y como mantenedor.
- **Éxito (Q3=E)**: F2 se construye sólo con el sistema; login F1 revestido sin cambios de comportamiento; claro/oscuro + Dynamic Type en todos los componentes (demostrable en catálogo/preview); coste 0 € sólo SDK de Apple.
- **Disparador (Q4=A)**: decisión tomada al cerrar F1 — va antes de F2.
- **Stakeholder (Q5=A) / decisor (Q6=A)**: único, tú. **Comunicación (Q7=B)**: sólo la traza AI-DLC.
- **Fuera de alcance (Q8=E)**: tab bar nativa (B-08) y pantallas de F2, microinteracciones avanzadas, temas más allá de claro/oscuro.
- **Supuesto (Q9=A, aceptado)**: diseño de referencia de Google Stitch, reproducido en SwiftUI, material como input en mockups; lo que falte se cubre con Apple HIG a coste 0 €.

¿Está todo correcto?

[Answer]: Looks correct
