# RAID Log — F3 Mercado (app nativa iOS)

> Risks, Assumptions, Issues, Dependencies. Elevado al nivel de ideación; el
> detalle de mitigación técnica se afina en diseño/construcción.

## Sources

- `.../ideation/feasibility/feasibility-assessment.md` y `constraint-register.md`.
- Aprendizajes durables de F1/F2 (`project.md` Corrections).
- `angular-app/src/app/features/market/` (comportamiento de escritura).

## Risks

| ID | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| **R1** | Errores **arm-only** del target SwiftUI que no afloran en `swift build`/`swift test` de WSL (Equatable, strict concurrency Swift 6, APIs UIKit/SwiftUI, colisión de nombres). | Media | Medio | Rigor anti-hueco-WSL: payloads `Equatable`, estáticas públicas `Sendable`, `Image(uiImage:)`, cualificar `FutmondoKit.Transaction`; validación en dispositivo con `xtool`. |
| **R2** | **Escritura con efecto económico real** (pujar/cancelar afecta al campeonato compartido). | Media | Alto | Confirmación + validación de importe (mín precio de mercado, máx disponible); señal clara aceptada/rechazada/error de red; refresco tras acción; deshabilitar botones durante la operación (patrón `bidding`). |
| **R3** | El **endpoint Sofascore** puede fallar o tardar (IP ban, timeout). | Media | Bajo | Sheet con estados loading/error aislados; el fallo de Sofascore no bloquea el Mercado. |
| **R4** | Deriva visual respecto a la fuente Angular. | Baja | Bajo | Reutilizar `DesignSystem`; cards 1:1 con la card Angular (Q2=A). |

## Assumptions

- **A1** — La sesión autenticada de F1 (`AuthService` + Keychain) cubre la
  escritura sin cambios; no hace falta nuevo flujo de auth. (Confirmar en diseño.)
- **A2** — `current_bid_id` viene en el payload de `/today` por jugador con puja
  activa (confirmado en `MarketPlayer`), suficiente para cancelar.

## Issues

- **None** (abiertos) en esta etapa.

## Dependencies

- **D1** — Base F1/F2 en `ios/` (`FutmondoKit`, `DesignSystem`, `RootTabView`):
  dependencia directa de implementación. Ya en producción/cerrada.
- **D2** — Backend `/api/v1/market/*` en producción (sin cambios). Dependencia de
  consumo.
- **D3** — Validación final en **dispositivo (iPhone 13 Pro) con `xtool`** por el
  usuario; necesaria para cerrar la fidelidad y los errores arm-only.

## Assumptions & Open Questions

None.
