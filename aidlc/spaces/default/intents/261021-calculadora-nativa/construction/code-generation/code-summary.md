# Code Summary — Calculadora nativa iOS

## Resultado

- `swift build --package-path ios` → Build complete (exit 0).
- `swift test --package-path ios` → **204 tests, 0 fallos** (168 existentes + 36
  nuevos). Filtro unit-scoped de la Calculadora → 36/36.
- Sin dependencias de pago (`Package.swift` `dependencies: []` intacto). Backend
  sin tocar.

## Ficheros creados — `FutmondoKit/Calculator` (lógica pura, cubierta con XCTest)

- `RosterPlayer.swift` — DTO `RosterPlayer` + `RosterResponse` tolerante
  (array raíz o envuelto en `players`).
- `OnSalePlayer.swift` — DTO `OnSalePlayer` + `OnSaleResponse`.
- `SellOutcome.swift` — `SellResponse {success,total,sold}` + enum `SellOutcome`
  (`total`/`partial`/`none`/`networkError`) con clasificador `.from(result:...)`.
- `RosterService.swift` — protocolo + `HTTPRosterService` (actor sobre
  `NetworkClient`): `fetchRoster` `/api/v1/roster/my`, `fetchOnSale`
  `/api/v1/roster/on-sale`, `sell` POST `/api/v1/roster/sell` → `SellOutcome`,
  `cancelSale` POST `/api/v1/roster/cancel-sale` → `MarketWriteOutcome`
  (endpoints exactos de la fuente Angular; backend intacto).
- `CalculatorMath.swift` — `projectedValue`, `selectedTotal`, `onSaleTotal`,
  `futureBalance` (`activeBidsTotal` SIEMPRE restado).
- `CalculatorSorter.swift` — `CalculatorSortField` + orden descendente,
  nulls-last, estable.
- `CalculatorPreferences.swift` — `KeyValueStore` + `UserDefaultsKeyValueStore`
  + `InMemoryKeyValueStore` (default toggle ON = cualquier valor != 'false').

## Ficheros creados — `FutmondoApp/Calculator` (SwiftUI, validadas en dispositivo)

- `CalculatorViewModel.swift` (@MainActor @Observable): carga paralela
  roster+economy+on-sale, recomposición por toggle + purga OFF→ON (BR4.2),
  proyección, sell/cancel con semántica "solo total retira" (BR8.2),
  `onWriteAccepted` cross-invalidación.
- `CalculatorView.swift`: cabecera + `DatePicker` nativo acotado a hoy, `Menu`
  de orden con filas `Toggle`, sección en venta, `LazyVGrid` 2-up,
  `confirmationDialog` de venta/cancelación, CTA flotante, `loadIfNeeded` +
  `.refreshable`.
- `CalculatorHeader.swift`: `NeonGlassCard` (Saldo futuro/actual, En venta
  SIEMPRE visible — R-01/BR6.1, Pujas activas solo si count>0 — BR6.2,
  Seleccionadas, toggle).
- `OnSaleSection.swift` (+ `OnSaleCard`, carrusel horizontal tras la revisión 2;
  la sección se oculta con toggle OFF, el dato de cabecera permanece).
- `CalculatorPlayerCard.swift`: reutiliza la estética de tiles de Mercado
  (hero, chip de posición, escudo); VALOR/TENDENCIA/PROYECTADO/PLUSVALÍA;
  tap-para-seleccionar; `profit` solo-presentación (R-03).
- `SellFloatingButton.swift`: CTA "Vender (N)".

## Ficheros modificados

- `FutmondoKit/Market/MarketTodayResponse.swift` — `activeBidsCount` añadido a
  `MarketUserInfo` como **opcional-con-default** (`decodeIfPresent ?? 0`, init
  por defecto y al final); decode de market/today y callers del memberwise init
  intactos (R-02).
- `FutmondoApp/Budget/RootTabView.swift` — 3.ª pestaña "Calculadora" (SF Symbol
  `calculator` tras la revisión 2, tinte verde neón, icono+etiqueta accesibles).
- `FutmondoApp/SplashView.swift` — compone `CalculatorViewModel` sobre el
  `NetworkClient` + `ActiveChampionshipStore` + `CalculatorPreferences`
  compartidos; `onWriteAccepted` invalida Presupuesto **y** Mercado
  (BR10.1/FR10.1).

## Tests añadidos (36) — `Tests/FutmondoKitTests`

- `CalculatorMathTests` (10): proyección (happy + nil-change + negativa/clamp),
  selectedTotal, onSaleTotal, futureBalance toggle ON/OFF, activeBidsTotal
  siempre restado, anti-doble-conteo, profit nunca en el cálculo.
- `CalculatorSorterTests` (7): cada campo descendente, projectedValue usa
  daysAhead, nulls-last, tie-break estable, vacío, default.
- `CalculatorPreferencesTests` (6): default ON, solo 'false' es OFF, round-trips,
  fallback de orden desconocido.
- `RosterPlayerTests` (13): decode de DTOs, formas de respuesta, clasificación
  de `SellOutcome`, endpoints exactos, no-fuga de credenciales, y la regresión
  R-02 (`active_bids_count` ausente→0 y presente→valor; compat del init).

## Decisiones clave

- `CalculatorPreferences` usa una abstracción `KeyValueStore` +
  `UserDefaultsKeyValueStore` en vez de conformar `UserDefaults` directamente,
  porque `UserDefaults` no es `Sendable` y su `set` toma `Any?` (la conformación
  directa no compila bajo Swift 6). Comportamiento idéntico al especificado.
- `RosterResponse`/`OnSaleResponse` toleran array raíz o envuelto en `players`
  (guía "wrapped vs root" de los patrones nativos).

## Desviaciones del plan

Ninguna en sustancia; solo las dos decisiones de implementación anteriores,
consistentes con el plan y los patrones. Sin `static var` de estado (Swift 6
device-strict); sin bajar ningún umbral; identificadores/comentarios en inglés y
texto de usuario en castellano.

## Revisión tras prueba en dispositivo (Step 12)

Ajustes de UX aplicados tras probar en el iPhone (solo vistas SwiftUI; build y
204 tests siguen verdes):

1. **Fecha de venta** pasó de card en el scroll a **botón de toolbar** (icono
   `calendar` / `calendar.badge.clock` si hay proyección activa) a la derecha
   del de ordenar; abre un `popover` con `DatePicker` gráfico + "Hoy (quitar
   proyección)".
2. **Píldora de resumen flotante al hacer scroll** (`CalcSummaryPill` +
   `CalcScrollOffsetReader` con `onScrollGeometryChange`): Saldo futuro ·
   Seleccionadas · Saldo actual, replicando el patrón de Mercado.
3. **Eliminado** el botón "Quitar selección" del `countLabel`.
4. **Botón "Vender (N)" más sutil**: píldora glass con borde neón alineada
   abajo-derecha (antes cápsula verde sólida grande centrada), para no competir
   con la tab bar.

## Revisión 2 tras prueba en dispositivo (Step 13)

1. **Icono de la pestaña Calculadora**: SF Symbol `function` → **`calculator`**
   en `RootTabView` (ramas iOS 18+ `Tab` y fallback `tabItem`).
2. **Bloque "En venta" → carrusel horizontal** (`OnSaleSection` reescrita):
   `ScrollView(.horizontal)` de tiles compactas `OnSaleCard` (foto hero
   circular, nombre, "PRECIO ACTUAL", y chip "Quitar" con icono + confirmación),
   en vez de filas a ancho completo. Estética coherente con las tiles de
   Mercado. Build verde, 204 tests.

## Revisión 3 tras prueba en dispositivo (Step 14)

1. **BUG corregido — cambio de campeonato no recargaba.** `CalculatorView` (y,
   por consistencia, `MarketView`) observaban `viewModel.activeChampionshipId`
   (getter de `UserDefaults`, no observable por SwiftUI), por lo que el
   `onChange` no disparaba. Ahora observan
   `budgetViewModel.activeChampionship?.championshipId` (propiedad `@Observable`
   que muta el selector) y fuerzan `load()`. (FR1.3)
2. **Icono de la pestaña**: `calculator` no se renderizaba en dispositivo →
   `plusminus.circle` (SF Symbol nativo fiable, matemático), en ambas ramas de
   `RootTabView`.
3. **Confirmaciones elegantes**: los dos `confirmationDialog` de vender/retirar
   se sustituyen por un **`ConfirmSheet`** nativo (sheet con detente, icono,
   título, mensaje y botones DS), enrutado por un único `.sheet(item:)` con el
   enum `CalculatorConfirmRoute` (evita el choque de dos `.sheet`). Mantiene
   semántica confirmar/cancelar y accesibilidad. Build verde, 204 tests.

## Revisión 4 tras prueba en dispositivo (Step 15)

- **Haptics de selección**: al seleccionar/deseleccionar una card en la
  Calculadora, el `onTap` dispara `UISelectionFeedbackGenerator().selectionChanged()`
  (helper `CalculatorView.fireSelectionHaptic`, bajo `#if canImport(UIKit)`,
  no-op fuera de dispositivo y con Reduce Motion activo). Import de `UIKit`
  condicional. Solo vista; build verde, 204 tests.
