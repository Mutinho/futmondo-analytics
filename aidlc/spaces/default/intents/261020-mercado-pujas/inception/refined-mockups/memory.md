<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — Mockups refinados con mapeo 1:1 al DesignSystem de F1/F2 (NeonGlassCard, PrimaryButton, GlassIconButton, TextInputField, Chips, DSColor/DSFont, MoneyFormatter, estados LoadingState/ErrorState/EmptyState). Sheets de puja/Sofascore y alert de cancelación con HIG. Badges Sofascore/%titular compuestos con tokens existentes (sin dependencia nueva). Interaction spec: bidding deshabilita botones, recarga sólo en éxito. Pull-to-refresh incluido (Q1=A).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-20 — Reviewer advisory (product-lead, 1 iter) sobre mockups: READY, 0 Major, 3 Minor aplicados: (1) M1 nombra orden por defecto value desc; (2) M2 anota tope efectivo available_for_bids (divergencia intencionada Q1=A) y rango de validación; (3) M2/M3 remiten al patrón de resultado de interaction-spec (éxito recarga, rechazo/error no).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
