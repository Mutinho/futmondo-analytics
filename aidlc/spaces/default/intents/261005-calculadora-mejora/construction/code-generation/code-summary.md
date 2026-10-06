# Code Summary — calculator-toggle

Mejora frontend-only, brownfield, in-place: toggle "Incorporar jugadores en
venta" en la pantalla Calculadora (`/calculator`). La inclusión de los jugadores
en venta en la proyección de saldo futuro pasa a ser opcional y persistente por
usuario, sin tocar backend ni la fórmula base.

## Ficheros modificados / creados

| Fichero | Acción | Qué cambió |
|---------|--------|------------|
| `angular-app/src/app/features/calculator/calculator.component.ts` | Modificado | Import `MatSlideToggleModule` + alta en `imports`; señal `includeOnSale: WritableSignal<boolean>` (restaura de `localStorage` con fallback a ON); `futureBalance` condiciona `onSaleTotal` a `includeOnSale()` (resta de `activeBidsTotal` siempre). **FR5**: nuevas señales privadas `rawRoster` y `onSaleIds`; `loadData()` guarda el roster completo + el set de IDs en venta y delega la composición en `rebuildSelectable()` (ON excluye en venta, OFF los incluye deseleccionados — BR5.1/BR5.2); `setIncludeOnSale(v)` persiste, al pasar a ON limpia de `selectedIds` cualquier ex-onSale (BR5.3/BR5.4) y reconstruye la lista; `sellPlayers()` poda también `rawRoster` para mantener coherencia. |
| `angular-app/src/app/features/calculator/calculator.component.html` | Modificado | `mat-slide-toggle` etiquetado "Incorporar jugadores en venta" dentro de `.calc-header`, enlazado a `includeOnSale()`/`setIncludeOnSale($event.checked)`. **FR5**: la sección de tarjetas "En venta" (`.on-sale-section`) se envuelve con `@if (includeOnSale() && onSalePlayers().length > 0)` → se OCULTA con el toggle OFF (BR4.1/FR5.2). Se retira el enfoque previo de "atenuar el importe" (`on-sale-excluded`). |
| `angular-app/src/app/features/calculator/calculator.component.scss` | Modificado | Alineación del toggle (`.calc-header-toggle`); **FR5**: eliminada la regla `.calc-header-value.on-sale-excluded` (enfoque de atenuar reemplazado por ocultar el bloque). |
| `angular-app/src/app/features/calculator/calculator.component.spec.ts` | Modificado | Spec ampliado: characterization-first + aserción de efecto; **FR5**: 4 specs nuevos sobre la composición de la lista seleccionable, deselección, invariante anti-doble-conteo y transición OFF→ON (13 specs en total). |

## Decisiones clave

- **Restauración/fallback en la inicialización de la señal** (no en un `effect`):
  `localStorage.getItem('futmondo_calc_include_onsale') === 'false' ? false : true`.
  Cualquier valor distinto del literal `'false'` (ausente, corrupto, no booleano)
  resuelve a `true` → cubre BR3.2/BR3.3/BR3.4 en una sola expresión determinista,
  sin try/catch (ninguna rama lanza).
- **Patrón espejo de `setViewMode`**: `setIncludeOnSale(v)` replica el patrón ya
  presente de persistencia en `localStorage` (`futmondo_view_calculator`), para
  consistencia con el código existente.
- **`futureBalance` reactivo** (computed signal): el cambio del toggle recalcula
  sin recargar (BR1.3/FR1.4). `activeBidsTotal` queda fuera del condicional
  (invariante BR2.1).
- **UI con Material estándar**: `mat-slide-toggle` aporta rol switch + estado
  `aria-checked` + operabilidad por teclado (NFR2) sin dependencias nuevas
  (`@angular/material` ya es dependencia, `^22.2.1`).
- **FR5 — composición reactiva de la lista seleccionable**: en vez de filtrar
  los en-venta de forma incondicional, se guarda el roster crudo (`rawRoster`) y
  el set `onSaleIds` y se deriva la lista activa en `rebuildSelectable()`. Con ON
  se excluyen (su valor cuenta vía `onSaleTotal`), con OFF se incluyen
  deseleccionados (BR5.1/BR5.2). `setIncludeOnSale` reconstruye sin recargar
  (BR5.3) y, al volver a ON, descarta la selección manual de los ex-onSale para
  garantizar la invariante anti-doble-conteo (BR5.4): un jugador en venta aporta
  por una sola vía.
- **Ocultar el bloque "En venta" (BR4.1/FR5.2)**: el enfoque previo de atenuar el
  importe de cabecera se reemplaza por ocultar la sección de tarjetas con
  `@if (includeOnSale() && …)`, conforme a FR5.2 (feedback de la prueba local).

## Resumen de cobertura de tests

Spec `calculator.component.spec.ts` — **13 tests, todos verdes**; suite completa
del frontend **75/75 verde** (ver Issues para el resultado exacto). Mapeo:

1. Characterization: `futureBalance` actual (ON-equivalente) = `balance + selectedTotal + onSaleTotal - activeBidsTotal` (NFR4).
2. ON incluye `onSaleTotal` (FR1.2/BR1.1).
3. OFF excluye `onSaleTotal` (FR1.3/BR1.2).
4. `activeBidsTotal` resta en ON y en OFF; la única diferencia ON↔OFF es `onSaleTotal` (FR2.1/BR2.1).
5. Cambiar el toggle persiste `'true'`/`'false'` en `localStorage` (FR3.1/BR3.1).
6. Restaura ON con `'true'` y OFF con `'false'` (FR3.2/BR3.2).
7. Fallback a ON ante clave ausente (FR3.3/BR3.3) y valor corrupto (`'maybe'`) (FR3.4/BR3.4).
8. **FR5** — con ON la lista seleccionable excluye los en-venta (FR5.1/BR5.1).
9. **FR5** — con OFF la lista incluye los en-venta deseleccionados y excluye `onSaleTotal` (FR5.2/FR5.3/BR5.2).
10. **FR5** — invariante anti-doble-conteo: con OFF seleccionar un ex-onSale suma a `selectedTotal` una sola vez (FR5.5/BR5.4).
11. **FR5** — transición OFF→ON re-excluye los en-venta y limpia su selección manual (FR5.4/BR5.3).

Las aserciones son de EFECTO (valor calculado de `futureBalance`, composición de
`players()`/`dataSource.data`, estado de `selectedIds`/`localStorage`), sin
`assert`/`expect(true)` ni specs espejo.

## Desviaciones

- **Ejecución de tests en contenedor**: el Node local es `22.22.1`, por debajo
  del mínimo del Angular CLI (`22.22.3`). Siguiendo la práctica afirmada, el
  comando unit-scoped se ejecutó en contenedor `node:22.22.3` a coste 0 €. El
  `node_modules` del host estaba incompleto (faltaban `jsdom` y
  `@vitest/coverage-v8`, ambos ya declarados en `package.json`); se ejecutó
  `npm ci` dentro del contenedor para instalar las dependencias ya declaradas
  (sin añadir dependencias nuevas).
- **Umbral de cobertura del comando unit-scoped**: el comando acotado a un solo
  spec reporta cobertura global por debajo del umbral de `angular.json` (es
  esperado: calcula cobertura de TODO el código ejecutando un único fichero). NO
  es una regresión; los umbrales de `angular.json` NO se tocaron (el ratchet solo
  sube). El gate real de CI corre el `ng test` completo del proyecto.
- **Advertencias `SpanishDateAdapter` DI deprecation**: pre-existentes
  (brownfield), provienen de los `providers` ya presentes del componente; no las
  introduce este cambio y no se abordan (fuera de alcance, frontend-only acotado).
