## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T15:53:44Z
**Iteration:** 1

Revisión adversarial de los NFR/seguridad de `u1-budget-data` (F2). Objetivo: refutar las garantías de no-fuga de credenciales, persistencia no sensible, transporte, decode estricto y las decisiones de stack (cero deps, testabilidad WSL, concurrencia). Tras cruzar SR1–SR4 y TS1–TS3 contra `functional-spec.md`, `requirements.md` (NFR1/NFR2/NFR6) y la `traceability.json`, no encuentro ninguna fuga real ni violación de coste 0 €: las llamadas de U1 reutilizan `AuthService`/`NetworkClient`/Keychain de F1 sin introducir almacenamiento nuevo, `UserDefaults` sólo guarda `championship_id` (no sensible), el transporte es HTTPS por construcción del `URLSessionNetworkClient`, y el decode es `Codable` estricto con opcionales tolerados. `Package.swift` mantiene `dependencies: []` y todo vive en `FutmondoKit` testeable con `swift test`. Las garantías son verificables (tabla de casos determinista, fakes del `NetworkClient`, suite de test de `UserDefaults`). Quedan dos imprecisiones menores de redacción que conviene cerrar, ninguna bloqueante.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-requirements/security-requirements.md > SR1 | SR1 afirma que el contexto de error no sensible incluye "status, endpoint", pero no fija si "endpoint" es la ruta sola o la URL completa con query string (`?championship_id=<id>`). Hoy la query sólo lleva un id no sensible, pero la redacción deja abierta una ruta de fuga si una llamada futura reutiliza este patrón con un valor sensible en la query, y el requisito es la única barrera escrita contra ello. | Precisar en SR1 que el contexto no sensible de `NetworkError` es la **ruta** (path) o path + query no sensible, y que **nunca** se incluye la URL de petición cruda completa en `message`/`localizedDescription`/`debugDescription`. | New |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-requirements/tech-stack-decisions.md > TS2 | TS2 fija formateo de dinero "sin `NumberFormatter`/locale" con separador `,` fijo, lo que contradice el texto de FR1.3 ("separador decimal el de la locale", "redondeo half-up"); la `functional-spec` lo refina a locale-independiente y half-away-from-zero por testabilidad en WSL. La elección es correcta y mejora el determinismo, pero la desviación respecto a FR1.3 no está anotada como tal en los artefactos NFR. | Anotar en TS2 (o en `functional-spec`) que el formato locale-independiente y half-away-from-zero es una desviación deliberada de FR1.3 motivada por tests deterministas en WSL, para que el gate no la lea como contradicción. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | n/a | Revisión por inspección cruzada de artefactos y trazabilidad. |

### Summary

Los NFR/seguridad de `u1-budget-data` son implementables y coherentes: sin fuga real de credenciales, sin deps nuevas, coste 0 € respetado y claims testables con `swift test`. Sólo quedan dos precisiones de redacción menores (alcance de "endpoint" en SR1 y desviación de formato de FR1.3 en TS2), ninguna bloqueante.

**Verdict: READY**
