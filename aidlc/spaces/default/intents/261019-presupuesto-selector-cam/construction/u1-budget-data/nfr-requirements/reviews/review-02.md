## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T15:55:30Z
**Iteration:** 2

Iteración 2 (final) adversarial de los NFR/seguridad de `u1-budget-data` (F2). La iteración 1 fue READY con dos findings Minor; esta pasada verifica que ambos se cerraron, sin reabrir el resto de garantías. Confirmo que las dos correcciones están aplicadas en los artefactos y cierran la ambigüedad de redacción sin relajar ningún requisito:

- **R-01 (SR1)**: `security-requirements.md` fija ahora el contexto de `NetworkError` como status HTTP + **path del endpoint** (p. ej. `/api/v1/analytics/balances`) y declara explícitamente que **nunca** se incluye la URL completa con query string ni ningún valor de query, razonando el contrato path-only para que el patrón siga seguro aunque una llamada futura ponga un valor sensible en la query. Cierra la ruta de fuga que señalaba el finding.
- **R-02 (TS2)**: `tech-stack-decisions.md` anota ahora la **desviación deliberada de FR1.3** (separador `,` constante independiente de locale + half-away-from-zero por aritmética entera frente a "separador de la locale"/"half-up"), encuadrada como decisión de determinismo de tests en WSL que **preserva** el resultado visible (`12,4M`, `-1,2M`) y **no relaja** ningún requisito. El gate ya no la leería como contradicción.

No aparecen regresiones ni nuevos riesgos: sin almacenamiento de credenciales nuevo (reutiliza `AuthService`/`NetworkClient`/Keychain de F1), `UserDefaults` sólo guarda `championship_id`, transporte HTTPS por construcción, decode `Codable` estricto, `Package.swift` con `dependencies: []` y todo en `FutmondoKit` testeable con `swift test`.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-requirements/security-requirements.md > SR1 | SR1 afirma que el contexto de error no sensible incluye "status, endpoint", pero no fija si "endpoint" es la ruta sola o la URL completa con query string (`?championship_id=<id>`). Hoy la query sólo lleva un id no sensible, pero la redacción deja abierta una ruta de fuga si una llamada futura reutiliza este patrón con un valor sensible en la query, y el requisito es la única barrera escrita contra ello. | Precisar en SR1 que el contexto no sensible de `NetworkError` es la **ruta** (path) o path + query no sensible, y que **nunca** se incluye la URL de petición cruda completa en `message`/`localizedDescription`/`debugDescription`. | Resolved (reviewer) |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-requirements/tech-stack-decisions.md > TS2 | TS2 fija formateo de dinero "sin `NumberFormatter`/locale" con separador `,` fijo, lo que contradice el texto de FR1.3 ("separador decimal el de la locale", "redondeo half-up"); la `functional-spec` lo refina a locale-independiente y half-away-from-zero por testabilidad en WSL. La elección es correcta y mejora el determinismo, pero la desviación respecto a FR1.3 no está anotada como tal en los artefactos NFR. | Anotar en TS2 (o en `functional-spec`) que el formato locale-independiente y half-away-from-zero es una desviación deliberada de FR1.3 motivada por tests deterministas en WSL, para que el gate no la lea como contradicción. | Resolved (reviewer) |

> R-01 Reviewer note: SR1 fija el contexto de `NetworkError` a status + path del endpoint y prohíbe la URL completa con query; cierra la ambigüedad de alcance de "endpoint".

> R-02 Reviewer note: TS2 anota la desviación deliberada de FR1.3 como decisión de determinismo (locale-independiente + half-away-from-zero) que preserva el resultado visible y no relaja nada.

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | n/a | Revisión por inspección cruzada de artefactos; confirmación de los dos findings Minor previos. |

### Summary

Las dos precisiones de redacción Minor de la iteración 1 están aplicadas y correctas; los NFR/seguridad de `u1-budget-data` quedan implementables y coherentes, sin findings abiertos.

**Verdict: READY**
