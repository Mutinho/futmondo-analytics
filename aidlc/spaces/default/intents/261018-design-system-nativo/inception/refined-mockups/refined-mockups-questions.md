# Refined Mockups & UX Design — Preguntas de clarificación

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, Material 3, Color Assets, Dynamic Type, WCAG) verbatim en inglés.
> Concreta el mapeo del tema de Angular a SwiftUI. Rellena cada `[Answer]:`.

## Q1. ¿Cómo derivar los valores concretos de color del tema de Angular hacia SwiftUI?

El tema Angular usa `mat.$green-palette` / `mat.$violet-palette` (resueltos por Material en runtime) más hex explícitos en `styles.scss` (`#2e7d32`/`#66bb6a` money-+, `#d32f2f`/`#ef5350` money-−, gradiente splash `#1b5e20→#2e7d32→#43a047`).

- A. Fijar un conjunto representativo de hex por rol (primary verde, tertiary violeta, surface/on-surface, money-+/-, splash) tomando los hex explícitos del SCSS y, para primary/tertiary, los tonos canónicos de las paletas Material 3 (verde ~`#2e7d32` / violeta), definidos como Color Assets con variante clara/oscura. Pragmático y a coste 0 €.
- B. Extraer en runtime los valores exactos de `--mat-sys-*` ejecutando el frontend Angular y copiarlos uno a uno.
- X. Other (please specify)

[Answer]: A. Hex representativos por rol (del SCSS + paletas Material verde/violeta) como Color Assets claro/oscuro; pragmático y coste 0 €.

## Q2. ¿Cómo se materializan los tokens en SwiftUI?

- A. Color Assets del asset catalog (con "Any/Dark Appearance") para colores + una enum/estructura de tokens Swift (`DesignTokens`) para tipografía y espaciado. Idiomático y sin dependencias.
- B. Todo en código Swift (sin asset catalog).
- X. Other (please specify)

[Answer]: A. Color Assets (asset catalog, Any/Dark) + enum/estructura `DesignTokens` para tipografía y espaciado.

## Q3. Patrones de interacción y estados por pantalla — ¿alcance?

- A. Catálogo: scroll vertical por secciones + toggles (tema y tamaño de texto). Login revestido: estados de los componentes (normal, loading, error) heredados de F1. Sin modales ni wizards.
- B. Not yet defined.
- X. Other (please specify)

[Answer]: A. Catálogo con scroll + toggles (tema y tamaño de texto); login con estados heredados (normal/loading/error); sin modales ni wizards.

## Q4. Nivel de accesibilidad a documentar en el checklist

- A. WCAG AA donde aplique a móvil nativo: contraste ≥4.5:1 / ≥3:1, Dynamic Type, VoiceOver (labels/roles), áreas táctiles ≥44×44 pt. Verificable con Accessibility Inspector.
- B. Sólo contraste + Dynamic Type.
- X. Other (please specify)

[Answer]: A. WCAG AA móvil: contraste ≥4.5:1 / ≥3:1, Dynamic Type, VoiceOver (labels/roles), áreas táctiles ≥44×44 pt; verificable con Accessibility Inspector.

## Q5. Responsive / breakpoints

- A. iPhone vertical (referencia iPhone 13 Pro); layout adaptable por tamaño dinámico y safe areas; sin iPad ni landscape en este intent.
- B. Añadir iPad/landscape.
- X. Other (please specify)

[Answer]: A. iPhone vertical (referencia iPhone 13 Pro); layout adaptable por tamaño dinámico y safe areas; sin iPad ni landscape.

## Consolidated Summary Confirmation

Resumen de Refined Mockups:

- **Mapeo de color (Q1=A, Q2=A)**: hex representativos por rol (primary verde, tertiary violeta, surface, money-+/-, splash) como Color Assets claro/oscuro; tipografía y espaciado en `DesignTokens`.
- **Interacción (Q3=A)**: catálogo con toggles tema/texto; login con estados heredados; sin modales.
- **Accesibilidad (Q4=A)**: WCAG AA móvil (contraste, Dynamic Type, VoiceOver, táctil ≥44pt).
- **Responsive (Q5=A)**: iPhone vertical, sin iPad/landscape.

Artefactos: design-system-mapping.md (Material 3→SwiftUI), mockups.md (catálogo + login revestido), interaction-spec.md (componentes), accessibility-checklist.md.

¿Does this all look correct?

[Answer]: Looks correct
