# Units Generation — Plan de decomposición y preguntas

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, SwiftPM, library, ui) verbatim en inglés.
> Agrupa los 4 componentes (DesignTokens, DesignComponents, DesignCatalog, LoginTheming) en Units construibles. Rellena cada `[Answer]:`.

## Q1. Granularidad / estrategia de Units

- A. **Dos Units**: `u1-design-system` (kind `library`: DesignTokens + DesignComponents + DesignCatalog — la librería reutilizable y su catálogo) y `u2-login-theming` (kind `ui`: revestir el login de F1), con `u2` dependiente de `u1`. Permite construir y validar la librería antes de tocar F1.
- B. **Una Unit** única (`u1-design-system`, kind `library`) con todo incluido el revestimiento del login.
- C. **Tres o más Units** (separar catálogo y/o tokens).
- X. Other (please specify)

[Answer]: A. Dos Units: u1-design-system (library) y u2-login-theming (ui), con u2 → u1.

## Q2. Modelo de despliegue / integración

- A. Embebido en la app iOS existente (estructura SwiftPM/`xtool.yml` de F1); no hay despliegue independiente — es código cliente que se compila con la app. Sin cambios de backend/CI.
- B. Not yet defined.
- X. Other (please specify)

[Answer]: A. Embebido en la app iOS (SwiftPM/`xtool.yml` de F1); sin despliegue independiente ni cambios backend/CI.

## Q3. Paralelismo

- A. `u1` primero (librería), luego `u2` (revestir login) que depende de `u1`; sin paralelismo real al ser un único mantenedor y haber dependencia directa.
- B. Not applicable.
- X. Other (please specify)

[Answer]: A. u1 primero (librería), luego u2 (revestir login, depende de u1); sin paralelismo real.

## Consolidated Summary Confirmation

Resumen de Units Generation:

- **Dos Units (Q1=A)**: `U1 u1-design-system` (library: tokens + componentes + catálogo, complejidad M) y `U2 u2-login-theming` (ui: revestir F1, complejidad S); U2 depende de U1.
- **Despliegue (Q2=A)**: embebido en la app iOS (SwiftPM); sin despliegue independiente ni backend/CI.
- **Paralelismo (Q3=A)**: ninguno; U1 antes que U2 por dependencia directa.
- **Edge block** cycle-free; story map: U1 cubre US1.1–US3.1, U2 cubre US4.1.

¿Does this all look correct?

[Answer]: Looks correct
