# Requirements — Calculadora nativa iOS

Intent: `261021-calculadora-nativa` · Scope: `refactor` (plan a medida
`native-screen-frontend`) · Fase: INCEPTION.

## Intent analysis

El objetivo es llevar a la app nativa iOS (SwiftUI) la pantalla **Calculadora**
que ya existe en la PWA Angular, de modo que el usuario pueda, desde el iPhone:
(1) ver de un vistazo su situación económica proyectada (saldo actual, dinero en
venta, pujas comprometidas, valor de lo seleccionado y **saldo futuro**),
(2) **simular ventas** seleccionando jugadores de su plantilla y proyectar su
valor a una fecha futura por tendencia, y (3) **ejecutar** esas ventas (poner a
la venta / cancelar venta) contra el backend existente. El valor para el usuario
es decidir ventas con la misma información y las mismas cuentas que la web, en
una experiencia nativa coherente con las pantallas de Mercado y Presupuesto ya
entregadas. No cambia el backend: es una pantalla **frontend-only** sobre la capa
iOS existente.

Fuente de verdad del comportamiento y las fórmulas: la vista Angular
`angular-app/src/app/features/calculator/` (`calculator.component.ts/html/scss`).

## Functional requirements

### FR1 — Carga de datos
- FR1.1 Al abrir la pantalla con un campeonato activo, cargar en paralelo:
  la plantilla del usuario (`getMyRoster`), el mercado de hoy
  (`GET /api/v1/market/today`, del que se leen `balance`, `active_bids_total`,
  `active_bids_count`) y los jugadores en venta (`getOnSale`).
- FR1.2 Mostrar estado de carga mientras se resuelven las llamadas y un estado de
  error legible en castellano si alguna falla (mensaje del backend si lo hay).
- FR1.3 Reaccionar al **cambio de campeonato activo** recargando los datos
  (mismo `ActiveChampionshipStore` que Mercado/Presupuesto).
- FR1.4 Reutilizar la caché en memoria `DataFreshness` ya existente
  (`loadIfNeeded()` al aparecer; recarga dura al cambiar de campeonato, pasar el
  TTL o con pull-to-refresh), para no refetchar al cambiar de pestaña.

### FR2 — Cabecera de resumen económico
- FR2.1 Mostrar **Saldo actual** (`balance`), con estilo positivo/negativo.
- FR2.2 Mostrar **En venta** = suma del valor de los jugadores actualmente en
  venta (`onSaleTotal`).
- FR2.3 Mostrar **Pujas activas (N)** con su importe restado (`active_bids_total`,
  `active_bids_count`), SOLO cuando `active_bids_count > 0`.
- FR2.4 Mostrar **Seleccionadas** = valor proyectado de los jugadores
  seleccionados (ver FR6).
- FR2.5 Mostrar **Saldo futuro** según la fórmula invariante de FR7, con estilo
  positivo/negativo.

### FR3 — Toggle "Incorporar jugadores en venta"
- FR3.1 Ofrecer un toggle nativo "Incorporar jugadores en venta", persistido en
  `UserDefaults`; por defecto **ON** (cualquier valor no explícitamente `false`
  resuelve a ON, como en la web).
- FR3.2 Con el toggle **ON**: los jugadores en venta se **excluyen** de la lista
  seleccionable (su valor cuenta ya vía "En venta", FR2.2), y se muestra el
  bloque "En venta".
- FR3.3 Con el toggle **OFF**: los jugadores en venta se **incluyen** en la lista
  seleccionable (el usuario puede seleccionarlos manualmente para simular su
  venta desde cero), y el bloque "En venta" se oculta.

### FR4 — Proyección por fecha
- FR4.1 Ofrecer un `DatePicker` nativo "Fecha de venta" acotado a hoy o después.
- FR4.2 Calcular `daysAhead` = días entre hoy (00:00) y la fecha elegida
  (mínimo 0); sin fecha, `daysAhead = 0`.
- FR4.3 Valor proyectado de un jugador = `value + change * daysAhead` (FR7).
- FR4.4 Indicar "Hoy (valor actual)" cuando `daysAhead = 0`, o "N día/días a
  futuro" en caso contrario.

### FR5 — Listado de jugadores seleccionables (solo cards)
- FR5.1 Presentar la lista seleccionable **solo en formato cards** nativas,
  reutilizando la **misma estética y los tiles de la pantalla de Mercado de iOS**
  (hero, glass/neon, tipografía, chips de posición), con el contenido adaptado:
  VALOR ACTUAL, TENDENCIA, VALOR PROYECTADO, PLUSVALÍA, y badges Sofascore /
  titularidad cuando existan.
- FR5.2 La composición de la lista seleccionable depende del toggle (FR3.2/FR3.3)
  y se **reconstruye sin recargar** del backend al cambiar el toggle.
- FR5.3 Ofrecer **orden** por valor proyectado, valor actual, tendencia o
  plusvalía mediante un `Menu` nativo (patrón ya usado en Mercado), persistido en
  `UserDefaults`.
- FR5.4 Mostrar el recuento "N jugadores disponibles".

### FR6 — Selección múltiple y total seleccionado
- FR6.1 Un **tap sobre la card** alterna su selección, con indicador de check
  visible en la card seleccionada.
- FR6.2 Permitir seleccionar/deseleccionar todos.
- FR6.3 **Seleccionadas** (FR2.4) = suma de `value + change * daysAhead` de los
  jugadores seleccionados.

### FR7 — Invariantes de dinero (criterios de aceptación)
- FR7.1 `selectedTotal = Σ (value + change * daysAhead)` sobre los seleccionados.
- FR7.2 `onSaleTotal = Σ value` sobre los jugadores en venta.
- FR7.3 **Saldo futuro** `futureBalance = balance + selectedTotal +
  (includeOnSale ? onSaleTotal : 0) − activeBidsTotal`.
- FR7.4 `activeBidsTotal` se **resta siempre** (invariante, con toggle ON u OFF).
- FR7.5 **Anti-doble-conteo**: un jugador en venta nunca aporta a la vez por
  `onSaleTotal` y por `selectedTotal`. Al pasar el toggle de OFF a ON se
  **descarta** cualquier selección manual de jugadores en venta que existiera
  bajo OFF, de modo que su valor cuente únicamente vía `onSaleTotal`.
- FR7.6 Estas fórmulas se implementan en lógica pura testeable en `FutmondoKit` y
  se cubren con XCTest (happy path + al menos dos casos de borde: toggle ON/OFF y
  proyección con `daysAhead > 0`).

### FR8 — Poner a la venta
- FR8.1 Cuando hay ≥1 seleccionado, mostrar un botón flotante **"Vender (N)"**.
- FR8.2 Al pulsarlo, pedir **confirmación** nativa ("¿Poner a la venta N
  jugador(es) a su valor de mercado actual?") antes de llamar a `sell`.
- FR8.3 Tras confirmar, invocar `sell(championshipId, ids)`; mostrar resultado
  (éxito total, parcial `sold/total`, o error) con mensaje en castellano.
- FR8.4 Tras una venta con éxito, retirar los jugadores vendidos de la lista y
  recargar los jugadores en venta, manteniendo coherente el estado seleccionable.

### FR9 — Cancelar venta
- FR9.1 En el bloque "En venta" (visible solo con toggle ON), cada jugador ofrece
  **cancelar venta** con confirmación ("¿Retirar a {nombre} del mercado?").
- FR9.2 Tras confirmar, invocar `cancelSale(championshipId, playerId)` y recargar
  los datos; mostrar error legible si falla.

### FR10 — Coherencia cruzada con otras pantallas
- FR10.1 Una venta/cancelación aceptada que cambie el saldo o las posiciones debe
  **invalidar la caché** de Presupuesto y Mercado (patrón `onWriteAccepted` →
  `invalidate()` ya existente), para que esas pantallas reflejen el cambio.

### FR11 — Navegación
- FR11.1 La Calculadora es una **nueva pestaña** (3.ª) del `RootTabView`, junto a
  Presupuesto y Mercado, con el tinte de selección verde neón y accesibilidad
  preservada (icono + etiqueta).

## Non-functional requirements

- NFR1 (Coste) Coste 0 €: solo SDK de Apple; sin dependencias de pago
  (`Package.swift` `dependencies: []`).
- NFR2 (Idioma) Identificadores, comentarios y docstrings en inglés; todo el
  texto de cara al usuario en castellano.
- NFR3 (Arquitectura/testabilidad) La lógica de cálculo vive en `FutmondoKit`
  cubierta con XCTest ejecutable (`swift test`); las vistas SwiftUI viven en
  `FutmondoApp` bajo `#if canImport(SwiftUI)` y se validan en dispositivo
  (llvm-cov no fiable en WSL).
- NFR4 (Look&feel) La pantalla reproduce la estética nativa ya establecida
  (Mercado como referencia de cards; design system existente), coherente con el
  tema Angular como fuente de verdad.
- NFR5 (Rendimiento) Scroll fluido a 120 Hz (ProMotion ya habilitado), evitando
  escrituras de estado por frame; cargas en paralelo y caché en memoria para no
  refetchar al cambiar de pestaña.
- NFR6 (Accesibilidad) Controles con etiquetas accesibles; selección y cifras
  comprensibles sin depender solo del color; respetar Reduce Motion en
  animaciones.
- NFR7 (Seguridad) No se manejan credenciales en esta pantalla; las preferencias
  en `UserDefaults` no son sensibles. Las llamadas reutilizan el `NetworkClient`
  autenticado existente.

## Constraints

- C1 Backend existente e **inmutable** en este intent: `getMyRoster`,
  `GET /api/v1/market/today`, `getOnSale`, `sell`, `cancelSale`. No se crea ni
  modifica API.
- C2 Build/verificación en WSL con `swift build`/`swift test`; validación de UI
  en dispositivo vía `ios/scripts/install-app.sh`.
- C3 Swift 6 strict concurrency se evalúa en el build de dispositivo (xtool), no
  en WSL: evitar estado `static var` no seguro (usar `static let`).

## Assumptions

- A1 Los campos del roster (`value`, `change`, `profit`, `points`, `average`,
  `sofascore_rating`, `starter_pct`, `position`, `team_logo`, `slug`) y los de
  `user_info` (`balance`, `active_bids_total`, `active_bids_count`) coinciden con
  los que ya consume la web; se confirmará contra los DTO existentes en
  `FutmondoKit` durante Functional Design. (Razón: reutilizamos el mismo backend.)
- A2 "En venta" (`getOnSale`) devuelve jugadores con al menos `player_id`,
  `name`, `slug`, `team`, `value`. (Razón: así los usa la vista Angular.)
- A3 Las bases de imágenes (caras/escudos) son las ya centralizadas en
  `MarketImageURL`. (Razón: reutilización del patrón de Mercado.)

## Out of scope

- O1 Cambios de backend o de contrato de API.
- O2 Modo tabla densa (se entrega solo cards; FR5.1).
- O3 Pipeline de CI, despliegue y operación (no los toca este intent).
- O4 Edición masiva avanzada más allá de poner/cancelar venta (p. ej. fijar
  precio manual distinto del valor de mercado).

## Open questions

- OQ1 Si `getOnSale`/`sell`/`cancelSale` aún no tienen cliente nativo en
  `FutmondoKit` (hoy existe el de pujas de Mercado), Functional Design decidirá
  si se añade un `RosterService` nativo reutilizando `NetworkClient`. No cambia
  el contrato de backend.
