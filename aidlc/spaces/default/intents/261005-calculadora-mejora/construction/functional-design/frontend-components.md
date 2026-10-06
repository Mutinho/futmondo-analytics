# Frontend Components — calculator-toggle

Diseño del cambio frontend sobre el componente existente `CalculatorComponent`
(`angular-app/src/app/features/calculator/`). Angular 22, standalone, signals,
`OnPush`. No se crea un componente nuevo: se extiende el existente.

## Jerarquía de componentes

- `CalculatorComponent` (existente) — se extiende:
  - Nueva señal de estado `includeOnSale: WritableSignal<boolean>`.
  - Nuevo control en la cabecera de resumen (`.calc-header`): `mat-slide-toggle`
    etiquetado "Incorporar jugadores en venta" (import `MatSlideToggleModule`).
  - El `computed()` `futureBalance` existente se modifica para condicionar
    `onSaleTotal` a `includeOnSale`.
  - El bloque "En venta" (sección de tarjetas `onSalePlayers`) se MUESTRA solo
    si `includeOnSale()`; se oculta con `@if` cuando es `false` (BR4.1).
  - La lista seleccionable (`players`/`dataSource`) se construye incluyendo o
    excluyendo los jugadores en venta según `includeOnSale()` (BR5.1).

## Estado y props

| Señal / dato | Tipo | Origen | Notas |
|--------------|------|--------|-------|
| `includeOnSale` | `WritableSignal<boolean>` | `localStorage` (`futmondo_calc_include_onsale`) con default/fallback ON | Nueva (BR3.1–BR3.4) |
| `onSaleTotal` | `Signal<number>` (computed) | existente | Sin cambios de cálculo |
| `activeBidsTotal` | `Signal<number>` | existente | Siempre resta (BR2.1) |
| `futureBalance` | `Signal<number>` (computed) | existente, **modificado** | Condiciona `onSaleTotal` a `includeOnSale` (BR1.1/BR1.2) |
| lista seleccionable | `players`/`dataSource` | existente, **modificado** | Incluye `onSalePlayers` solo con OFF; reconstrucción reactiva al cambiar el toggle (BR5.1/BR5.3) |

## Flujos de interacción

1. **Init**: leer `localStorage` y fijar `includeOnSale` (helper con fallback a
   `true` — BR3.3/BR3.4). Construir la lista seleccionable según `includeOnSale`
   (WF4): con ON excluir `onSaleIds`, con OFF incluirlos deseleccionados.
2. **Toggle change**: `setIncludeOnSale(value)` → `includeOnSale.set(value)` +
   persistir en `localStorage` (BR3.1); reconstruir la lista seleccionable
   (BR5.3): al pasar a ON, re-excluir `onSaleIds` y limpiar de `selectedIds`
   cualquier jugador en venta previamente marcado.
3. **Recálculo**: `futureBalance` (computed) reacciona a `includeOnSale`,
   `selectedTotal` y `onSaleTotal`.

## Snippet ilustrativo (≤15 líneas, interface-level)

```ts
// Lista seleccionable según el toggle (BR5.1): con ON excluye onSale, con OFF los incluye
selectable = computed(() => {
  const onSaleIds = new Set(this.onSalePlayers().map(p => p.player_id));
  return this.includeOnSale()
    ? this.roster().filter(p => !onSaleIds.has(p.player_id))
    : this.roster();
});

setIncludeOnSale(v: boolean) {                 // BR3.1 + BR5.3
  this.includeOnSale.set(v);
  localStorage.setItem('futmondo_calc_include_onsale', String(v));
  if (v) this.dropOnSaleFromSelection();       // re-exclude + clear manual selection
}
```

## Validación de formulario / accesibilidad (NFR2)

- `mat-slide-toggle` con etiqueta de texto asociada "Incorporar jugadores en venta".
- Operable por teclado (foco visible + Espacio/Enter — provisto por Material).
- Estado on/off accesible vía rol switch / `aria-checked` del componente Material.

## Puntos de integración con API

- Ninguno nuevo. Se siguen usando `getMyRoster()`, `GET /api/v1/market/today`,
  `getOnSale()` como hoy. Sin cambios de backend.

## Tests (NFR4, characterization-first)

- Caracterizar primero el `futureBalance` y la lista seleccionable actuales
  (toggle implícito ON) con un spec.
- Specs nuevos que aseveran: ON incluye `onSaleTotal` y excluye los jugadores en
  venta de la lista; OFF excluye `onSaleTotal`, muestra esos jugadores en la
  lista deseleccionados y oculta el bloque "En venta"; invariante anti-doble-conteo
  (BR5.4) al seleccionar un ex-onSale con OFF; transición OFF→ON re-excluye y
  limpia la selección (BR5.3); pujas siempre restan; persistencia y
  restauración/fallback de `localStorage`.

## Sources

- `requirements.md` (FR1–FR5, NFR2, NFR4), `functional-design-questions.md`.
- Código: `calculator.component.ts` (`futureBalance`, `onSaleTotal`, `loadData` filtrado `onSaleIds`, `setViewMode`, patrón `localStorage`).

## Assumptions & Open Questions

None.
