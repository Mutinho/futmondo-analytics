## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T09:31:05Z
**Iteration:** 2

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/functional-spec.md > Workflow W1 paso 1 y Equivalencia de revestimiento | La especificación coloca la card "centrada sobre el gradiente de splash (`DSColor.splashGradient`)" y lista `DSColor.splashGradient` como parte del login revestido, pero el login real de F1 (`ios/Sources/FutmondoApp/LoginView.swift`) NO tiene fondo de gradiente: su `body` es un `VStack` con logo, título y card sobre `.padding(24)` sin background. El gradiente de splash vive en otra superficie (sólo se comparte el logo vía `matchedGeometryEffect`). Añadir un fondo de gradiente al login es un cambio visual/de layout, no un revestimiento equivalente, y contradice el mandato "sin cambios de comportamiento". | Quitar el gradiente de splash del login revestido (el login no lo tenía) o, si se decide introducirlo, reclasificarlo explícitamente como cambio visual deliberado con su justificación y trazarlo a un requisito; no presentarlo como elemento "antes→después" equivalente. | Resolved (reviewer) |
| R-02 | Major | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/frontend-components.md > Jerarquía y Props/estado; functional-spec.md > Equivalencia (fila TextInputField) | La equivalencia mapea el campo de contraseña de F1 (que incluye su propio toggle de visibilidad `isPasswordVisible` con botón "ojo") a `TextInputField` de U1 como "secure + toggle". La API pública de U1 en contract-summary expone `TextInputField(label, text, icon, isSecure, errorMessage?)` — `isSecure: Bool` fijo, SIN parámetro ni afordancia de toggle de visibilidad. El componente de U1, tal como está contratado, no puede proveer el toggle, así que no puede reemplazar al campo de contraseña de F1 sin perder ese comportamiento. | Resolver el desajuste de contrato: o bien el toggle lo mantiene `LoginView` fuera de `TextInputField` (y la equivalencia deja de atribuir el toggle a U1), o bien se registra como gap de contrato contra U1 para que `TextInputField` exponga visibilidad conmutable; dejar la elección como "decisión de implementación en code-generation" oculta una API que hoy no existe. | Resolved (reviewer) |
| R-03 | Major | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/functional-spec.md > Máquina de estados | La máquina de estados se declara "heredada de AuthViewModel, sin cambios" pero no coincide con `AuthViewModel`: su enum real es `idle, typing, loading, error, success` y `markTypingIfNeeded()` transiciona `idle ↔ typing` al editar los campos. El diagrama omite por completo el estado `typing`. Siendo el functional-spec la fuente de verdad de workflows y máquinas de estado, documenta un modelo de estados inexacto del comportamiento que se dice preservar. | Corregir el diagrama para reflejar los estados reales de `AuthViewModel` (incluir `typing` y la transición por edición de campos), o declarar explícitamente que es una vista simplificada y no la máquina de estados completa de F1. | Resolved (reviewer) |
| R-04 | Minor | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/functional-spec.md > Workflow W1 paso 1 | W1 introduce un "subtítulo (`DSFont.body`)" que no existe en el login de F1 (`LoginView` sólo tiene logo + `Text("Futmondo Analytics")` como título + card). Es un elemento nuevo presentado como parte del revestimiento equivalente. | Eliminar el subtítulo del flujo de revestimiento o justificarlo como adición visual deliberada trazada a un requisito, no como equivalencia antes→después. | Resolved (reviewer) |
| R-05 | Minor | aidlc/spaces/default/intents/261018-design-system-nativo/construction/u2-login-theming/functional-design/traceability.json > upstream_ids | Los IDs `AC4.1.1/.2/.3` no se pueden verificar contra ningún artefacto upstream del pass-list (requirements.md usa FR6.1/FR6.2; el story-map referencia US4.1 pero no enumera criterios de aceptación AC4.1.x). Las filas N/A están justificadas y la unit es UI-only sin rules, pero la procedencia de los AC es incomprobable. | Confirmar que los `AC4.1.x` existen en el artefacto de user-stories/criterios de aceptación de US4.1 y, si procede, referenciarlo; en caso contrario alinear los upstream_ids con los IDs realmente definidos (FR6.x / US4.1). | Resolved (reviewer) |

> R-01 Reviewer note: Ya no se añade gradiente; LoginView.swift usa `.ultraThinMaterial` sin LinearGradient.

> R-02 Reviewer note: Toggle de visibilidad conservado del patrón de F1 (estado local `isPasswordVisible`); U1 `TextInputField` no expone toggle (coincide con contract-summary).

> R-03 Reviewer note: Máquina de estados incluye idle/typing/loading/error/success coincidiendo con AuthViewModel.

> R-04 Reviewer note: Sin subtítulo inventado.

> R-05 Reviewer note: traceability referencia FR6.1/FR6.2 enumerables.

### Summary

Todas las correcciones de la iteración 1 están aplicadas y verificadas contra el código real (LoginView.swift / AuthViewModel.swift) y el contrato de U1. Sin nuevos hallazgos.

READY
