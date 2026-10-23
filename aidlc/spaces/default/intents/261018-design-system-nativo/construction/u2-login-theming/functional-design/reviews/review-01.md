## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T09:26:19Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/functional-spec.md > Workflow W1 paso 1 y Equivalencia de revestimiento | La especificación coloca la card "centrada sobre el gradiente de splash (`DSColor.splashGradient`)" y lista `DSColor.splashGradient` como parte del login revestido, pero el login real de F1 (`ios/Sources/FutmondoApp/LoginView.swift`) NO tiene fondo de gradiente: su `body` es un `VStack` con logo, título y card sobre `.padding(24)` sin background. El gradiente de splash vive en otra superficie (sólo se comparte el logo vía `matchedGeometryEffect`). Añadir un fondo de gradiente al login es un cambio visual/de layout, no un revestimiento equivalente, y contradice el mandato "sin cambios de comportamiento". | Quitar el gradiente de splash del login revestido (el login no lo tenía) o, si se decide introducirlo, reclasificarlo explícitamente como cambio visual deliberado con su justificación y trazarlo a un requisito; no presentarlo como elemento "antes→después" equivalente. | New |
| R-02 | Major | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/frontend-components.md > Jerarquía y Props/estado; functional-spec.md > Equivalencia (fila TextInputField) | La equivalencia mapea el campo de contraseña de F1 (que incluye su propio toggle de visibilidad `isPasswordVisible` con botón "ojo") a `TextInputField` de U1 como "secure + toggle". La API pública de U1 en contract-summary expone `TextInputField(label, text, icon, isSecure, errorMessage?)` — `isSecure: Bool` fijo, SIN parámetro ni afordancia de toggle de visibilidad. El componente de U1, tal como está contratado, no puede proveer el toggle, así que no puede reemplazar al campo de contraseña de F1 sin perder ese comportamiento. | Resolver el desajuste de contrato: o bien el toggle lo mantiene `LoginView` fuera de `TextInputField` (y la equivalencia deja de atribuir el toggle a U1), o bien se registra como gap de contrato contra U1 para que `TextInputField` exponga visibilidad conmutable; dejar la elección como "decisión de implementación en code-generation" oculta una API que hoy no existe. | New |
| R-03 | Major | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/functional-spec.md > Máquina de estados | La máquina de estados se declara "heredada de AuthViewModel, sin cambios" pero no coincide con `AuthViewModel`: su enum real es `idle, typing, loading, error, success` y `markTypingIfNeeded()` transiciona `idle ↔ typing` al editar los campos. El diagrama omite por completo el estado `typing`. Siendo el functional-spec la fuente de verdad de workflows y máquinas de estado, documenta un modelo de estados inexacto del comportamiento que se dice preservar. | Corregir el diagrama para reflejar los estados reales de `AuthViewModel` (incluir `typing` y la transición por edición de campos), o declarar explícitamente que es una vista simplificada y no la máquina de estados completa de F1. | New |
| R-04 | Minor | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/functional-spec.md > Workflow W1 paso 1 | W1 introduce un "subtítulo (`DSFont.body`)" que no existe en el login de F1 (`LoginView` sólo tiene logo + `Text("Futmondo Analytics")` como título + card). Es un elemento nuevo presentado como parte del revestimiento equivalente. | Eliminar el subtítulo del flujo de revestimiento o justificarlo como adición visual deliberada trazada a un requisito, no como equivalencia antes→después. | New |
| R-05 | Minor | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/traceability.json > upstream_ids | Los IDs `AC4.1.1/.2/.3` no se pueden verificar contra ningún artefacto upstream del pass-list (requirements.md usa FR6.1/FR6.2; el story-map referencia US4.1 pero no enumera criterios de aceptación AC4.1.x). Las filas N/A están justificadas y la unit es UI-only sin rules, pero la procedencia de los AC es incomprobable. | Confirmar que los `AC4.1.x` existen en el artefacto de user-stories/criterios de aceptación de US4.1 y, si procede, referenciarlo; en caso contrario alinear los upstream_ids con los IDs realmente definidos (FR6.x / US4.1). | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación delegada ejecutable en esta revisión) | — | La revisión se apoya en comprobación cruzada manual del functional-spec/frontend-components contra `contract-summary.md`, `components.md` y el código real de F1 (`LoginView.swift`, `AuthViewModel.swift`). |

### Summary

El revestimiento preserva correctamente la API pública de `LoginView` (`init(viewModel:logoNamespace:)`), no introduce API de red y respeta la disciplina de etapa de diseño; pero introduce un fondo de gradiente de splash y un subtítulo que el login de F1 no tiene (cambio de layout disfrazado de equivalencia), mapea el campo de contraseña con toggle a un `TextInputField` de U1 cuyo contrato no ofrece toggle, y documenta una máquina de estados que no coincide con `AuthViewModel`. Esos puntos deben resolverse antes de considerar implementable el revestimiento sin regresión.

NOT-READY
