# Requirements Analysis — Preguntas de clarificación (re-run tras ampliación FR5)

Intent: `calculadora-mejora`. Re-ejecución tras probar en local: se amplía el
comportamiento del toggle OFF (FR5).

## Q1 — Comportamiento del toggle OFF (ampliación detectada en pruebas)

Con el toggle OFF no basta con atenuar el importe "En venta": los jugadores en
venta deben poder simularse "desde cero".

- A. Con OFF: ocultar el bloque "En venta" (sección de tarjetas) y devolver esos jugadores a la lista seleccionable, **deseleccionados**. Con ON, comportamiento actual.
- B. Con OFF: igual que A pero los jugadores en venta entran **preseleccionados**.
- C. Mantener solo la atenuación (sin reubicar jugadores).
- X. Other (please specify)

[Answer]: A — Con el toggle OFF se oculta el bloque "En venta" y los jugadores en venta pasan a la lista seleccionable DESELECCIONADOS; con ON se mantiene el comportamiento actual (bloque visible, jugadores excluidos de la lista, `onSaleTotal` sumado). Formalizado como FR5.1–FR5.4.

---

## Consolidated Summary Confirmation

- **Toggle** "Incorporar jugadores en venta" (ON por defecto, persistido en `localStorage` `futmondo_calc_include_onsale`, fallback a ON).
- **ON**: `futureBalance` suma `onSaleTotal`; bloque "En venta" visible; jugadores en venta EXCLUIDOS de la lista seleccionable (comportamiento actual).
- **OFF**: `futureBalance` NO suma `onSaleTotal`; bloque "En venta" OCULTO; jugadores en venta en la lista seleccionable, DESELECCIONADOS, para simular su venta desde cero.
- **Invariante**: `activeBidsTotal` siempre resta (ON y OFF).
- **Reactivo**: alternar el toggle reconstruye la lista y recalcula sin recargar.
- **Alcance**: solo frontend; sin datos/endpoints nuevos; coste 0 €; PWA; gate de CI; no cambiar la fórmula lineal base.
- **Trazabilidad**: FR1 (cálculo), FR2 (invariante), FR3 (persistencia), FR4 (preservación de venta/datos), FR5 (reubicación bloque + lista).

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
