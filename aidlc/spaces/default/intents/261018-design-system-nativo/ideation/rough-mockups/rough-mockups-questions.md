# Rough Mockups & Concept Visualization — Preguntas de clarificación

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, Material 3, WCAG, Apple HIG) verbatim en inglés.
> Wireframes de baja fidelidad para un sistema de diseño: la "UI" aquí es la pantalla de catálogo/preview + el login de F1 revestido. Rellena cada `[Answer]:`.

## Q1. ¿Cuáles son las pantallas/vistas clave de este intent?

- A. Dos: (1) **Catálogo/preview** del sistema de diseño (muestra tokens de color, tipografía y los componentes base en claro/oscuro y varios tamaños de Dynamic Type) y (2) el **login de F1 revestido** con el sistema.
- B. Sólo la pantalla de catálogo/preview.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Dos: catálogo/preview del sistema de diseño y el login de F1 revestido.

## Q2. ¿Cuál es el flujo principal (happy path)?

- A. Abrir la app en modo desarrollo → navegar al catálogo → alternar claro/oscuro y tamaño de texto para verificar los componentes; en paralelo, el login revestido se ve igual que antes pero con el nuevo estilo.
- B. Not applicable (no hay flujo de usuario, es una capa técnica).
- X. Other (please specify)

[Answer]: A. Abrir en modo desarrollo → navegar al catálogo → alternar claro/oscuro y tamaño de texto para verificar los componentes; el login revestido se ve igual pero con el nuevo estilo.

## Q3. ¿Jerarquía de información del catálogo?

- A. Secciones: Colores (tokens claro/oscuro) → Tipografía (escala + Dynamic Type) → Espaciado → Componentes (botón, campo, tarjeta, estados de carga/error), cada uno con su preview.
- B. Not yet defined.
- X. Other (please specify)

[Answer]: A. Colores (tokens claro/oscuro) → Tipografía (escala + Dynamic Type) → Espaciado → Componentes (botón, campo, tarjeta, estados carga/error), cada uno con su preview.

## Q4. ¿Hay brand guidelines / design system / patrones a seguir?

- A. Sí: el tema del frontend Angular existente (`angular-app/src/styles.scss`) es la fuente de verdad — Material 3 paleta primaria verde (`mat.$green-palette`) / terciaria violeta, Roboto, claro/oscuro (`body.dark-theme`), tokens semánticos (`money-positive` `#2e7d32`/`#66bb6a`, `money-negative` `#d32f2f`/`#ef5350`, escala `h1/h2/h3`, gradiente de splash verde). Donde Material 3 no tenga equivalente 1:1 en SwiftUI, cubrir con Apple HIG. Google Stitch descartado.
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. Sí: el tema del frontend Angular (`angular-app/src/styles.scss`) como fuente de verdad (Material 3 verde/violeta, Roboto, claro/oscuro, tokens semánticos); donde Material 3 no tenga equivalente 1:1 en SwiftUI, cubrir con Apple HIG. Google Stitch descartado.

## Q5. ¿Qué dispositivos / form factors hay que soportar?

- A. iPhone 13 Pro (dispositivo de referencia del proyecto), orientación vertical; el sistema debe escalar a otros iPhone vía Dynamic Type y layout adaptable.
- B. Not yet defined.
- X. Other (please specify)

[Answer]: A. iPhone 13 Pro (dispositivo de referencia), orientación vertical; escalar a otros iPhone vía Dynamic Type y layout adaptable.

## Q6. ¿Requisitos de accesibilidad conocidos?

- A. Dynamic Type (texto escalable) como requisito central; contraste de color adecuado en claro/oscuro; compatibilidad con VoiceOver en los componentes base (etiquetas/roles correctos). Objetivo informal alineado con WCAG AA donde aplique a móvil nativo.
- B. Sólo Dynamic Type + contraste; VoiceOver se difiere.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Dynamic Type central; contraste adecuado en claro/oscuro; VoiceOver en los componentes base (etiquetas/roles); objetivo informal alineado con WCAG AA donde aplique a móvil nativo.

## Consolidated Summary Confirmation

Resumen de tus respuestas de Rough Mockups:

- **Pantallas (Q1=A)**: catálogo/preview del sistema + login de F1 revestido.
- **Flujo (Q2=A)**: abrir en desarrollo → catálogo → alternar claro/oscuro y tamaño de texto; login revestido igual que F1.
- **Jerarquía del catálogo (Q3=A)**: Colores → Tipografía → Espaciado → Componentes.
- **Referencia de diseño (Q4=A)**: tema de Angular (`angular-app/src/styles.scss`) como fuente de verdad; Apple HIG donde Material 3 no tenga equivalente 1:1; Stitch descartado.
- **Dispositivo (Q5=A)**: iPhone 13 Pro vertical; escalar vía Dynamic Type y layout adaptable.
- **Accesibilidad (Q6=A)**: Dynamic Type + contraste claro/oscuro + VoiceOver en componentes base; objetivo informal WCAG AA donde aplique.

Wireframes: catálogo (Colores/Tipografía/Espaciado/Componentes) + login revestido (card sobre gradiente verde, basado en el layout real de Angular).

¿Está todo correcto?

[Answer]: Looks correct
