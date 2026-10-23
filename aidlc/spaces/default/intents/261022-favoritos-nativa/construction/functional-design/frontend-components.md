# Frontend Components — Favoritos nativa iOS (SwiftUI)

Jerarquía SwiftUI y puntos de integración. Reutiliza el design system y la
estética de tiles de Mercado/Calculadora (NFR4).

## Capas

- **FutmondoKit (lógica pura, XCTest)**:
  - `FavoritePlayer` (Codable snake_case→camelCase; tolerante array/wrapped como
    `RosterResponse`).
  - `FavoritesService` (protocolo) + `HTTPFavoritesService` (actor sobre
    `NetworkClient`): `fetchFavorites(championshipId)` →
    `GET /api/v1/favorites/my?championship_id=<id>`; `unfollow(championshipId,
    playerId)` → `POST /api/v1/favorites/unfollow?championship_id=<id>&player_id=<id>`
    con **body vacío y ambos ids como query params** (confirmado contra
    `favorites.service.ts`; a diferencia de `RosterService.cancelSale`, que usa
    body JSON) → `MarketWriteOutcome`.
  - `FavoritesSorter` (patrón `CalculatorSorter`): value/change/sofascoreRating/
    starterPct/points, descendente, nils al final.
  - `FavoritesPreferences` (`KeyValueStore` + `UserDefaultsKeyValueStore`,
    reutilizando el patrón de `CalculatorPreferences`; solo el orden).
  - Reutiliza `DataFreshness`, `MarketWriteOutcome`, `MarketImageURL`.
- **FutmondoApp (vistas SwiftUI, `#if canImport(SwiftUI)`, device-validated)**:
  - `FavoritesView`, `FavoritesViewModel` (@MainActor @Observable),
    `FavoritePlayerCard`, reutiliza `ConfirmSheet` y el `SofascoreDetailSheet` +
    menú "…" de Mercado.

## Jerarquía de componentes

```
FavoritesView
├── toolbar: ChampionshipMenu (leading) · sortMenu (leading) · settingsMenu (trailing)
├── countLabel ("N jugadores favoritos libres")
├── estado vacío / carga / error (componentes compartidos)
└── LazyVGrid de FavoritePlayerCard[]   // 2-up, estética tiles de Mercado
     ├── hero (foto) + nombre + equipo (escudo) + chips de posición
     ├── badges: Sofascore + titularidad
     ├── métricas: VALOR · TENDENCIA · PUNTOS(Jx) · MEDIA (+ casa/fuera/partidos)
     ├── menú "…": Ver perfil Sofascore / Ver estadísticas
     └── botón "Quitar" (destructivo) → ConfirmSheet
```

## Estado (FavoritesViewModel, @MainActor @Observable)

- `players: [FavoritePlayer]`, `sortField`, `isWriting`, `phase`, `lastNotice`.
- `freshness: DataFreshness` + `loadIfNeeded()` + `invalidate()`.
- Deriva la lista ordenada vía `FavoritesSorter`.
- Sin `onWriteAccepted`/cross-invalidación (quitar un favorito no cambia saldos,
  FR7.1).

## Validación / reglas de UI

- "Quitar" requiere confirmación (BR5.1) y respeta la guardia `isWriting`
  (BR5.3); fallo → lista intacta + re-habilitar (BR5.4).
- Nulos/cero → "-" (BR3.1); media con casa/fuera/partidos como texto secundario
  (BR3.2); badge por `sofascore_rating`, `rating` no se muestra (BR3.3).
- "Ver perfil Sofascore" solo si hay URL (BR6.1). Accesibilidad: labels, no
  solo-color, Reduce Motion.

## Integración con servicios (sin cambio de backend, C1)

Rutas EXACTAS confirmadas contra la fuente Angular `favorites.service.ts`
(`baseUrl = /api/v1/favorites`):

| Acción | Método + ruta | Forma | Notas |
|---|---|---|---|
| Cargar favoritos | `GET /api/v1/favorites/my?championship_id=<id>` | query param | NUEVO cliente; respuesta tolerante array/wrapped |
| Quitar de favoritos | `POST /api/v1/favorites/unfollow?championship_id=<id>&player_id=<id>` | **ambos ids como query params, body VACÍO `{}`** | NUEVO; devuelve `MarketWriteOutcome`. OJO: a diferencia de `RosterService.cancelSale` (body JSON), unfollow usa **query params** |
| Perfil / estadísticas Sofascore | componentes de Mercado reutilizados | — | sin backend nuevo |

`HTTPFavoritesService` (actor): `fetchFavorites` hace `GET .../favorites/my`
con `championship_id` percent-encoded en la query; `unfollow` hace
`POST .../favorites/unfollow` con `championship_id` y `player_id` percent-encoded
en la query y sin cuerpo (igual que la web).

## Navegación

- 4.ª pestaña del `RootTabView` (icono `star`/`star.fill`), tinte verde,
  accesible por icono + etiqueta (FR8.1).
