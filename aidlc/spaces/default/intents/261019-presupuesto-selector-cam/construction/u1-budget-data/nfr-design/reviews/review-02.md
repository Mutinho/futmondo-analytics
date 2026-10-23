## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T19:04:19Z
**Iteration:** 2

Iteración 2 (final, adversarial) del NFR Design (`security-design` + `logical-components`) de `u1-budget-data`. La iteración 1 fue READY con dos Minor (R-01, R-02); el objetivo de esta pasada es confirmar que ambos quedaron aplicados y volver a intentar refutar el diseño sobre las rutas afectadas. Verifiqué los dos puntos y no encontré ningún Critical ni Major nuevo.

**R-01 (cobertura de no-fuga en el decode-error).** `security-design.md` > SR1 ahora asevera explícitamente la no-fuga en **ambas rutas de error**: el `NetworkError` de red/status y el `DecodingError` de un response malformado (SR4). Deja constancia de que el `DecodingError` de Foundation describe la ruta tipo/clave y no el payload de credenciales, y aun así el test lo asevera. Fixed.

**R-02 (frontera U1/U2 en la escritura del id activo).** `logical-components.md` incorpora el párrafo **Frontera U1/U2**: U1 **expone** `UserDefaultsActiveChampionshipStore` (`activeId` / `setActive`) y la función pura `ActiveChampionshipResolver.resolve`; U1 **no decide cuándo** persistir, es el `BudgetViewModel` de U2 quien invoca `setActive` si el id resuelto difiere del persistido (owner de FR3.3). La ambigüedad de doble escritura queda cerrada. Fixed.

Sin regresiones: el layout sigue siendo aditivo sobre `FutmondoKit/Budget/` sin tocar `Networking/`/`Auth/`/`DesignSystem/` de F1, SR2-SR3 intactos, y `## Assumptions & Open Questions: None` en ambos artefactos.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | construction/u1-budget-data/nfr-design/security-design.md > SR1 (no-leak error test) | El test de no-fuga cubre el error de red, pero el error de decode estricto (SR4) es una ruta de error distinta cuyo mensaje (claves/tipos de Foundation) no se asevera explícitamente como libre de valores sensibles | Extender la aserción de no-fuga también al mensaje del error de decode, o dejar constancia explícita de que el `DecodingError` de Foundation no contiene credenciales por construcción | Resolved (reviewer) |
| R-02 | Minor | construction/u1-budget-data/functional-design/functional-spec.md > ActiveChampionshipResolver / ActiveChampionshipStore | `UserDefaultsActiveChampionshipStore` (persistencia del id) vive en U1, mientras el spec anota que el owner de persistir el id resuelto es el `BudgetViewModel` (U2); la frontera de quién escribe el id activo queda ambigua entre U1 y U2 | Aclarar en una línea que U1 expone el store y U2 decide cuándo invocar `setActive`, para que no haya doble escritura del id | Resolved (reviewer) |

> R-01 Reviewer note: SR1 extiende la aserción de no-fuga al `DecodingError` (SR4) además del `NetworkError`, con constancia explícita de que Foundation no expone credenciales

> R-02 Reviewer note: `logical-components.md` fija la frontera: U1 expone store + resolver; U2 `BudgetViewModel` es owner de `setActive` (FR3.3)

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | N/A | Revisión por inspección cruzada de artefactos y verificación de hallazgos previos |

### Summary

Ambos Minor de la iteración 1 quedan aplicados (cobertura de no-fuga en el decode-error y frontera U1/U2 de escritura del id activo); sin hallazgos nuevos ni regresiones.

**Verdict: READY**
