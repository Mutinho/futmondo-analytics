# Build and Test Summary — F3 Mercado

## Estado general

- **Build**: `swift build --package-path ios` → **success** (exit 0).
- **Tests**: `swift test --package-path ios` → **153/153 verde** (40 nuevos de
  Mercado + 113 preexistentes de F1/F2), 0 fallos.
- **Readiness**: build-ready y test-ready para la lógica de `FutmondoKit`. La UI
  SwiftUI se valida en dispositivo (iPhone 13 Pro, `xtool dev build`), diferido —
  no ejecutable en WSL por desajuste compilador/SDK (limitación de toolchain, no
  del código).

## Inventario de tipos de test generados

- Unit (per-unit, Code Generation): XCTest sobre `FutmondoKit` (modelos, sorter,
  validador, mapeo de outcome, servicios con doble). **Ejecutados**.
- Integration (`integration-test-instructions.md`, standard): fronteras
  `u1-market ↔ F1/F2` y `↔ contratos backend`, cubiertas con los dobles in-memory.
- Performance (`performance-test-instructions.md`): responsividad de UI; validada
  en dispositivo / `MarketSorterTests`; sin load tests (cliente, no servicio).
- Security (`security-test-instructions.md`): no-fuga de credenciales + auth +
  TLS; cubierto por tests + gitleaks del gate.

## Expectativas de cobertura por Unit

- `u1-market`: piso feature 80% línea medido sobre la lógica de `FutmondoKit`
  (40 tests, 5–8 por componente). El número `llvm-cov` no es fiable en WSL
  (aprendizaje durable): se documenta como no verificable numéricamente aquí, no
  se relaja ningún umbral. Vistas SwiftUI fuera del cómputo (validación en
  dispositivo).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BUILD | build-instructions.md | `swift build` exit 0 | exit 0, Build complete | salida de `swift build --package-path ios` | build-and-test | Met |
| UNIT-TESTS | unit-test-instructions.md | suite verde | 153/153, 0 fallos | salida de `swift test --package-path ios` | build-and-test | Met |
| COV-FLOOR-FK | code-generation-plan.md (feature 80% línea, FutmondoKit) | 80% línea sobre lógica testeable | No medible numéricamente (llvm-cov no fiable en WSL) | aprendizaje durable `project.md`; 40 tests 5–8/componente | build-and-test | Unverified |
| NFR6.x-UI | nfr-design/performance-design.md | responsividad UI | Validación en dispositivo diferida (WSL no compila `xtool dev build`) | code-summary.md (Step 12 sin marcar) | device (manual) | Unverified |
| NFR3.x-SEC | nfr-design/security-design.md | sin fuga de credenciales, Bearer, TLS | aseverado por `MarketServiceTests` (no-fuga, Bearer); TLS por tests F1 | `swift test` verde | build-and-test | Met |
| EXISTING-SUITE-GREEN | team.md Testing Posture | suite existente verde | 113 tests preexistentes verdes dentro de los 153 | salida de `swift test` | build-and-test | Met |

## Limitaciones / pendientes conocidos

- **COV-FLOOR-FK = Unverified**: la cobertura de línea no es medible de forma
  fiable con el toolchain Swift en WSL (aprendizaje durable). NO se bajó ni
  desactivó ningún umbral; se documenta la limitación. La lógica testeable está
  en `FutmondoKit` con 5–8 tests por componente.
- **NFR6.x-UI = Unverified**: la validación de vistas SwiftUI en dispositivo
  (`xtool dev build`, iPhone 13 Pro) no es ejecutable en este WSL por desajuste
  compilador/SDK; es trabajo de dispositivo, conforme al aprendizaje durable.
  No hay una etapa posterior de validación de UI nativa programada en el plan
  (la dimensión E2E/dispositivo es inexistente hoy, documentada como riesgo en
  `team.md`); queda como verificación manual de dispositivo.

> Nota: ambos `Unverified` provienen de limitaciones **de entorno/toolchain WSL
> ya afirmadas como durables**, no de defectos del código ni de umbrales
> relajados. La suite ejecutable está verde.

## Assumptions & Open Questions

None.
