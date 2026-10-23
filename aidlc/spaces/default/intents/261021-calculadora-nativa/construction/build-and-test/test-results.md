# Test Results — Calculadora nativa iOS

## Build

- Comando: `swift build --package-path ios`
- Resultado: **éxito** — "Build complete!", exit 0.

## Tests

- Comando: `swift test --package-path ios`
- Resultado: **204 ejecutados, 0 fallos, 0 inesperados** (0.295 s).
  - Previos: 168. Nuevos de la Calculadora: 36
    (`CalculatorMathTests` 10, `CalculatorSorterTests` 7,
    `CalculatorPreferencesTests` 6, `RosterPlayerTests` 13).
- Omitidos: 0.

## Detalle de fallos

Ninguno.

## Cobertura

No se mide numéricamente (llvm-cov no fiable con el toolchain de Swift en WSL —
regla durable del proyecto). La lógica pura testeable está cubierta con XCTest
ejecutable; las vistas SwiftUI se validan en dispositivo.

## Target Verification Matrix (final)

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BT-BUILD | build-instructions.md | `swift build` exit 0 | exit 0 | "Build complete!" | build-and-test | Met |
| BT-TESTS | unit-test-instructions.md | Suite verde | 204 tests, 0 fallos | "Executed 204 tests, with 0 failures" | build-and-test | Met |
| BT-SUITE-GREEN | team.md § Testing Posture | Sin regresión | 204/204 verde | mismo run | build-and-test | Met |
| BT-UI-DEVICE | project.md § Corrections | UI validada en dispositivo | No ejecutable en WSL (validada por el propietario en dispositivo) | n/a WSL | manual device validation | N/A |

Todos los targets medibles localmente: **Met**. Único `N/A`: validación de UI en
dispositivo (limitación durable del toolchain en WSL, no un target local).

## Resultado

**Éxito.** Todos los comandos pasaron y todos los targets aplicables están `Met`.
