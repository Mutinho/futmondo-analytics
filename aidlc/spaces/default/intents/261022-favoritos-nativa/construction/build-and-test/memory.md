<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-23T07:00:00Z — crossfade skeleton→contenido en SwiftUI: poner `.transition(.opacity)` en las ramas de un `switch` NO cruza (SwiftUI reemplaza el subárbol y el contenido aparece de golpe). El patrón fiable es un `ZStack` con AMBAS capas montadas y opacidad cruzada por un flag `isLoading` (componente reutilizable `CrossfadeLoader`), animado con `.animation(value: isLoading)`.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-23T07:05:00Z — skeleton de carga nativo "WOW" a coste 0: relleno con gradiente de marca en movimiento (`AuroraFill`, verde→violeta del DS, drift en bucle) + entrada escalonada + crossfade, reutilizable (`SkeletonCard`/`SkeletonRow`/`SkeletonHeader`/`SkeletonScreen`/`SkeletonListScreen`), respetando Reduce Motion. Mejor percepción que spinner+'Cargando…'. Las pantallas con lista de filas (Presupuesto) necesitan `SkeletonRow` propio, no el grid de tiles.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-23T07:10:00Z — la lentitud de carga percibida en Mercado (~1,6s) y Favoritos (~3,4s) es del BACKEND (consultan Futmondo/Sofascore en vivo), no del cliente (medido; balances 0,4s porque lee de Neon sincronizado). Mejora de raíz = intent de backend (servir desde datos pre-sincronizados / caché TTL). Documentado en knowledge/aidlc-shared/backend-latency-market-favorites.md.
