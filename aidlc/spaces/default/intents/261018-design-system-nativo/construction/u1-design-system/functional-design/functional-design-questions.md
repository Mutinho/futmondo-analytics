# Functional Design — U1 `u1-design-system` — Preguntas

> Fase: construcción. Idioma: castellano; tokens técnicos (SwiftUI, Color Assets, DesignTokens, Dynamic Type) verbatim en inglés.
> Diseño funcional de la librería del sistema de diseño (tokens + componentes + catálogo). Acotado por refined-mockups y contract-summary. Rellena cada `[Answer]:`.

## Q1. Modelo de "entidades" de la librería

- A. Sin entidades de datos persistentes (coherente con domain-design): los tokens son constantes/recursos. `entities.md` describirá los **grupos de tokens** (color, tipografía, espaciado) como estructuras de configuración ligeras (no entidades de dominio con identidad), y el foco del diseño funcional serán las **reglas** (resolución de tema, Dynamic Type, contraste) y el **functional-spec** (workflows del catálogo + componentes).
- B. Modelar entidades de datos formales.
- X. Other (please specify)

[Answer]: A. Sin entidades persistentes; tokens como estructuras de config ligeras; foco en reglas + functional-spec.

## Q2. Reglas de negocio a capturar (BR)

- A. Las esperables de un sistema de diseño: resolución de color según modo claro/oscuro (BR de color), escalado de tipografía con Dynamic Type (BR de tipografía), estados de componente (botón normal/disabled/loading; campo normal/foco/error), y el objetivo de contraste (≥4.5:1 / ≥3:1) como regla de validación de diseño.
- B. Not yet defined.
- X. Other (please specify)

[Answer]: A. Reglas: resolución de color claro/oscuro, escalado Dynamic Type, estados de componente y objetivo de contraste.

## Q3. Alcance del functional-spec y frontend-components

- A. functional-spec = workflow del catálogo (abrir → alternar tema/tamaño → ver secciones) + especificación de interacción de cada componente; frontend-components = jerarquía SwiftUI (CatalogView → secciones → componentes) con props/estado de cada componente. Sin API de red.
- B. Not yet defined.
- X. Other (please specify)

[Answer]: A. functional-spec = workflow del catálogo + interacción por componente; frontend-components = jerarquía SwiftUI con props/estado. Sin API de red.

## Consolidated Summary Confirmation

Resumen de Functional Design — U1 `u1-design-system`:

- **Entidades (Q1=A)**: sin entidades persistentes; grupos de tokens (ColorToken, TypographyToken, SpacingToken, SplashGradient) como config ligera.
- **Reglas (Q2=A)**: BR1.1 color claro/oscuro, BR1.2 Dynamic Type, BR1.3 fallback fuente, BR1.4 contraste (≥4.5:1 / ≥3:1), BR2.1 estados botón, BR2.2 estados campo.
- **Functional-spec / frontend-components (Q3=A)**: workflow W1 del catálogo + interacción por componente; jerarquía SwiftUI (CatalogView → secciones → componentes) con props/estado; sin API de red.
- **Trazabilidad**: ACs de US1.1–US3.1 mapeadas a BRs; espaciado/Card/mostrar-catálogo como N/A justificado.

¿Does this all look correct?

[Answer]: Looks correct
