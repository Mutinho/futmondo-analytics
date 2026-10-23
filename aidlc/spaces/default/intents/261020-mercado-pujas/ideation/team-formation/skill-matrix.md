# Skill Matrix — F3 Mercado (app nativa iOS)

## Sources

- `.../ideation/team-formation/team-assessment.md`.
- `.../ideation/feasibility/feasibility-assessment.md` — elementos técnicos.

## Habilidades requeridas vs cobertura

| Habilidad | Necesaria para | Cobertura |
|---|---|---|
| **SwiftUI** (vistas, sheets, `TabView`) | UI de Mercado, 2ª pestaña, sheet Sofascore | Conductor (persona developer) + sub-agente developer; patrón ya ejercido en F1/F2 |
| **Swift concurrency (async/await, Sendable)** | Servicio de datos + escritura en `FutmondoKit` | Cubierta; aprendizaje durable sobre strict concurrency Swift 6 |
| **Networking HTTPS + Bearer** | Consumo de `/market/*` | `NetworkClient` de F1 ya lo cubre |
| **Diseño/tema (DesignSystem oscuro/neón)** | Fidelidad visual | `DesignSystem` de F1/F2 reutilizable; persona design para matices |
| **Testing (XCTest en `FutmondoKit`)** | Lógica pura (formato, orden, validación de puja) | Patrón de F2 (tests en library target) |
| **Toolchain WSL + `xtool`** | Build de dispositivo, aflorar arm-only | Propietario valida en dispositivo; conductor aplica rigor anti-hueco |

## Brechas

- **Ninguna brecha nueva** respecto a F2. La única habilidad crítica ligada a
  humano es la **validación en dispositivo** (ya cubierta por el propietario).

## Assumptions & Open Questions

None.
