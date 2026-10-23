# Infrastructure Design — Specification (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA.** U2 no provisiona ni modifica infraestructura. Es UI SwiftUI que corre en el dispositivo del usuario y consume el backend existente (sin cambios). Sin recursos cloud, sin IaC.

## Dependencias de runtime

- SDK de Apple (SwiftUI/Foundation) en el dispositivo.
- Backend `futmondo-api` existente (consumo vía U1 → `NetworkClient` de F1). Sin cambios.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/logical-components.md`

## Assumptions & Open Questions

None.
