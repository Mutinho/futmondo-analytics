# Constraint Register — F3 Mercado (app nativa iOS)

## Sources

- `aidlc/spaces/default/memory/project.md` / `team.md` — mandatos durables.
- `.../ideation/intent-capture/intent-statement.md` — alcance y límites.
- `.../ideation/market-research/build-vs-buy.md` — Build con SDK de Apple.
- Aprendizajes durables de F1/F2 (toolchain Swift en WSL).

## Restricciones

| ID | Restricción | Origen | Tipo |
|---|---|---|---|
| **C1** | **Coste 0 €**: sólo SDK de Apple; sin dependencias de pago ni servicios con gasto recurrente. Excepción acotada (Apple Developer Program, distribución) **no activada** en este intent. | `project.md`/`team.md` (mandato durable) | Dura |
| **C2** | **Tema Angular como fuente de verdad** del diseño; reutilizar el `DesignSystem` oscuro/neón de F1/F2. Donde no haya equivalente, Apple HIG. | `team.md` Code Style | Dura |
| **C3** | **Sin cambios de backend ni de contrato de API**: el cliente nativo sólo **consume** `/api/v1/market/*`. | intent-statement (alcance) | Dura |
| **C4** | **Seguridad de credenciales**: refresh token en **Keychain**, nunca en claro; la escritura usa la sesión autenticada de F1, sin almacenamiento nuevo de credenciales. | `project.md` Forbidden | Dura |
| **C5** | **Idioma**: identificadores/comentarios/docstrings en **inglés**; texto de usuario en **castellano**. | `team.md` Code Style | Dura |
| **C6** | **Toolchain WSL no compila el target SwiftUI** (`FutmondoApp`): errores arm-only sólo en build de dispositivo con `xtool`. Lógica pura va a `FutmondoKit` (XCTest ejecutable); vistas SwiftUI bajo `#if canImport(SwiftUI)`, validadas en dispositivo. | Aprendizaje F1 (durable) | Dura (de proceso) |
| **C7** | **Sin `actool` en WSL**: Color Sets en código (tokens Swift), no en `Assets.xcassets`. | Aprendizaje F1 (durable) | Dura (de proceso) |
| **C8** | **iOS 26 / Liquid Glass** como línea base del cliente nativo (`Package.swift` `.iOS("26.0")`). | Base F1/F2 | Dura |
| **C9** | **Sólo cards** (no tabla) y **orden descendente**, por paridad con F2. | intent-statement (Q2/orden) | Blanda (decisión de producto) |

## Assumptions & Open Questions

None.
