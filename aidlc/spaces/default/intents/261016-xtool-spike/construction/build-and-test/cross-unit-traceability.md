# Cross-Unit Traceability — Spike de la cadena `xtool` (B-01)

## Contexto

Scope `bugfix` incremental, zero-Unit: no hubo `requirements-analysis` ni `user-stories`, por lo
que no existen `FR`/`NFR`/`AC` formales que enumerar. La trazabilidad se evalúa contra los
objetivos del spike definidos en `traceability.json` de code-generation.

## Verdicto: PASS (con T3 pendiente de validación en vivo)

| ID | Cobertura | Owning Stage/Unit | Target file | Estado |
|----|-----------|-------------------|-------------|--------|
| B-01-app | OK | code-generation | `spikes/ios-xtool/Sources/XToolSpike/ContentView.swift` | existe |
| B-01-xtool-config | OK | code-generation | `spikes/ios-xtool/xtool.yml` | existe |
| B-01-setup | OK | code-generation | `spikes/ios-xtool/scripts/setup-wsl.sh` | existe |
| B-01-smoke | OK | code-generation | `spikes/ios-xtool/scripts/smoke.sh` | existe |
| B-01-runbook | OK | code-generation | `docs/spikes/ios-xtool.md` | existe |

## Elementos no cubiertos

Ninguno a nivel de artefacto: los 5 objetivos del spike tienen fichero existente.

## Hallazgo a elevar en el gate

El objetivo de aceptación **T3-chain-live** (la app arranca en el iPhone 13 Pro vía la cadena
`xtool`) queda `Unverified`: su validación es manual en dispositivo y no ejecutable en este
entorno. No es un hueco de cobertura de artefactos, sino la verificación en vivo pendiente de
una sesión interactiva con tu hardware y Apple ID.
