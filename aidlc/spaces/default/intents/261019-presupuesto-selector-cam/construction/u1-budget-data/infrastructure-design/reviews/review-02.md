## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T19:25:21Z
**Iteration:** 2

Iteración 2 (final) adversarial de la postura **NO-APLICA** de infraestructura/CI-CD para la unidad `u1-budget-data` (librería cliente iOS `FutmondoKit/Budget/`). La iteración 1 fue READY con dos findings Minor (R-01 traza tangencial a `NFR1.1`; R-02 verificación Swift local sin constancia de riesgo asumido). Re-verifiqué ambos contra los artefactos corregidos e intenté refutar que los arreglos fueran cosméticos; ambos quedan cerrados con sustancia.

- **R-01 (traza) — Fixed**: `traceability.json` ya no traza el único elemento a `NFR1.1`. Ahora `elements[0].requirements` es `["NFR6.1"]`, con una `note` que indica que la justificación real es la postura de verificación de UI/iOS (`swift build/test` local en WSL, sin runner Swift en CI) y el coste 0 €, y que `NFR1.1` (JWT_SECRET) **no aplica aquí**. Corrige exactamente la ambigüedad reportada: el ancla es ahora la NFR que respalda de verdad el NO-APLICA y la no-aplicabilidad de `NFR1.1` queda explícita.
- **R-02 (riesgo asumido) — Fixed**: `cicd-pipeline.md` añade la sección **"Riesgo/deuda aceptada"** que registra `swift build && swift test` como **garantía manual local** (WSL) **sin control automatizado en el PR**, declarándolo **deuda/riesgo aceptado** y aclarando que NO-APLICA significa "no hay infra/CI nuevo que diseñar", **no** "nada que verificar"; deja el runner Swift en CI como follow-up (intent aparte). El NO-APLICA ya no puede leerse como ausencia de verificación.

No aparecen regresiones ni nuevos riesgos: el gate bloqueante del PR sigue vigente a nivel de repo (no opt-in por cambio), `gitleaks` escanea el árbol completo incluidos los ficheros Swift nuevos, no se introducen dependencias ni se relaja ningún control, y diferir el runner macOS/Swift sigue siendo un recorte de alcance coherente con `team.md` (Testing Posture, matiz nativo iOS). Sin findings nuevos.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/traceability.json > elements[0].requirements | El único elemento (cicd-pipeline NO-APLICA) traza a `NFR1.1`, que es el arranque con `JWT_SECRET` no-default del backend web; no es la justificación real del NO-APLICA (que es "sin cambios de infra/CI para una librería cliente"). La traza es tangencial y puede confundir al lector del gate. | Trazar a la NFR/regla que realmente respalda el NO-APLICA (gate de CI existente / coste 0 €), o anotar explícitamente por qué `NFR1.1` es el ancla. No bloqueante. | Resolved (reviewer) |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/cicd-pipeline.md > Verificación | La verificación local `swift build && swift test` corre en WSL del desarrollador y no queda reflejada en ningún control automatizado del PR; es una garantía manual, no bloqueante. Es aceptable para una librería cliente sin runner Swift, pero conviene dejar constancia de que la ausencia de gate Swift es un riesgo asumido (regresión Swift no detectada por el gate actual). | Registrar explícitamente como riesgo asumido/deuda ("sin cobertura de CI para el paquete iOS; verificación local obligatoria antes del merge"), para que el gate no lea el NO-APLICA como "nada que verificar". | Resolved (reviewer) |

> R-01 Reviewer note: `traceability.json` traza ahora a `NFR6.1` con nota de que `NFR1.1` no aplica; traza tangencial eliminada.

> R-02 Reviewer note: `cicd-pipeline.md` registra la verificación Swift local como riesgo/deuda aceptado sin control automatizado en el PR; NO-APLICA ya no se lee como "nada que verificar".

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | N/A | Revisión por inspección cruzada de los artefactos corregidos y la review de iteración 1. |

### Summary

Ambos findings Minor de la iteración 1 están corregidos con sustancia: la traza apunta ahora a `NFR6.1` con la no-aplicabilidad de `NFR1.1` explícita, y la verificación Swift local queda registrada como riesgo/deuda aceptado. Sin findings nuevos ni regresiones; el diseño es implementable.

**Verdict: READY**
