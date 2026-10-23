## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T19:02:38Z
**Iteration:** 1

Revisión adversarial del NFR Design (`security-design` + `logical-components`) de la unidad `u1-budget-data`. Intenté refutar el diseño por tres vías: (1) una ruta de fuga de credenciales que SR1-SR4 no cubran, (2) un layout que rompa el package F1, y (3) claims no testeables. No encontré ningún Critical ni Major: el diseño cierra las cuatro SR con evidencia comprobable y el layout es aditivo sobre `FutmondoKit` sin tocar F1.

**Hallazgos de seguridad (SR1-SR4).** SR1 queda bien cerrado: los errores se propagan como `NetworkError` tipado de F1 con contexto `status` + `path` (nunca la URL completa ni el query string), y el contrato fija path-only de forma preventiva aunque hoy la query sólo lleve un `championship_id` no sensible; existe un test que asevera que la descripción del error **no** contiene `championship_id` ni tokens. SR2 persiste sólo el id (String) bajo clave fija en `UserDefaults`, sin sesión ni tokens. SR3 hereda el rechazo de base URL no-https del `URLSessionNetworkClient` de F1 y U1 no abre canales nuevos. SR4 usa `Codable` estricto con opcionales que absorben el subconjunto legacy sin ejecución dinámica, coherente con los casos límite de `functional-spec.md`. No se añade superficie de ataque nueva.

**Layout.** Todo cae en `FutmondoKit/Budget/` (subcarpeta nueva) y en `Tests/FutmondoKitTests/Budget*Tests.swift`, sin nuevo target ni dependencia y sin modificar `Networking/`/`Auth/`/`DesignSystem/` salvo para consumir `NetworkClient`. No hay riesgo de romper el package F1 ni ciclo de dependencias. Rendimiento NO-APLICA está justificado (O(n) sobre listas de decenas; la fluidez de render es de U2/NFR4). Trazabilidad completa: SR1-SR4 → NFR2.1 y layout → NFR1.1/NFR6.1.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | construction/u1-budget-data/nfr-design/security-design.md > SR1 (no-leak error test) | El test de no-fuga cubre el error de red, pero el error de decode estricto (SR4) es una ruta de error distinta cuyo mensaje (claves/tipos de Foundation) no se asevera explícitamente como libre de valores sensibles | Extender la aserción de no-fuga también al mensaje del error de decode, o dejar constancia explícita de que el `DecodingError` de Foundation no contiene credenciales por construcción | New |
| R-02 | Minor | construction/u1-budget-data/functional-design/functional-spec.md > ActiveChampionshipResolver / ActiveChampionshipStore | `UserDefaultsActiveChampionshipStore` (persistencia del id) vive en U1, mientras el spec anota que el owner de persistir el id resuelto es el `BudgetViewModel` (U2); la frontera de quién escribe el id activo queda ambigua entre U1 y U2 | Aclarar en una línea que U1 expone el store y U2 decide cuándo invocar `setActive`, para que no haya doble escritura del id | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | N/A | Revisión por inspección cruzada de artefactos y trazabilidad |

### Summary

El diseño de seguridad cierra SR1-SR4 con evidencia testeable y el layout es aditivo sobre `FutmondoKit` sin perturbar F1; sólo quedan dos Minor (cobertura del mensaje de decode-error y aclaración del owner de escritura del id activo) que no bloquean. READY.

**Verdict: READY**
