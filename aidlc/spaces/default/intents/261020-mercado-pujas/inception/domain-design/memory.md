<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — Componentes: en FutmondoKit C1 MarketPlayer (Equatable/Sendable), C2 MarketUserInfo, C3 MarketTodayResponse, C4 MarketWriteOutcome (enum .accepted/.rejected/.networkError), C5 MarketService (actor), C6 MarketSorter (puro), C7 BidAmountValidator (puro), C8 SofascoreDetail; en FutmondoApp V1 MarketView, V2 MarketViewModel, V3 MarketPlayerCard, V4 BidSheet, V5 CancelBidConfirmation, V6 SofascoreDetailSheet, V7 RootTabView (2ª pestaña). 4 ADRs (partición datos/UI, resultado tipado, tope available_for_bids, sin dependencias). traceability.json cubre FR1–FR8.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
