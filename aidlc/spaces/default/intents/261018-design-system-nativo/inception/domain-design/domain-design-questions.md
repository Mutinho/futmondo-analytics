# Domain Design — Preguntas de clarificación

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, SwiftPM, DesignTokens) verbatim en inglés.
> Componentes lógicos (bloques de software) del sistema de diseño. Rellena cada `[Answer]:`.

## Q1. Decomposición en componentes

- A. Cuatro bloques: `DesignTokens` (color/tipografía/espaciado), `DesignComponents` (botón, campo, tarjeta, estados), `DesignCatalog` (pantalla de catálogo/preview) y `LoginTheming` (revestimiento del login de F1). DesignComponents y DesignCatalog dependen de DesignTokens; LoginTheming depende de DesignComponents + DesignTokens.
- B. Dos bloques: `DesignSystem` (tokens + componentes juntos) y `DesignCatalog`.
- X. Other (please specify)

[Answer]: A. Cuatro bloques: DesignTokens, DesignComponents, DesignCatalog, LoginTheming (con sus dependencias).

## Q2. ¿Son componentes "sin entidades de dominio" (UI/presentación)?

- A. Sí: es una capa de presentación; no hay entidades de datos persistentes propias. Los "tokens" son constantes/recursos, no entidades de dominio. (entities: [] en el catálogo.)
- B. Modelar los tokens como entidades.
- X. Other (please specify)

[Answer]: A. Sí: capa de presentación, sin entidades de datos persistentes; tokens como constantes/recursos (entities: []).

## Consolidated Summary Confirmation

Resumen de Domain Design:

- **Decomposición (Q1=A)**: cuatro componentes — `DesignTokens` (base), `DesignComponents`, `DesignCatalog`, `LoginTheming`. Grafo acíclico.
- **Sin entidades (Q2=A)**: capa de presentación; tokens como constantes/recursos.
- **ADRs**: ADR-001 (4 bloques vs. DesignSystem único) y ADR-002 (tokens no son entidades).
- **Trazabilidad**: US1.1–1.3→DesignTokens, US2.1→DesignComponents, US3.1→DesignCatalog, US4.1→LoginTheming.

¿Does this all look correct?

[Answer]: Looks correct
