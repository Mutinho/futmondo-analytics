# Code Summary — Favoritos nativa iOS

## Resultado

- `swift build --package-path ios` → Build complete (exit 0).
- `swift test --package-path ios` → **232 tests, 0 fallos** (204 previos + 28
  nuevos). Sin dependencias de pago. Backend intacto.

## Ficheros creados — `FutmondoKit/Favorites` (lógica pura, XCTest)

- `FavoritePlayer.swift` — DTO (snake_case→camelCase) + `FavoritesResponse`
  tolerante (array raíz / `players` / `favorites`). Dos ratings: `rating`
  (decodeIfPresent, no se muestra) y `sofascoreRating` (badge/orden);
  `homeAverage`/`awayAverage`/`matches`. `encode(to:)` explícito (escribe solo
  la clave canónica `players`) para evitar el warning del encoder sintetizado
  por la clave alias.
- `FavoritesService.swift` — protocolo + `HTTPFavoritesService` (actor sobre
  `NetworkClient`): `fetchFavorites` = `GET /api/v1/favorites/my?championship_id=<id>`;
  `unfollow` = `POST /api/v1/favorites/unfollow?championship_id=<id>&player_id=<id>`
  con **body vacío y ambos ids como query params** → `MarketWriteOutcome`
  (distinto de `RosterService.cancelSale`, que usa body JSON — BR8.1).
- `FavoritesSorter.swift` — `FavoritesSortField`
  (value/change/sofascoreRating/starterPct/points) + orden descendente
  nulls-last estable.
- `FavoritesPreferences.swift` — persiste `sortField` vía `KeyValueStore`.

## Ficheros creados — `FutmondoApp/Favorites` (SwiftUI, device-validated)

- `FavoritesViewModel.swift` (@MainActor @Observable): `loadIfNeeded` +
  `DataFreshness`; `unfollow` con guardia `isWriting`, **eliminación local
  optimista** en aceptado (BR5.2; sin reload), lista intacta + re-habilitar en
  fallo (BR5.3/BR5.4).
- `FavoritesView.swift`: toolbar (ChampionshipMenu + `Menu` de orden +
  settings), countLabel, estados vacío/carga/error, `LazyVGrid`,
  `onChange(budgetViewModel.activeChampionship?.championshipId)` → recarga
  (BR1.2), `.refreshable`, único `.sheet(item:)` (ConfirmSheet +
  SofascoreDetailSheet).
- `FavoritePlayerCard.swift`: estética tiles de Mercado; nulos/cero "-"
  (BR3.1); media con casa/fuera/partidos (BR3.2); badge por `sofascoreRating`
  (BR3.3); menú "…" (Ver estadísticas / Ver perfil si hay URL); botón QUITAR →
  ConfirmSheet.

## Ficheros modificados

- `RootTabView.swift` — 4.ª pestaña "Favoritos" (SF Symbol `star`, tinte verde),
  ramas iOS 18+ y fallback.
- `SplashView.swift` — compone `FavoritesViewModel` sobre el `NetworkClient` +
  `ActiveChampionshipStore` + `FavoritesPreferences` compartidos. Sin
  cross-invalidación (FR7.1).

## Tests añadidos (28) — `Tests/FutmondoKitTests`

- `FavoritePlayerTests` (8): decode, nulos, dos ratings, formas tolerantes.
- `FavoritesSorterTests` (8): cada campo descendente, nulls-last, estable.
- `FavoritesPreferencesTests` (4): round-trip del orden, default.
- `FavoritesServiceTests` (7): endpoints exactos; **regresión BR8.1** (unfollow
  usa query params + body vacío, no body JSON).

## Desviaciones del plan

Ninguna en sustancia. Nota: `encode(to:)` explícito en `FavoritesResponse` para
evitar warning por la clave alias de decode. Vistas SwiftUI validadas en
dispositivo (llvm-cov no fiable en WSL).

## Revisión 1 tras prueba en dispositivo (Step 10)

- **Quitar de favoritos sin recargar**: tras un `unfollow` aceptado, el
  `FavoritesViewModel` ya NO llama a `reload()`; elimina el jugador de `players`
  en memoria (`removeAll { $0.playerId == ... }`) y, si queda vacío, pasa a
  estado vacío (BR5.2 actualizada). La vista dispara el unfollow y el grid lleva
  `.animation(.spring, value: players.map(\.playerId))` + `.transition` por
  card, de modo que las tarjetas restantes **se recolocan con animación fluida**
  (no-op bajo Reduce Motion). Sin nueva petición al backend. Build verde, 232
  tests.

## Revisión 2 tras prueba en dispositivo (Step 11)

- **Sin alert de éxito**: al quitar de favoritos ya NO se emite
  `FavoritesNotice.success`; la desaparición animada de la card lo comunica. El
  aviso de ERROR (rejected/networkError) se mantiene. (Eliminada la constante
  `unfollowSuccess`.)
- **Skeletons nativos de carga**: el estado `.loading` ya no muestra spinner +
  "Cargando…"; muestra `SkeletonGrid` — una rejilla 2-up de `SkeletonCard` con
  la silueta real de la tile (hero + franjas de métricas + banda de CTA),
  renderizada con `.redacted(reason: .placeholder)` + un `ShimmerModifier`
  (barrido diagonal animado, no-op bajo Reduce Motion). Componentes nuevos en
  `ios/Sources/FutmondoApp/Shared/SkeletonCard.swift` (`ShimmerModifier` +
  `.shimmering()` + `SkeletonCard` + `SkeletonGrid`), **reutilizables** para
  aplicar el mismo patrón a las demás pantallas después. Build verde, 232 tests.

## Revisión 3 — rollout del skeleton a todas las pantallas (ampliación de alcance)

- Ampliación consentida por el propietario (fuera del scope original de
  Favoritos). Añadido `SkeletonHeader` + `SkeletonScreen` reutilizables a
  `Shared/SkeletonCard.swift` (`SkeletonScreen(showHeader:)` = header opcional +
  grid, en ScrollView no interactivo).
- Reemplazado el `LoadingState` (spinner + "Cargando…") por skeleton en:
  **Mercado** (`SkeletonScreen(showHeader: true)` — tiene banner económico),
  **Presupuesto** (`showHeader: true` — resumen), **Calculadora**
  (`showHeader: true` — cabecera económica) y **Favoritos**
  (`showHeader: false` — sin cabecera).
- Solo estado `.loading`/`.idle`; sin cambios de lógica ni contratos. Toca
  ficheros de intents ya cerrados (Mercado/Calculadora/Presupuesto) como cambio
  de UI consentido. `LoadingState` sigue usándose en sheets/detalle (no queda
  huérfano). Build verde, 232 tests.

## Revisión 4 — skeleton WOW (aurora + crossfade) + SkeletonRow (Presupuesto)

- `Shared/SkeletonCard.swift` reescrito: el relleno de las piezas pasa de gris a
  un **`AuroraFill`** — gradiente de marca (verde `DSColor.primary` → violeta
  `DSColor.tertiary`) que **se desplaza** en bucle (`easeInOut.repeatForever`),
  con blend `plusLighter`; Reduce Motion → estático. Entrada **escalonada**
  (`StaggeredAppear`, delay por índice). `.transition(.opacity)` en cada rama de
  carga + animación de estado en el body → **crossfade** suave skeleton→contenido.
- **`SkeletonRow` + `SkeletonListScreen`** nuevos, fieles a `BudgetRow` (nombre +
  divider + SALDO/RENDIMIENTO + PUJA MÁXIMA/PREMIOS): **Presupuesto** usa
  `SkeletonListScreen` (filas a ancho completo), no el grid de tiles.
  Mercado/Calculadora/Favoritos siguen con `SkeletonScreen` (grid de tiles) ya
  con la aurora. Se añadió `reduceMotion` + animación de estado a `BudgetView`
  para su crossfade. Build verde, 232 tests.

## Revisión 5 — crossfade completo (contenido entra con fundido)

- El skeleton se desvanecía pero el contenido real entraba de golpe (solo la
  rama de carga tenía `.transition`). Añadido `.transition(.opacity)` a la rama
  de **contenido** (`.data`/`.loaded`) de las 4 vistas (Mercado, Presupuesto,
  Calculadora, Favoritos): ahora el contenido real **entra con fundido**
  mientras el skeleton se desvanece — crossfade completo. La animación de estado
  del body (nil bajo Reduce Motion) coordina ambas transiciones. Build verde,
  232 tests.

## Revisión 6 — crossfade REAL (ZStack opacidad cruzada)

- El `.transition(.opacity)` por rama de `switch` NO cruzaba (SwiftUI lo trata
  como reemplazo) → las cards seguían apareciendo de golpe. Rehecho con un
  componente reutilizable **`CrossfadeLoader`** (`Shared/CrossfadeLoader.swift`):
  un `ZStack` que mantiene **ambas capas montadas** (skeleton + contenido) y
  cruza su `opacity` desde un flag `isLoading` (`skeleton.opacity(isLoading?1:0)`
  / `content.opacity(isLoading?0:1)`), con `allowsHitTesting` en la capa
  oculta y `.animation(.easeInOut(0.45), value: isLoading)` (nil bajo Reduce
  Motion). Fundido real skeleton↔contenido.
- Las 4 vistas (Mercado, Presupuesto, Calculadora, Favoritos) envuelven su
  `content` en `CrossfadeLoader(isLoading: isLoadingState) { skeleton } content:
  { content }`; su rama de carga pasa a `Color.clear` (el loader pone el
  skeleton encima) y se quitaron los `.transition(.opacity)` por rama y la
  `.animation(value:)` del body (la dueña de la animación es el loader).
  Eliminada la `reduceMotion` ya no usada en `BudgetView`. Build verde, 232
  tests.
