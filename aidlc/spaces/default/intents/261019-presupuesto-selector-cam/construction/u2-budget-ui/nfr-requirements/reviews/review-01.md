## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T07:26:12Z
**Iteration:** 1

Revisión adversarial de los requisitos NFR/seguridad de `u2-budget-ui` (capa de
presentación SwiftUI que consume U1 `FutmondoKit/Budget` + el DesignSystem de
F1). Busqué rutas de fuga de credenciales por la UI o por los mensajes de error,
mal uso de `UserDefaults`, superficie de red nueva, violaciones de
dependencias/coste y afirmaciones de rendimiento no verificables.

**Qué resiste al escrutinio.** SR1-SR3 son coherentes con la garantía de no-fuga
de U1: `security-design.md` de `u1-budget-data` confirma que el error tipado sólo
lleva `status` + `path` (sin URL/query), con test que asevera la ausencia de
`championship_id`/token en **ambas** rutas (`NetworkError` y `DecodingError`).
SR2 encaja con `UserDefaultsActiveChampionshipStore` (clave
`futmondo_active_championship`, sólo un `String`); SR3 no abre canales nuevos —
toda la red pasa por U1 → `NetworkClient` de F1 (HTTPS forzado en el init). TS1
mantiene `Package.swift` sin dependencias; TS2 confina U2 al target `FutmondoApp`
bajo `#if canImport(SwiftUI)`; TS3 usa el Liquid Glass automático del `TabView`
nativo (coste 0 €). PR1/PR2 declaran los objetivos (60 fps, <100 ms) y PR3 es
honesto: observación en iPhone 13 Pro, no medible en WSL — no se presenta ninguna
métrica no verificable como verificada.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | construction/u2-budget-ui/nfr-requirements/security-requirements.md > SR1 | SR1 hereda la garantía de no-fuga de U1, pero el string que el usuario ve lo construye el propio `BudgetViewModel` al pasar a `error(String)` (ver functional-spec), y no hay ninguna aserción en U2 que confirme que ese string no interpola `championship_id` ni material de token. La garantía de U1 sólo cubre el error tipado de U1; la cobertura de UI se descarta explícitamente en TS2. | Dejar escrito en SR1 que el VM NO interpola el `championship_id` ni el token en el string mostrado (lo propaga verbatim desde el error tipado de U1), o exponer esa comprobación como lógica pura testeable en `FutmondoKit` para no depender de validación en dispositivo. | New |
| R-02 | Minor | construction/u2-budget-ui/nfr-requirements/performance-requirements.md > PR2 encabezado | El encabezado de PR2 cita `NFR4.2`, que no existe en `requirements.md` (NFR4 sólo define NFR4.1, que ya cubre scroll 60 fps y feedback <100 ms). `traceability.json` mapea PR1 y PR2 correctamente a NFR4.1, de modo que el único punto con la referencia colgante es la prosa del encabezado. | Corregir el encabezado de PR2 para citar `NFR4.1` (coherente con `traceability.json`), o añadir el sub-requisito NFR4.2 aguas arriba si se quiere separar scroll de feedback. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | N/A | Revisión por inspección cruzada de artefactos y contratos pasados. |

### Summary

Los requisitos de seguridad, rendimiento y stack de U2 son implementables y no
abren rutas de fuga de credenciales ni superficie de red nueva; los dos hallazgos
son Minor (asegurar por escrito/aserción que el VM no interpola el id en el error
mostrado, y una referencia colgante a `NFR4.2`). Sin Critical ni Major: READY.

**Verdict: READY**
