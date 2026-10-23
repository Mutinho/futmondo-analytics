## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-21T08:39:17Z
**Iteration:** 1

### Resumen de verificación

Revisión adversarial de la implementación terminada de `u1-market`. Intenté
refutar el trabajo en los diez ejes señalados y no encontré ningún defecto
bloqueante: la suite corre verde de verdad, los tests aseveran efectos reales y
la lógica de negocio crítica (mapeo de desenlace de escritura, tope de puja,
aislamiento de Sofascore, seguridad) cumple los contratos consumidos.

### Evidencia ejecutada

`swift test --package-path ios` → **153 tests, 0 failures** (exit 0). Los 40
tests nuevos de Mercado están presentes y pasan: `MarketDTOTests`,
`MarketSorterTests`, `BidAmountValidatorTests`, `MarketWriteOutcomeTests`,
`MarketServiceTests` (incluye `SofascoreServiceTests`).

### Hallazgos verificados (sin defecto)

- **Tests genuinos**: aseveran efectos reales, no `assert true`. `MarketServiceTests`
  comprueba la query exacta (`bid?championship_id=…&player_id=…&player_slug=…&price=…&is_clause=false`;
  `cancelbid?championship_id=…&bid_id=…`); cada componente cubre happy + ≥2
  casos de error/borde (p. ej. `BidAmountValidatorTests` cubre valid, límites
  inclusivos, `nonPositive`, `tooLow`, `tooHigh`, parseo de texto).
- **`MarketWriteOutcome.from` exhaustivo y correcto** contra las 8 cajas reales
  de `NetworkError`: 2xx-true→`.accepted`; 2xx-false o 4xx (`clientError`,
  `unauthorized`, `forbidden`)→`.rejected`; 5xx/`transport`/`cancelled`/`decoding`/`unexpectedStatus`→`.networkError`.
  Aseverado en `MarketWriteOutcomeTests` (tests 1–7).
- **BR-UI-2**: el tope de validación es `available_for_bids`, no `max_bid`
  (`BidAmountValidator`), con test dedicado `testCapIsAvailableNotMaxBid`.
- **`isWriting` global + recarga sólo en `.accepted`**: `MarketViewModel`
  bloquea con un `guard !isWriting`, propaga `isWriting` a cada
  `MarketPlayerCard`, y `apply(outcome:)` recarga únicamente en `.accepted`
  (BR-UI-3/BR-UI-4).
- **Aislamiento FR8.2**: `SofascoreService` es un actor separado que apunta a
  `/api/v1/sofascore/player/…` (no `/market`), `404→.empty`, y
  `SofascoreDetailViewModel` es fresco por sheet; ningún camino toca
  `MarketViewModel`.
- **Seguridad (NFR3)**: Bearer vía el `NetworkClient` reutilizado; los avisos
  sólo llevan prosa del backend o texto genérico localizado (aseverado:
  `testRejectionCarriesOnlyBackendProseOrFallback`, `testLoadTodayErrorPropagatesWithoutLeak`,
  `testLoadDetailOutcomeNeverLeaksName`); `URLSessionNetworkClient.init` rechaza
  base URL no-https (NFR3.5); sin secretos/tokens hardcodeados en tests (dobles
  in-memory).
- **`Package.swift`**: `dependencies: []` — sin dependencias nuevas (coste 0 €).
- **`source-manifest.json`**: lista las 22 rutas cambiadas; coincide con el
  árbol real (`MarketSortSheet` vive dentro de `MarketBanner.swift`, ya listado;
  `DSGlassIcon` es un componente F2 reutilizado, no una ruta nueva). Sin
  omisiones ni rutas ajenas.
- **Integridad**: sin imports/referencias rotas (el build compila), sin stubs
  parciales, sin ficheros duplicados `*_modified`.
- **Trazabilidad**: cada target `OK` de `traceability.json` existe en disco
  (verificado, incl. `NFR3.5 → URLSessionNetworkClient.swift`).

Step 12 (build en dispositivo `xtool`) y la ausencia de cobertura numérica
llvm-cov en WSL son límites de toolchain documentados y expuestos con
honestidad; no se penalizan.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| - | - | - | No findings | No action required | Resolved |

### Summary

Implementación completa, testeada (153/153 verde) y coherente con el
functional-spec, el security-design y los requisitos; los diez ejes de la
revisión pasan sin defecto bloqueante. READY.
