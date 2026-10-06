# Business Rules — calculator-toggle

Reglas de la mejora del toggle "Incorporar jugadores en venta". IDs estables
`BR{group}.{seq}` (trazabilidad). Técnicamente agnósticas: describen el
comportamiento, no la implementación.

```yaml
rules:
  - id: BR1.1
    statement: "El saldo futuro incluye el total de jugadores en venta solo cuando la preferencia includeOnSale es true."
    category: calculation
    applies_to: FutureBalanceProjection
    trigger: "Al recalcular futureBalance (cambio de toggle, selección, fecha o carga de datos)."
    logic: "IF includeOnSale THEN futureBalance = balance + selectedTotal + onSaleTotal - activeBidsTotal."
    violation_behaviour: "N/A (regla de cálculo determinista)."
    source: FR1.2

  - id: BR1.2
    statement: "El saldo futuro excluye el total de jugadores en venta cuando la preferencia includeOnSale es false."
    category: calculation
    applies_to: FutureBalanceProjection
    trigger: "Al recalcular futureBalance."
    logic: "IF NOT includeOnSale THEN futureBalance = balance + selectedTotal - activeBidsTotal."
    violation_behaviour: "N/A (regla de cálculo determinista)."
    source: FR1.3

  - id: BR1.3
    statement: "El cambio de la preferencia recalcula el saldo futuro de forma reactiva, sin recargar ni requerir otra acción."
    category: policy
    applies_to: FutureBalanceProjection
    trigger: "Cambio del valor includeOnSale."
    logic: "IF includeOnSale cambia THEN futureBalance se recomputa inmediatamente (computed signal)."
    violation_behaviour: "N/A."
    source: FR1.4

  - id: BR2.1
    statement: "El total de pujas activas siempre se resta del saldo futuro, con independencia de includeOnSale."
    category: constraint
    applies_to: FutureBalanceProjection
    trigger: "Al recalcular futureBalance."
    logic: "activeBidsTotal se resta SIEMPRE (ON y OFF). Invariante."
    violation_behaviour: "Un cálculo que no reste activeBidsTotal es incorrecto."
    source: FR2.1

  - id: BR3.1
    statement: "La preferencia includeOnSale se persiste en localStorage bajo la clave futmondo_calc_include_onsale."
    category: policy
    applies_to: IncludeOnSalePreference
    trigger: "Cambio del valor includeOnSale."
    logic: "ON write: localStorage[futmondo_calc_include_onsale] = ('true' | 'false')."
    violation_behaviour: "N/A."
    source: FR3.1

  - id: BR3.2
    statement: "Al cargar la pantalla, la preferencia se restaura desde localStorage."
    category: policy
    applies_to: IncludeOnSalePreference
    trigger: "Inicialización del componente Calculadora."
    logic: "includeOnSale = parse(localStorage[futmondo_calc_include_onsale])."
    violation_behaviour: "N/A."
    source: FR3.2

  - id: BR3.3
    statement: "La preferencia por defecto (sin valor guardado) es true (incluye jugadores en venta), preservando el comportamiento actual."
    category: policy
    applies_to: IncludeOnSalePreference
    trigger: "Inicialización sin valor en localStorage."
    logic: "IF localStorage no tiene la clave THEN includeOnSale = true."
    violation_behaviour: "N/A."
    source: FR3.3

  - id: BR3.4
    statement: "Un valor almacenado corrupto, ausente o no parseable a booleano se trata como 'sin valor' -> true, sin error ni render roto."
    category: validation
    applies_to: IncludeOnSalePreference
    trigger: "Inicialización con valor de localStorage no igual a 'true' ni 'false'."
    logic: "IF stored NOT IN {'true','false'} THEN includeOnSale = true (misma vía que BR3.3)."
    violation_behaviour: "Nunca lanzar excepción ni bloquear el render por un valor inválido."
    source: FR3.4

  - id: BR4.1
    statement: "Con includeOnSale = false, el bloque 'En venta' (seccion de tarjetas onSalePlayers) se OCULTA; con includeOnSale = true se muestra como hoy."
    category: policy
    applies_to: Calculator UI (seccion En venta)
    trigger: "Render de la pantalla segun includeOnSale."
    logic: "IF NOT includeOnSale THEN ocultar la seccion de tarjetas 'En venta' ELSE mostrarla."
    violation_behaviour: "N/A (regla de presentación)."
    source: FR5.1, FR5.2

  - id: BR5.1
    statement: "La lista seleccionable incluye los jugadores en venta solo cuando includeOnSale = false; con true quedan excluidos (comportamiento actual)."
    category: policy
    applies_to: Calculator selectable list
    trigger: "Construccion/reconstruccion de la lista seleccionable (carga o cambio del toggle)."
    logic: "IF includeOnSale THEN excluir onSalePlayers de la lista ELSE incluirlos."
    violation_behaviour: "N/A."
    source: FR5.1, FR5.2

  - id: BR5.2
    statement: "Los jugadores en venta que entran a la lista seleccionable (toggle OFF) entran deseleccionados."
    category: policy
    applies_to: Calculator selection state
    trigger: "Al incluir onSalePlayers en la lista seleccionable."
    logic: "IF NOT includeOnSale THEN los onSalePlayers añadidos NO estan en selectedIds por defecto."
    violation_behaviour: "N/A."
    source: FR5.3

  - id: BR5.3
    statement: "Alternar el toggle reconstruye la lista seleccionable de forma reactiva, sin recargar; al volver a ON los onSalePlayers se re-excluyen y su seleccion manual previa se descarta."
    category: policy
    applies_to: Calculator selectable list + selection state
    trigger: "Cambio de includeOnSale."
    logic: "IF includeOnSale pasa a true THEN excluir onSalePlayers de la lista y limpiar su seleccion manual; su valor vuelve a contar via onSaleTotal (BR1.1)."
    violation_behaviour: "N/A."
    source: FR5.4

  - id: BR5.4
    statement: "Invariante anti-doble-conteo: un jugador en venta aporta su valor por una sola via (onSaleTotal con ON, o selectedTotal si se selecciona con OFF), nunca ambas."
    category: constraint
    applies_to: FutureBalanceProjection
    trigger: "Al recalcular futureBalance con jugadores en venta presentes."
    logic: "IF includeOnSale THEN su valor cuenta via onSaleTotal y NO puede estar en selectedTotal (excluido de la lista); IF NOT includeOnSale THEN su valor cuenta via selectedTotal solo si seleccionado, y NO via onSaleTotal (excluido de la suma)."
    violation_behaviour: "Un cálculo que sume el mismo jugador por ambas vías es incorrecto."
    source: FR5.5
```

## Resumen de reglas

| ID | Categoría | Resumen | Fuente |
|------|-----------|---------|--------|
| BR1.1 | calculation | Incluir `onSaleTotal` si toggle ON | FR1.2 |
| BR1.2 | calculation | Excluir `onSaleTotal` si toggle OFF | FR1.3 |
| BR1.3 | policy | Recalcular reactivo al cambiar el toggle | FR1.4 |
| BR2.1 | constraint | `activeBidsTotal` siempre resta (invariante) | FR2.1 |
| BR3.1 | policy | Persistir en `localStorage` (`futmondo_calc_include_onsale`) | FR3.1 |
| BR3.2 | policy | Restaurar desde `localStorage` al cargar | FR3.2 |
| BR3.3 | policy | Por defecto ON sin valor guardado | FR3.3 |
| BR3.4 | validation | Valor inválido → ON, sin error | FR3.4 |
| BR4.1 | policy | Bloque "En venta" oculto con toggle OFF | FR5.1/FR5.2 |
| BR5.1 | policy | Lista seleccionable incluye onSale solo con OFF | FR5.1/FR5.2 |
| BR5.2 | policy | onSale entran deseleccionados con OFF | FR5.3 |
| BR5.3 | policy | Reconstrucción reactiva; OFF→ON re-excluye y limpia selección | FR5.4 |
| BR5.4 | constraint | Invariante anti-doble-conteo (una sola vía) | FR5.5 |

## Sources

- `requirements.md` (FR1–FR5).
- Respuestas de diseño en `functional-design-questions.md`.

## Assumptions & Open Questions

None.
