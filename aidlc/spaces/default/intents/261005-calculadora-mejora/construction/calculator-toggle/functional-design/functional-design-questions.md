# Functional Design — Preguntas (unidad: calculator-toggle) — re-run tras FR5

Diseño actualizado para cubrir el alcance ampliado (FR5): con el toggle OFF se
oculta el bloque "En venta" y los jugadores en venta pasan a la lista
seleccionable, deseleccionados. Las decisiones de diseño ya se cerraron en
Requisitos; no hay preguntas abiertas nuevas.

## Consolidated Summary Confirmation

- **Unidad**: `calculator-toggle` (frontend-only, Angular `calculator.component.ts` + `.html` + `.scss`).
- **Toggle**: `mat-slide-toggle` "Incorporar jugadores en venta" en la cabecera de resumen (`.calc-header`).
- **Cálculo**: `futureBalance` incluye `onSaleTotal` solo con ON; con OFF = `balance + selectedTotal - activeBidsTotal`. `activeBidsTotal` siempre resta.
- **Bloque "En venta"**: visible con ON; OCULTO con OFF (FR5.1/FR5.2, BR4.1).
- **Lista seleccionable**: con ON excluye los jugadores en venta; con OFF los incluye DESELECCIONADOS (FR5.1–FR5.3, BR5.1/BR5.2). Reconstrucción reactiva; al volver a ON se re-excluyen y se limpia su selección manual (FR5.4, BR5.3).
- **Invariante anti-doble-conteo**: un jugador en venta aporta por una sola vía (`onSaleTotal` con ON o `selectedTotal` si se selecciona con OFF), nunca ambas (FR5.5, BR5.4).
- **Persistencia**: `localStorage` `futmondo_calc_include_onsale`; restaura al cargar; por defecto ON; corrupto/ausente → ON.
- **Sin cambios** en vender, fuentes de datos ni backend.
- **Tests** (characterization-first): ON/OFF del cálculo, visibilidad del bloque, composición de la lista, invariante anti-doble-conteo, transición OFF→ON, persistencia/fallback.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
