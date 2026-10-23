## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T19:23:38Z
**Iteration:** 1

Revisión adversarial de la postura **NO-APLICA** de infraestructura/CI-CD para la unidad `u1-budget-data` (librería cliente iOS `FutmondoKit/Budget/`). Intenté refutarla por tres vías: que el gate bloqueante dejara de correr sobre el PR, que alguna regla de secretos/dependencias quedara sorteada, y que no añadir un runner Swift fuera un recorte de control disfrazado de alcance. Ninguna se sostiene.

- **El gate sigue corriendo**: `team.md` (Way of Working) fija `ci.yml` job `quality` como **required status check** sobre `pull_request → main`, replicado en el job `verify` de `fly-deploy.yml` para push directo. Es un control a nivel de repo, no opt-in por cambio, de modo que un PR que sólo añade ficheros Swift no puede evitar `gitleaks` + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`. El artefacto afirma exactamente esto ("aplica al PR tal cual"): correcto.
- **Secretos/dependencias no se sortean**: `gitleaks` escanea todo el árbol, así que los ficheros Swift nuevos siguen escaneados; la unidad no introduce dependencias (SDK de Apple, coste 0 €), consistente con el mandato durable de coste 0 € de `team.md` (Deployment). No se baja ni silencia ningún control.
- **No añadir runner Swift es defendible**: `team.md` (Testing Posture, matiz nativo iOS) ya documenta que una capa nativa exigiría **rehacer el arnés de test de UI** y re-basar umbrales sobre un runner distinto — trabajo de otro intent, no de éste. El artefacto difiere el runner macOS/Swift a un intent aparte y mantiene la verificación local `swift build && swift test`: decisión de alcance coherente, no un control caído.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/traceability.json > elements[0].requirements | El único elemento (cicd-pipeline NO-APLICA) traza a `NFR1.1`, que es el arranque con `JWT_SECRET` no-default del backend web; no es la justificación real del NO-APLICA (que es "sin cambios de infra/CI para una librería cliente"). La traza es tangencial y puede confundir al lector del gate. | Trazar a la NFR/regla que realmente respalda el NO-APLICA (gate de CI existente / coste 0 €), o anotar explícitamente por qué `NFR1.1` es el ancla. No bloqueante. | New |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/cicd-pipeline.md > Verificación | La verificación local `swift build && swift test` corre en WSL del desarrollador y no queda reflejada en ningún control automatizado del PR; es una garantía manual, no bloqueante. Es aceptable para una librería cliente sin runner Swift, pero conviene dejar constancia de que la ausencia de gate Swift es un riesgo asumido (regresión Swift no detectada por el gate actual). | Registrar explícitamente como riesgo asumido/deuda ("sin cobertura de CI para el paquete iOS; verificación local obligatoria antes del merge"), para que el gate no lea el NO-APLICA como "nada que verificar". | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | N/A | Revisión por inspección cruzada de artefactos y `team.md`. |

### Summary

La postura NO-APLICA está justificada y no deja caer silenciosamente ningún control: el gate bloqueante del PR sigue vigente a nivel de repo, no se sortea ninguna regla de secretos/dependencias, y diferir el runner Swift es un recorte de alcance coherente con las prácticas del equipo. Sólo dos puntos menores de documentación (traza tangencial a `NFR1.1` y riesgo asumido de la verificación Swift manual), ninguno bloqueante.

**Verdict: READY**
