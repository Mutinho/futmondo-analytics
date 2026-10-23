<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-21T18:25:00Z — al portar una pantalla nativa que añade un campo a un DTO ya consumido por otra pantalla (p. ej. activeBidsCount en MarketUserInfo), el campo nuevo debe ser opcional-con-default (decodeIfPresent ?? 0 + parámetro de init por defecto) para no romper el decode ni los call sites existentes; añadirlo como requerido es una regresión silenciosa. (lo señaló la revisión adversarial)
- 2026-10-21T18:25:30Z — no reutilizar un tipo de resultado de escritura existente (MarketWriteOutcome: accepted/rejected/networkError) cuando el nuevo endpoint devuelve más información (sold/total en /roster/sell): un éxito parcial necesita su propio tipo-suma dedicado, o el caso parcial queda irrepresentable.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
