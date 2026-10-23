# Build and Test Summary — Calculadora nativa iOS

## Estado general

- **Build**: OK (`swift build --package-path ios` → "Build complete!", exit 0).
- **Tests**: 204/204 en verde (`swift test --package-path ios`), 0 fallos.
- Estrategia de test: **minimal** (scope `refactor`). Sin piso de cobertura
  nuevo; la suite existente se mantiene en verde (obligación cumplida).
- Prerequisitos: ninguno externo (SDK de Apple, `dependencies: []`).

## Inventario de tipos de test

| Tipo | Generado | Motivo |
|---|---|---|
| Unit (XCTest, FutmondoKit) | Sí (en Code Generation) | 36 tests nuevos de la Calculadora |
| Integration | NO (N/A) | minimal; frontend-only, backend inmutable |
| Performance | NO (N/A) | minimal; cubierto por patrones nativos + dispositivo |
| Security | NO (N/A) | minimal; sin superficie de seguridad nueva |

## Cobertura por unidad

- Unidad única (Calculadora). Lógica pura (`CalculatorMath`, `CalculatorSorter`,
  `CalculatorPreferences`, DTOs, `SellOutcome`) cubierta con XCTest ejecutable.
- Las vistas SwiftUI quedan fuera del cómputo de cobertura (llvm-cov no fiable
  en WSL; regla durable de memoria) y se validan en dispositivo.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BT-BUILD | build-instructions.md § Comandos de build | `swift build` exit 0 | exit 0, "Build complete!" | `swift build --package-path ios` | build-and-test | Met |
| BT-TESTS | unit-test-instructions.md § Comando | Suite verde (sin regresión) | 204 tests, 0 fallos | `swift test --package-path ios` → "Executed 204 tests, with 0 failures" | build-and-test | Met |
| BT-SUITE-GREEN | team.md § Testing Posture (minimal; suite existente en verde) | Sin tests rotos | 204/204 verde (168 previos + 36 nuevos) | mismo run de tests | build-and-test | Met |
| BT-UI-DEVICE | project.md § Corrections (llvm-cov no fiable en WSL) | Vistas SwiftUI validadas en dispositivo | Validación manual en dispositivo (`install-app.sh`); ya probada por el propietario | n/a en WSL | manual device validation | N/A |

Nota sobre BT-UI-DEVICE: es una **limitación durable y conocida** del toolchain
en WSL (regla afirmada en memoria), no un target medible localmente de esta
etapa, por lo que se marca `N/A` (no `Unverified`): la verificación de UI no es
ejecutable en WSL por diseño. La pantalla ya fue probada en el iPhone por el
propietario durante las revisiones de Code Generation.

## Evaluación de preparación

- **Build-ready**: Sí.
- **Test-ready**: Sí (204 verde).
- **Deployment-ready**: Sí para el paquete; la distribución nativa (App Store /
  `xtool`) y la validación de UI en dispositivo quedan fuera del alcance de este
  intent (sin etapas de Operation en el plan).

## Limitaciones / pendientes

- La cobertura de línea no se verifica numéricamente en WSL (llvm-cov no fiable);
  cubierto por XCTest ejecutable de la lógica pura.
- La UI SwiftUI se valida en dispositivo (ya probada por el propietario en las
  revisiones).
