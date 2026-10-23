# Cross-Unit Traceability — F3 Mercado (Build and Test gate)

> Gate de cobertura final de etapa (no es la frontera de fase). Enumera cada `FR`
> y `NFR` de `requirements.md` y cada `AC` de tres segmentos de `stories.md`, y
> verifica cobertura `OK` con fichero existente en la `traceability.json` de
> code-generation (stage-level + por Unit). Una sola Unit: `u1-market`.

## Veredicto: **PASS** ✅

Todos los FR1–FR8 están cubiertos con fichero de implementación existente. Los
NFR se cubren por la cadena NFR (requirements → design) y, los de impacto en
código (NFR3.x seguridad, NFR6.x responsividad), por ficheros de
`u1-market/code-generation`. No hay `AC` de tres segmentos en `stories.md` (usa
Given/When/Then a nivel de US, no IDs `ACx.y.z`), así que no hay ACs que
enumerar.

## Cobertura funcional (FR → fichero)

| ID | Estado | Unit | Target (existe) |
|---|---|---|---|
| FR1 | OK | u1-market | ios/Sources/FutmondoApp/Budget/RootTabView.swift |
| FR2 | OK | u1-market | ios/Sources/FutmondoKit/Market/MarketService.swift |
| FR3 | OK | u1-market | ios/Sources/FutmondoApp/Market/MarketBanner.swift |
| FR4 | OK | u1-market | ios/Sources/FutmondoApp/Market/MarketPlayerCard.swift |
| FR5 | OK | u1-market | ios/Sources/FutmondoKit/Market/MarketSorter.swift |
| FR6 | OK | u1-market | ios/Sources/FutmondoApp/Market/BidSheet.swift |
| FR7 | OK | u1-market | ios/Sources/FutmondoApp/Market/MarketPlayerCard.swift |
| FR8 | OK | u1-market | ios/Sources/FutmondoApp/Market/SofascoreDetailSheet.swift |

## Cobertura no funcional (NFR)

| ID | Estado | Dónde se cubre |
|---|---|---|
| NFR1 (coste 0 €) | OK | `Package.swift` `dependencies: []`; tech-stack-decisions NFR1.x |
| NFR2 (tema) | OK | reutiliza DesignSystem F1/F2 (vistas Market); nfr-design NFR2.1 |
| NFR3 (seguridad) | OK | code-generation NFR3.1/3.4/3.5/3.6 → MarketService, BidAmountValidator, URLSessionNetworkClient, MarketWriteOutcome |
| NFR4 (idioma) | OK | identificadores EN / UI ES en los ficheros Market; tech-stack NFR4.1 |
| NFR5 (testabilidad) | OK | lógica en FutmondoKit con XCTest (40 tests); nfr-design NFR5.1 |
| NFR6 (accesibilidad/responsividad) | OK | code-generation NFR6.1/6.3/6.4/6.5/6.6 → MarketViewModel, MarketView, MarketSorter, SofascoreService |

## Elementos sin cubrir

Ninguno.

## Nota sobre verificación

- La cobertura de código (`OK` + fichero existente) está completa. Las dos
  entradas `Unverified` del Target Verification Matrix (cobertura numérica
  `llvm-cov` y validación de UI en dispositivo) son limitaciones de **toolchain
  WSL** afirmadas como durables, NO huecos de trazabilidad: cada FR/NFR traza a
  código existente y la suite está verde.

## Assumptions & Open Questions

None.
