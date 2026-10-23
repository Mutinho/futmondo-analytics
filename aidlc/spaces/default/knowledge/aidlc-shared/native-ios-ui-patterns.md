# Patrones de UI nativa iOS (SwiftUI) — reutilizables para futuras pantallas

> Conocimiento de equipo (`aidlc-shared`): lo leen todos los agentes en cada
> intent del espacio. Recoge decisiones y patrones **ya validados en dispositivo**
> durante el intent F3 (Mercado nativo) y el pulido de UX posterior, para no
> re-derivarlos pantalla a pantalla. Guía reutilizable; NO sustituye a las reglas
> de `memory/` (que sólo se escriben por el ritual de learnings). Prosa en
> castellano; tokens técnicos verbatim en inglés.

## Fuente de verdad del diseño

- La **fuente de verdad del comportamiento** de cada pantalla nativa es su vista
  Angular equivalente en `angular-app/src/app/features/<feature>/`. Antes de
  diseñar, LEER el `.ts` + `.html` + `.scss` de esa vista: layout, campos,
  colores por tramo, y **la lógica condicional exacta** (ver el bug de
  `current_bid` abajo).
- El **tema** (colores/tipografía/superficies) se reproduce con el `DesignSystem`
  de `FutmondoApp`/`FutmondoKit` (SDK de Apple, coste 0 €). Donde Material 3 no
  tenga equivalente 1:1, Apple HIG.

## Bugs/trampas de port Angular → Swift (ya pagadas)

- **Falsy de JavaScript**: en Angular `@if (x)` con `x = 0` NO muestra nada
  (0 es falsy). Al portar, un `Int?` del backend que llega como `0` (no `null`)
  no debe tratarse como "hay valor". Caso real: `current_bid: 0` = **sin puja**;
  `hasActiveBid` exige `currentBid > 0` **y** `currentBidId` no vacío. Revisar
  este patrón en cualquier campo numérico "0 = ausente".
- **Respuesta envuelta vs. raíz**: algunos endpoints devuelven
  `{ "success": true, "player": { … } }` (stats anidadas bajo una clave), no el
  objeto en la raíz. El `NetworkClient` decodifica el tipo que le pidas, así que
  hay que decodificar un **DTO envoltorio** y desenvolver (ver
  `SofascoreDetailResponse`). Si el detalle "falla al cargar", sospechar del
  shape de la respuesta primero.
- **Imágenes externas**: avatares de jugador y escudos de equipo vienen de bases
  fijas (`MarketImageURL`): `faces/64/{slug}.png` y `teams/64/{team_logo}`. Usar
  `AsyncImage` con fallback (silueta / color) cuando el slug/logo falte o falle.

## Componentes nativos y patrones de interacción

- **Selector de opción única en toolbar (campeonato, orden, Compra/Venta)**: un
  `Menu` nativo cuyo `label` es un `DSGlassIcon`. Para que **los textos queden
  alineados**, cada fila es un **`Toggle`** (no `Label(checkmark)` en el activo +
  `Text` en el resto: eso desalinea, porque el no-seleccionado no reserva el
  hueco del check). El `Toggle` reserva el gutter en todas las filas. Es el
  componente transversal: arreglarlo una vez lo arregla en todas las pantallas.
- **NUNCA usar `.sheet(item:)` dos veces sobre la misma vista**: SwiftUI sólo
  honra el último y el otro no presenta (síntoma: "el detalle no abre"). Usar
  **un único `.sheet(item:)` enrutado por un enum** `Identifiable`
  (ver `MarketSheetRoute`).
- **Hoja de detalle a pantalla completa**: `NavigationStack` dentro de la sheet,
  `.presentationDetents([.large])`, `.navigationBarTitleDisplayMode(.inline)`,
  "Cerrar" en `.toolbar`. Evita la sheet que sale "a medias" y hay que arrastrar.
- **Enlace externo** (p. ej. abrir sofascore.com): `Link` nativo o
  `@Environment(\.openURL)`; colocarlo en el menú `...` de la tarjeta o dentro de
  la hoja de detalle, no duplicado en ambos.
- **CTA + overflow**: el botón de acción principal (p. ej. "PUJAR") homogéneo
  (verde primario sólido, sin degradado por-elemento) y, a su lado, un botón
  **redondo `...`** (glass) con un `Menu` para acciones secundarias.
- **Fondo transversal**: `.authenticatedBackground()` en TODAS las pantallas
  autenticadas (no sólo una). Nunca en Splash/Login.
- **Tab bar**: tinte de selección = `DSColor.primary` (verde) vía `.tint(...)`
  en el `TabView`; accesible porque la selección también va por icono relleno +
  etiqueta, no sólo color.

## "WOW" nativo (animaciones y pieza de datos)

- **Swift Charts** (`Charts.framework`, SDK de Apple, coste 0 €) para
  mini-gráficas (barra de capacidad, etc.). `Gauge` nativo para medidores
  (`.accessoryLinearCapacity`/`.accessoryCircular`).
- **Entrada escalonada de listas**: `.scrollTransition` (iOS 17+) con fade +
  escala + offset por celda; no-op bajo Reduce Motion.
- **Haptics**: `UISelectionFeedbackGenerator` / `UIImpactFeedbackGenerator` /
  `UINotificationFeedbackGenerator(.success)` en ajustes de slider, snap y
  confirmaciones (bajo `#if canImport(UIKit)`).

## Skeletons de carga (preferir al spinner "Cargando…")

- **Efecto moderno de marca, coste 0**: en vez de spinner + texto, mostrar
  placeholders con la forma real del contenido, rellenos con un **gradiente de
  marca en movimiento** (`AuroraFill`: verde `DSColor.primary` → violeta
  `DSColor.tertiary`, drift en bucle con `blendMode(.plusLighter)`), + **entrada
  escalonada** (`StaggeredAppear`, delay por índice). Componentes reutilizables
  en `FutmondoApp/Shared/SkeletonCard.swift`:
  `SkeletonCard` (tile), `SkeletonHeader` (banner/resumen), `SkeletonRow` (fila),
  `SkeletonScreen` (header opcional + grid 2-up) y `SkeletonListScreen`
  (header + filas). Todo gated por Reduce Motion (estático si está activo).
- **Elegir skeleton según el layout real**: pantallas de **tiles** (Mercado,
  Calculadora, Favoritos) → `SkeletonScreen` (grid); pantallas de **filas**
  (Presupuesto) → `SkeletonListScreen` con `SkeletonRow` fiel a la fila
  (`BudgetRow`), NO el grid de tiles. `showHeader: true` cuando hay card de
  resumen/banner arriba; `false` si no (Favoritos).
- **Crossfade skeleton→contenido (trampa importante)**: `.transition(.opacity)`
  en las ramas de un `switch` de estado **NO cruza** — SwiftUI reemplaza el
  subárbol y el contenido entra de golpe. El patrón fiable es `CrossfadeLoader`
  (`FutmondoApp/Shared/`): un `ZStack` con AMBAS capas montadas (skeleton +
  contenido) y opacidad cruzada por un flag `isLoading`
  (`content.opacity(isLoading ? 0 : 1)` / `skeleton.opacity(isLoading ? 1 : 0)`,
  `allowsHitTesting` en la capa oculta), animado con `.animation(value:
  isLoading)` y gated por Reduce Motion. La rama de carga del `switch` pasa a
  `Color.clear` (el loader pone el skeleton encima).

## "WOW" nativo (animaciones y pieza de datos)

- **Swift Charts** (`Charts.framework`, SDK de Apple, coste 0 €) para
  mini-gráficas (barra de capacidad, etc.). `Gauge` nativo para medidores
  (`.accessoryLinearCapacity`/`.accessoryCircular`).
- **Entrada escalonada de listas**: `.scrollTransition` (iOS 17+) con fade +
  escala + offset por celda; no-op bajo Reduce Motion.
- **Resumen flotante al hacer scroll**: NO intentar un "morph" entre dos vistas
  con `matchedGeometryEffect` entre `ScrollView` y `overlay` (frágil; se queda
  detrás). Patrón que funciona: la tarjeta grande vive DENTRO del `ScrollView`
  (se va con el scroll) y una **píldora compacta flota en `.overlay(top)`**,
  apareciendo con transición (fade + move) cuando el scroll pasa un umbral.
- **Scroll offset**: medirlo con **`onScrollGeometryChange(for:)`** (iOS 18+;
  fiable), no con `GeometryReader` + `PreferenceKey` (no dispara bien). Guardar
  sólo un **`Bool`** (cruce de umbral), NO el offset continuo: escribir estado en
  cada frame re-evalúa toda la lista y hace el scroll "pesado".
- **Respetar siempre `@Environment(\.accessibilityReduceMotion)`**: desactivar
  animaciones (sólo fade/none) cuando esté activo.

## Rendimiento / 120 Hz (ProMotion)

- Una app SwiftUI se capa a **60 Hz** aunque el panel sea ProMotion 120 Hz,
  salvo que el `Info.plist` lleve **`CADisableMinimumFrameDurationOnPhone = true`**.
  Con `xtool`, añadirlo vía `infoPlist:` en `xtool.yml` (si se edita el plist
  generado se pierde en el siguiente build).
- Scroll fluido: evitar escrituras de `@State` por frame; cuidar coste por celda
  (`.ultraThinMaterial`, sombras/glow, `AsyncImage` sin caché, `scrollTransition`).

## Caché en memoria para evitar refetch al cambiar de pestaña

- En `TabView`, la pestaña que entra se **reconstruye**, así que `.task { load() }`
  **refetcha en cada cambio**. Solución: `loadIfNeeded()` gobernado por una
  política de frescura pura y testeable (`DataFreshness`: TTL + campeonato
  cargado + `invalidate()`), `.task` → `loadIfNeeded`, y **pull-to-refresh**
  (`.refreshable`) para el refresco manual.
- **Coherencia cruzada tras escritura**: si una pantalla (Mercado) cambia cifras
  que otra (Presupuesto) muestra, tras un write aceptado **invalidar** la caché
  de la otra (callback `onWriteAccepted` → `invalidate()`); comparten el
  `ActiveChampionshipStore`.

## Toolchain (WSL/Linux) — ya afirmado en memoria

- `swift test`/`swift build` en WSL **no** aplican Swift 6 strict concurrency
  tan estricto como el build de dispositivo (`xtool`): un `static var` de
  `PreferenceKey` compila en WSL pero **falla en dispositivo** ("not
  concurrency-safe"); usar `static let`. Validar en dispositivo lo que toque UI.
- `actool` no disponible (Color Sets en código, `DSColorToken`); `llvm-cov` no
  fiable (lógica testeable en `FutmondoKit` con XCTest; vistas SwiftUI validadas
  en dispositivo).

## Sources

- `ios/Sources/FutmondoApp/Market/*` (MarketView, MarketPlayerCard, MarketBanner,
  BidSheet, SofascoreDetailSheet), `ios/Sources/FutmondoApp/Budget/*`
  (ChampionshipMenu, SortMenu, TeamDetailView, RootTabView),
  `ios/Sources/FutmondoKit/Market/*` (MarketImageURL, DataFreshness,
  SofascoreDetail), `ios/xtool.yml`.
- Fuente de verdad: `angular-app/src/app/features/market/`,
  `angular-app/src/app/shared/utils/player.utils.ts`.
