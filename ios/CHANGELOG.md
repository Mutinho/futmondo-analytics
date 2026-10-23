# Changelog — App nativa iOS (FutmondoApp)

Registro de cambios de la app nativa iOS (SwiftUI, SDK de Apple, coste 0 €).
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/).

## [No publicado] — 2026-10-21

### Añadido
- **Pantalla F3 "Mercado"** (pujas): rejilla 2-up de tiles con hero (foto del
  jugador semitransparente + nombre + escudo del equipo), VALOR y PUNTOS
  destacados, CTA "PUJAR" homogéneo (verde primario sólido) y menú `...` de
  acciones secundarias ("Ver estadísticas" / "Ver perfil Sofascore"). Segunda
  pestaña del `RootTabView`. Fuente de verdad: vista Angular `features/market/`.
- **Hoja de puja** (`BidSheet`): importe hero, `Slider` + `Stepper` nativos
  acotados a `[market_price, available]`.
- **Hoja de detalle Sofascore** a pantalla completa con hero estilo tile y
  rating grande; enlace nativo a sofascore.com.
- **Caché en memoria** para no refetchar al cambiar de pestaña: política pura
  `DataFreshness` (TTL 180 s + campeonato cargado), `loadIfNeeded()` en `.task`,
  **pull-to-refresh** (`.refreshable`) en Mercado y Presupuesto, e **invalidación
  cruzada**: una puja/cancelación aceptada invalida la caché de Presupuesto.
- **Píldora de economía flotante** al hacer scroll en Mercado
  (Disponible · Presupuesto · Balance), vía `onScrollGeometryChange` (iOS 18+).
- **ProMotion 120 Hz**: `CADisableMinimumFrameDurationOnPhone` vía `xtool.yml`.

### Cambiado
- Selectores de campeonato / orden / Compra-Venta a `Menu` nativo con filas
  `Toggle` (alineación homogénea del gutter del check).
- Tinte de pestaña seleccionada = verde neón (`DSColor.primary`), accesibilidad
  preservada (icono relleno + etiqueta, no sólo color).
- Banner de Mercado simplificado (eliminada la barra de capacidad/leyenda).

### Corregido
- `hasActiveBid` respeta el falsy de Angular: `current_bid: 0` = **sin puja**
  (exige `currentBid > 0` y `currentBidId` no vacío).
- Decodificación del detalle Sofascore: respuesta envuelta `{success, player}`.
- Conflicto de dos `.sheet(item:)`: unificado en un único enum `MarketSheetRoute`.
- Timeout de type-check en `SofascoreDetailSheet` (tipado explícito del
  intermedio).

### Notas
- Lógica testeable en `FutmondoKit` (XCTest): **168 tests en verde**
  (`swift test`). Vistas SwiftUI validadas en dispositivo (`scripts/install-app.sh`),
  fuera del cómputo de cobertura (`llvm-cov` no fiable en WSL).
- Patrones reutilizables para futuras pantallas en
  `aidlc/spaces/default/knowledge/aidlc-shared/native-ios-ui-patterns.md`.
