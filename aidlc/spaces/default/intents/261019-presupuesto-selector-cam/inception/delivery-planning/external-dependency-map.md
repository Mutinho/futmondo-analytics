# External Dependency Map — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (delivery-planning). Idioma: castellano; tokens técnicos verbatim en inglés.

| Dependencia | Tipo | Estado | Nota |
|-------------|------|--------|------|
| SDK de Apple (SwiftUI, Foundation, XCTest) | Plataforma | Disponible | Coste 0 €. |
| `FutmondoKit`/`FutmondoApp` DesignSystem (F1) | Interna | Disponible | Red/auth/tokens de diseño ya construidos. |
| Backend `futmondo-api` (endpoints `balances`, `championships`) | Servicio existente | Disponible | Sin cambios; sólo consumo. |
| `xtool` + iPhone 13 Pro | Toolchain/dispositivo | Disponible (del propietario) | Para build en dispositivo y validación de UI. |
| Apple Developer Program | Distribución | NO activado en este intent | Excepción acotada; no aplica (sin publicación). |

Ninguna dependencia nueva de pago ni OSS. Sin bloqueos externos para empezar la construcción.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/contract-design/contract-summary.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/{dependencies,technology-stack}.md`

## Assumptions & Open Questions

None.
