# Scope Definition & Prioritization — Preguntas de clarificación

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, Material 3, Apple HIG) verbatim en inglés.
> Define el boundary in/out y el backlog priorizado (proto-Units, MoSCoW). Rellena cada `[Answer]:`.

## Q1. ¿Cuál es el alcance mínimo viable que aporta valor en este intent?

- A. Tokens semánticos (color claro/oscuro derivados del tema Angular, tipografía Roboto con Dynamic Type, espaciado) + componentes SwiftUI base (botón, campo de texto, tarjeta, estados de carga/error) + una pantalla de catálogo/preview que los demuestre + revestir el login de F1.
- B. Igual que A pero SIN revestir F1 en este intent (sólo la capa + catálogo; F1 se reviste en otro momento).
- C. Igual que A pero SIN la pantalla de catálogo/preview.
- X. Other (please specify)

[Answer]: A. Tokens semánticos (color claro/oscuro del tema Angular, Roboto con Dynamic Type, espaciado) + componentes SwiftUI base (botón, campo, tarjeta, estados carga/error) + pantalla de catálogo/preview + revestir el login de F1.

## Q2. ¿Qué capacidades son must-have vs. nice-to-have?

- A. Must: tokens de color (claro/oscuro), tipografía Dynamic Type, espaciado, botón, campo, tarjeta, estados carga/error, revestir F1. Nice: catálogo/preview como pantalla navegable, variantes extra de componentes (p. ej. tamaños/estilos secundarios).
- B. Must: todo lo de A incluido el catálogo/preview (lo consideras imprescindible como evidencia). Nice: variantes extra.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: B. Must: tokens (color claro/oscuro, Dynamic Type, espaciado), botón, campo, tarjeta, estados carga/error, catálogo/preview y revestir F1. Nice: variantes extra de componentes.

## Q3. ¿Dependencias entre capacidades?

- A. Los tokens (color/tipografía/espaciado) son la base; los componentes dependen de los tokens; el catálogo depende de los componentes; revestir F1 depende de tokens + componentes.
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. Tokens como base; componentes dependen de tokens; catálogo depende de componentes; revestir F1 depende de tokens + componentes.

## Q4. ¿Preferencia de secuenciación?

- A. Dependency-first: tokens → componentes → catálogo → revestir F1 (orden natural de dependencias).
- B. Risk-first: atacar primero el riesgo dominante (fidelidad de reproducción del tema Angular) con un spike de tokens+1 componente validado en claro/oscuro, luego el resto.
- C. Value-first.
- X. Other (please specify)

[Answer]: B. Risk-first: spike inicial de tokens + 1 componente validado en claro/oscuro contra el frontend Angular para retirar el riesgo de fidelidad, luego el resto respetando el orden de dependencias.

## Q5. ¿Hay deadlines duros ligados a alguna capacidad?

- A. No: sin plazo (proyecto personal).
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. No: sin plazo (proyecto personal).

## Q6. Boundary de producto — ¿confirmas lo que queda FUERA (de intent-capture Q8 + feasibility)?

- A. Sí, fuera: navegación/tab bar nativa (B-08, va en F2), aplicación del sistema a las pantallas de F2, animaciones/microinteracciones avanzadas, temas más allá de claro/oscuro (alto contraste, temas de marca), y cualquier dependencia de pago.
- B. Quiero ajustar el boundary (indica cómo).
- X. Other (please specify)

[Answer]: A. Sí, fuera: tab bar nativa (B-08, F2), aplicación a pantallas de F2, animaciones/microinteracciones avanzadas, temas más allá de claro/oscuro, y cualquier dependencia de pago.

## Consolidated Summary Confirmation

Resumen de tus respuestas de Scope Definition:

- **Alcance mínimo (Q1=A)**: tokens (color claro/oscuro del tema Angular, Roboto+Dynamic Type, espaciado) + componentes base (botón, campo, tarjeta, estados carga/error) + catálogo/preview + revestir F1.
- **Must vs. nice (Q2=B)**: todo lo anterior (incl. catálogo/preview) es must-have; variantes extra de componentes son nice (Could).
- **Dependencias (Q3=A)**: tokens → componentes → catálogo; revestir F1 depende de tokens + componentes.
- **Secuenciación (Q4=B)**: risk-first — spike de tokens + 1 componente validado en claro/oscuro contra Angular, luego el resto por dependencias.
- **Deadlines (Q5=A)**: ninguno.
- **Boundary (Q6=A)**: fuera tab bar nativa (B-08→F2), aplicación a pantallas de F2, animaciones avanzadas, temas más allá de claro/oscuro, dependencias de pago.

Backlog priorizado: DS-01 (spike fidelidad) → DS-02/03/04 (tokens) → DS-05 (componentes) → DS-06 (catálogo) → DS-07 (revestir F1); DS-08 (variantes) Could.

¿Está todo correcto?

[Answer]: Looks correct
