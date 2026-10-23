# Test Results — F3 Mercado (Build and Test)

## Build

- Comando: `swift build --package-path ios`
- Resultado: **success** (exit 0). "Build complete!"
- Aviso benigno: `libxml2.so.2: no version information available` (FoundationXML
  en Linux; no afecta).

## Tests

- Comando (dedup, scoped al paquete): `swift test --package-path ios`
- Resultado: **153 ejecutados, 0 fallos, 0 skipped** (0.589 s).
  - 40 tests nuevos de Mercado (MarketDTO 8, MarketSorter 8, BidAmountValidator 8,
    MarketWriteOutcome 8, MarketService+Sofascore 8+... ) — todos verde.
  - 113 tests preexistentes de F1/F2 — todos verde (suite existente intacta).

## Cobertura

- `llvm-cov` **no es fiable** con el toolchain Swift en Linux/WSL (aprendizaje
  durable, `project.md`). La cobertura de línea NO se mide numéricamente aquí. La
  lógica testeable está en `FutmondoKit` con 5–8 tests por componente. **Ningún
  umbral se bajó ni desactivó.**

## Target Verification Matrix (finalizada)

| Target ID | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|
| BUILD | exit 0 | exit 0 | `swift build` output | build-and-test | Met |
| UNIT-TESTS | suite verde | 153/153, 0 fallos | `swift test` output | build-and-test | Met |
| EXISTING-SUITE-GREEN | suite existente verde | 113 preexistentes verdes | `swift test` output | build-and-test | Met |
| NFR3.x-SEC | sin fuga credenciales, Bearer, TLS | aseverado por tests | `MarketServiceTests` / tests F1 | build-and-test | Met |
| COV-FLOOR-FK | 80% línea (FutmondoKit) | no medible numéricamente en WSL | aprendizaje durable; 40 tests 5–8/comp. | build-and-test | Unverified |
| NFR6.x-UI | validación de vistas en dispositivo | diferida (WSL no compila `xtool dev build`) | code-summary Step 12 sin marcar | device (manual) | Unverified |

## Análisis de los `Unverified` (ladder de fallo)

- **Rung 1 (fix in-stage)**: no aplica. No es config de test/build ni entorno
  arreglable: es una limitación afirmada del toolchain Swift en WSL (llvm-cov no
  fiable; `xtool dev build` no compila contra el SDK local).
- **Rung 2 (clasificar y estimar impacto)**: la causa raíz NO está en el código
  generado ni en una elección de approach swappable (librería/imagen/flag). Es el
  entorno de ejecución WSL, ya documentado como limitación durable. **No existe un
  fix identificable en ninguna dimensión swappable** que haga medible la cobertura
  o compilable la UI en este WSL sin un dispositivo/host Apple.
- Por tanto: variante **no-fix** del halt-and-ask (autonomía no inventa un fix ni
  decide rendirse; es decisión del humano).

> Los dos `Unverified` son limitaciones de entorno/toolchain afirmadas como
> durables en memoria, NO defectos del código ni umbrales relajados. La suite
> ejecutable está 153/153 verde y el build compila.

## Assumptions & Open Questions

None.
