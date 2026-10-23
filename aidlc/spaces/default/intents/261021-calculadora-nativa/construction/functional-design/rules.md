# Business Rules — Calculadora nativa iOS

Fuente de verdad: el bloque `yaml`. Los `BRx.y` son claves de trazabilidad
permanentes. Prosa resumida al final.

```yaml
rules:
  # Grupo 1 — Proyección de valor (FR4, FR7)
  - id: BR1.1
    statement: "El valor proyectado de un jugador es value + change*daysAhead."
    category: calculation
    applies_to: RosterPlayer
    trigger: "Al calcular Seleccionadas, al ordenar por valor proyectado, y al mostrar la card."
    logic: "projected = value + (change ?? 0) * daysAhead"
    violation: "N/A (cálculo); un change nil cuenta como 0."
    source: FR4.3, FR7
  - id: BR1.2
    statement: "daysAhead es el número de días (>=0) entre hoy (00:00) y la fecha elegida; sin fecha, 0."
    category: calculation
    applies_to: CalculatorState
    trigger: "Al cambiar la fecha en el DatePicker."
    logic: "daysAhead = max(0, wholeDays(today00:00, chosenDate00:00)); nil fecha -> 0"
    violation: "Una fecha anterior a hoy se acota a 0 (el picker ya la impide)."
    source: FR4.1, FR4.2

  # Grupo 2 — Totales (FR7)
  - id: BR2.1
    statement: "selectedTotal = suma de (value + change*daysAhead) sobre los jugadores seleccionados."
    category: calculation
    applies_to: CalculatorState
    trigger: "Al cambiar selección o daysAhead."
    logic: "selectedTotal = Σ projectedValue(p, daysAhead) para p en selectedIds"
    violation: "N/A"
    source: FR6.3, FR7.1
  - id: BR2.2
    statement: "onSaleTotal = suma de value sobre los jugadores en venta."
    category: calculation
    applies_to: OnSalePlayer
    trigger: "Al cargar / tras poner o cancelar venta."
    logic: "onSaleTotal = Σ value para p en onSalePlayers"
    violation: "N/A"
    source: FR7.2

  # Grupo 3 — Saldo futuro (FR7, invariantes de dinero)
  - id: BR3.1
    statement: "Saldo futuro = balance + selectedTotal + (includeOnSale ? onSaleTotal : 0) − activeBidsTotal."
    category: calculation
    applies_to: CalculatorState
    trigger: "Al cambiar cualquier entrada (selección, toggle, fecha, datos cargados)."
    logic: "futureBalance = balance + selectedTotal + (includeOnSale ? onSaleTotal : 0) - activeBidsTotal"
    violation: "N/A"
    source: FR7.3
  - id: BR3.2
    statement: "activeBidsTotal SIEMPRE se resta del saldo futuro, con el toggle ON u OFF."
    category: constraint
    applies_to: CalculatorState
    trigger: "En todo cálculo de saldo futuro."
    logic: "El término -activeBidsTotal no depende de includeOnSale."
    violation: "Si no se restara, el saldo futuro quedaría inflado."
    source: FR7.4

  # Grupo 4 — Anti-doble-conteo (FR7.5)
  - id: BR4.1
    statement: "Ningún jugador en venta aporta a la vez por onSaleTotal y por selectedTotal."
    category: constraint
    applies_to: CalculatorState
    trigger: "En cada recomposición de la lista seleccionable."
    logic: >
      Con includeOnSale=ON los jugadores en venta se EXCLUYEN de la lista
      seleccionable (cuentan vía onSaleTotal). Con OFF se INCLUYEN y pueden
      seleccionarse (cuentan vía selectedTotal), y onSaleTotal no se suma.
    violation: "Doble conteo: el valor del jugador se contaría dos veces."
    source: FR5.2, FR7.5
  - id: BR4.2
    statement: "Al pasar el toggle de OFF a ON, se descartan de selectedIds los ids de jugadores en venta."
    category: policy
    applies_to: CalculatorState
    trigger: "setIncludeOnSale(true)."
    logic: "selectedIds := selectedIds \\ onSaleIds; luego recomponer lista."
    violation: "Quedaría una selección fantasma que violaría BR4.1."
    source: FR7.5

  # Grupo 5 — Preferencia 'incorporar en venta' (FR3)
  - id: BR5.1
    statement: "includeOnSale por defecto es ON; cualquier valor persistido distinto del literal 'false' resuelve a ON."
    category: policy
    applies_to: CalculatorPreferences
    trigger: "Al arrancar la pantalla."
    logic: "includeOnSale = (stored == 'false') ? false : true"
    violation: "N/A (default seguro)."
    source: FR3.1
  - id: BR5.2
    statement: "La lista seleccionable se recompone en memoria al cambiar el toggle, sin recargar del backend. Con el toggle OFF, las selecciones de jugadores en venta persisten entre recargas y SOLO se purgan en la transición OFF->ON (BR4.2), nunca por una recarga de datos."
    category: policy
    applies_to: CalculatorState
    trigger: "setIncludeOnSale; recargas de datos."
    logic: "selectable = ON ? roster.filter(!onSale) : roster; una recarga NO purga selectedIds (solo el paso OFF->ON lo hace)."
    violation: "Una recarga innecesaria del backend, o purgar selección en una recarga bajo OFF."
    source: FR5.2

  # Grupo 6 — Presentación de la cabecera (R-01)
  - id: BR6.1
    statement: "El ítem 'En venta' de la cabecera de resumen se muestra SIEMPRE; lo que se oculta con el toggle OFF es la sección de cards de jugadores en venta."
    category: policy
    applies_to: CalculatorState
    trigger: "Al renderizar cabecera y sección en venta."
    logic: "header.onSale visible = true siempre; section.onSaleCards visible = includeOnSale && onSalePlayers.nonEmpty"
    violation: "Ocultar el dato de cabecera confundiría al usuario (R-01)."
    source: FR2.2, FR3.3
  - id: BR6.2
    statement: "'Pujas activas (N)' solo se muestra cuando activeBidsCount > 0."
    category: policy
    applies_to: EconomySnapshot
    trigger: "Al renderizar la cabecera."
    logic: "visible = activeBidsCount > 0"
    violation: "N/A"
    source: FR2.3

  # Grupo 7 — Plusvalía (R-03)
  - id: BR7.1
    statement: "La plusvalía mostrada y ordenable es el campo profit del roster; es solo-presentación y NO entra en las invariantes de dinero (FR7)."
    category: policy
    applies_to: RosterPlayer
    trigger: "Al mostrar la card y al ordenar por plusvalía."
    logic: "plusvalia = profit; signo + presentación verde/rojo; nunca suma a futureBalance."
    violation: "Incluir profit en futureBalance sería un error de cálculo."
    source: FR5.1, FR5.3

  # Grupo 8 — Poner a la venta (FR8)
  - id: BR8.1
    statement: "Poner a la venta requiere >=1 jugador seleccionado y confirmación explícita antes de llamar al backend."
    category: validation
    applies_to: CalculatorState
    trigger: "Pulsar 'Vender (N)'."
    logic: "if selectedIds.isEmpty -> no-op; else mostrar confirmación; solo tras confirmar -> sell."
    violation: "Una venta sin confirmación."
    source: FR8.1, FR8.2
  - id: BR8.2
    statement: "La venta devuelve un SellOutcome dedicado (total/partial/none/networkError). Solo se retiran los jugadores y se recarga 'en venta' en total (sold == total); en partial/none solo se informa y la lista/selección se mantienen."
    category: policy
    applies_to: CalculatorState
    trigger: "Respuesta de sell (SellOutcome)."
    logic: >
      total(sold) -> quitar vendidos de roster+selectable, limpiar selectedIds,
      recargar onSale, invalidar cachés; partial(sold,total) -> mostrar
      'sold/total', NO retirar, NO recargar; none(total) -> informar fallo;
      networkError(message) -> mensaje legible. (sell NO usa MarketWriteOutcome
      porque necesita transportar sold/total — R-01.)
    violation: "Retirar en parcial dejaría el estado incoherente (R-02 de requisitos)."
    source: FR8.3, FR8.4

  # Grupo 9 — Cancelar venta (FR9)
  - id: BR9.1
    statement: "Cancelar venta requiere confirmación; tras cancelar se recargan los datos."
    category: validation
    applies_to: OnSalePlayer
    trigger: "Pulsar cancelar en una card en venta."
    logic: "mostrar confirmación; tras confirmar -> cancelSale -> recargar datos."
    violation: "Cancelación sin confirmación."
    source: FR9.1, FR9.2

  # Grupo 10 — Coherencia cruzada (FR10)
  - id: BR10.1
    statement: "Una venta o cancelación aceptada invalida la caché de Presupuesto y Mercado."
    category: policy
    applies_to: CalculatorState
    trigger: "Resultado aceptado de sell/cancelSale."
    logic: "onWriteAccepted -> budget.invalidate(); market.invalidate()"
    violation: "Otras pantallas mostrarían cifras obsoletas."
    source: FR10.1

  # Grupo 11 — Carga y frescura (FR1)
  - id: BR11.1
    statement: "Al aparecer se carga solo si hace falta (loadIfNeeded); el cambio de campeonato, el TTL o el pull-to-refresh fuerzan recarga dura. Las tres llamadas se cargan en paralelo."
    category: policy
    applies_to: CalculatorState
    trigger: ".task / cambio de campeonato / refresh."
    logic: "reutilizar DataFreshness (TTL 180s, por campeonato); roster+market+onSale en paralelo."
    violation: "Refetch en cada cambio de pestaña."
    source: FR1.1, FR1.3, FR1.4
```

## Resumen de reglas

| Grupo | Tema | Reglas |
|---|---|---|
| BR1 | Proyección de valor | BR1.1, BR1.2 |
| BR2 | Totales | BR2.1, BR2.2 |
| BR3 | Saldo futuro (invariante) | BR3.1, BR3.2 |
| BR4 | Anti-doble-conteo | BR4.1, BR4.2 |
| BR5 | Preferencia 'incorporar en venta' | BR5.1, BR5.2 |
| BR6 | Cabecera de resumen (R-01) | BR6.1, BR6.2 |
| BR7 | Plusvalía (R-03) | BR7.1 |
| BR8 | Poner a la venta (R-02) | BR8.1, BR8.2 |
| BR9 | Cancelar venta | BR9.1 |
| BR10 | Coherencia cruzada | BR10.1 |
| BR11 | Carga y frescura | BR11.1 |
