# Requirements — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, Material 3, VoiceOver, Apple HIG, iOS Keychain) verbatim en inglés.
> IDs FR/NFR permanentes (claves de trazabilidad). Trazan a la ideación (intent-statement, scope-document) y al tema de Angular como fuente de verdad.

## Intent analysis

El objetivo es dotar a la app nativa iOS de una **capa de diseño reutilizable en SwiftUI** que reproduzca el tema del frontend Angular existente, de modo que las pantallas de F2 se construyan sobre una base común y coherente y el login de F1 quede revestido sin cambios de comportamiento. No es un producto de mercado: es una base técnica/visual para acelerar y homogeneizar la construcción nativa, a coste 0 €. [intent-statement] [scope-document]

## Functional requirements

### FR1 — Tokens de color
- **FR1.1** El sistema define tokens de color semánticos que reproducen los roles clave del tema Angular Material 3: `primary` (verde), `tertiary` (violeta), `surface`/`on-surface` y sus variantes. [Q1]
- **FR1.2** El sistema define los tokens semánticos propios del proyecto: `money-positive` y `money-negative`, con sus valores de claro y oscuro. [Q1]
- **FR1.3** El sistema define el gradiente de splash verde como token/recurso reutilizable. [Q1]
- **FR1.4** Todos los tokens de color tienen variante para modo claro y modo oscuro, resolviéndose automáticamente según el modo del sistema. [Q1] [Q7]

### FR2 — Tipografía
- **FR2.1** El sistema define una escala tipográfica `h1`/`h2`/`h3` + body basada en Roboto. [Q2]
- **FR2.2** Todos los estilos tipográficos soportan Dynamic Type (el texto escala con el ajuste de tamaño del sistema). [Q2]
- **FR2.3** Si Roboto no está disponible como fuente empaquetada, se usa la fuente del sistema con la misma escala (fallback). [Q2]

### FR3 — Espaciado
- **FR3.1** El sistema define una escala de espaciado reutilizable con pasos fijos `xs=4`, `sm=8`, `md=16`, `lg=24`, `xl=32` (puntos), usada por los componentes; los valores exactos pueden afinarse en design pero el conjunto de pasos queda comprometido. [Q3] [Q7]

### FR4 — Componentes base (SwiftUI)
- **FR4.1** Botón primario con estados normal, disabled y loading. [Q3]
- **FR4.2** Campo de texto con label, icono opcional y estado de error. [Q3]
- **FR4.3** Tarjeta (superficie contenedora) alineada con los tokens de surface. [Q3]
- **FR4.4** Estados de carga y de error reutilizables. [Q3]
- **FR4.5** Todos los componentes consumen los tokens (FR1–FR3) y responden a claro/oscuro sin estilos ad-hoc por pantalla. [Q3] [Q1]

### FR5 — Pantalla de catálogo/preview
- **FR5.1** Una pantalla de catálogo muestra todos los tokens (colores, tipografía, espaciado) y todos los componentes base. [Q7]
- **FR5.2** El catálogo ofrece un control para alternar modo claro/oscuro y otro para variar el tamaño de Dynamic Type, permitiendo verificar los componentes de un vistazo contra el tema de Angular. [Q7]

### FR6 — Revestir el login de F1
- **FR6.1** El login de F1 se reviste con el sistema de diseño (campos, botón, estados y colores del sistema). [Q4]
- **FR6.2** El login revestido conserva el comportamiento funcional de F1 sin cambios: login → auto-login (Keychain) → logout, validación y mensajes de error. Criterio de "sin regresión" verificable manualmente en el iPhone 13 Pro. [Q4]

## Non-functional requirements

- **NFR1 — Accesibilidad**: todos los componentes base soportan Dynamic Type; el contraste de color cumple un ratio mínimo de **4.5:1 para texto normal y 3:1 para texto grande (≥ 24 pt o ≥ 19 pt bold) y elementos de UI**, tanto en claro como en oscuro, comprobable con el Accessibility Inspector de Xcode; los componentes exponen etiquetas/roles correctos para VoiceOver. Objetivo alineado con WCAG AA donde aplique a móvil nativo (sin herramienta de auditoría de pago). [Q5]
- **NFR2 — Coste y dependencias**: el sistema se construye únicamente con el SDK de Apple; coste 0 € recurrente; sin dependencias de pago ni tooling de diseño de pago. [Q6] [memory:project.md Mandated]
- **NFR3 — Fidelidad al tema de referencia**: el resultado visual reproduce fielmente los tokens de color (FR1), tipografía (FR2) y espaciado (FR3) del tema del frontend Angular (`angular-app/src/styles.scss`). Criterio de aceptación: verificación visual lado a lado en la pantalla de catálogo (FR5.2), en claro y oscuro, contra el tema de Angular. Donde Material 3 no tenga equivalente 1:1 en SwiftUI, se cubre con Apple HIG. [Q1] [memory:project.md Corrections]
- **NFR4 — Dispositivo**: dispositivo de referencia iPhone 13 Pro (vertical); el sistema escala a otros iPhone vía Dynamic Type y layout adaptable. [Q7]

## Constraints

- Sólo SDK de Apple / SwiftUI; capa autocontenida que encaja con la estructura SwiftPM/`xtool.yml` del proyecto iOS de F1. [constraint-register]
- Google Stitch descartado como referencia; la única fuente de verdad del diseño es el tema de Angular. [memory:project.md]

## Out of scope

- Navegación / tab bar nativa (B-08) — corresponde a F2. [Q8]
- Aplicación del sistema a las pantallas de datos de F2. [Q8]
- Animaciones/transiciones avanzadas y microinteracciones. [Q8]
- Temas adicionales más allá de claro/oscuro (alto contraste, temas de marca). [Q8]
- Arnés de test de UI nativo (XCTest/snapshot) y su umbral — diferido a F2 / intent de tooling. [Q8]
- Cualquier cambio de backend o de CI/CD. [Q8]

## Assumptions & Open Questions

- [assumption] Los valores hex concretos del tema de Angular se mapearán a color sets SwiftUI (claro/oscuro) en functional-design / code-generation; aquí se fijan los roles, no los hex. [Q1]
- [assumption] El proyecto iOS de F1 admite añadir la capa de diseño como módulo/estructura SwiftPM sin refactor mayor. [constraint-register]
- Open question: mapeo exacto de valores hex del tema Angular → color sets SwiftUI (claro/oscuro), a concretar en functional-design. [Q1]
