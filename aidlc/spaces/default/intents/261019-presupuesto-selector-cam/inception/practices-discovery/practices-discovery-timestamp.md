# Practices Discovery — Timestamp F2 `261019-presupuesto-selector-cam`

- **Fecha**: 2026-10-19
- **Stage**: practices-discovery (phase inception)
- **Agent**: aidlc-pipeline-deploy-agent (release engineer)
- **Intent**: F2 `261019-presupuesto-selector-cam` — feature nativa iOS SwiftUI
  (pantalla de Budget + selector de championship), brownfield, coste 0 €, tema
  Angular como fuente de verdad, sin cambios de backend.

## Nota de herencia

F2 **hereda el set de reglas ya afirmado** en
`aidlc/spaces/default/memory/{team.md,project.md,org.md}` por los intents previos
(incluido F1 `261018-design-system-nativo`, que introdujo la capa nativa `ios/`)
**sin contradicciones**. No se promueve ninguna práctica nueva: el único candidato
plausible (estructura/testing iOS — `FutmondoKit` testeable + `FutmondoApp` SwiftUI
bajo `#if canImport(SwiftUI)`, validación en dispositivo; Color Sets en código;
`llvm-cov` no fiable en WSL) **ya está capturado** como Correction aprendida
(learned 2026-10-19) en `project.md`.

Este stage es de **confirmación**, no de re-invención: las prácticas discovered
reafirman las reglas vigentes y las mapean a lo que F2 toca (Budget + selector
sobre `FutmondoKit`/`FutmondoApp`).

## Sources

- `aidlc/spaces/default/memory/{team.md,project.md,org.md}`
- `aidlc/spaces/default/codekb/futmondo-analytics/{technology-stack,code-quality-assessment,dependencies,code-structure}.md`
- `ios/Package.swift`, `ios/xtool.yml`, `ios/Sources/**`, `ios/Tests/**`
- Artefactos hermanos: `team-practices.md`, `discovered-rules.md`, `evidence.md`

## Assumptions & Open Questions

None.
