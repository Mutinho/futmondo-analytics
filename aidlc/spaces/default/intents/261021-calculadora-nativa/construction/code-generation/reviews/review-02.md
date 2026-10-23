## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-21T19:07:13Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| - | - | - | No findings | No action required | Resolved |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| `swift build --package-path ios` | PASS (exit 0, "Build complete!") | Compila limpio; los avisos `libxml2.so.2 ... no version information` son ruido del enlazador del toolchain en WSL, no diagnósticos del paquete. |
| `swift test --package-path ios` | PASS — 204 tests, 0 fallos ("All tests passed") | Confirma la afirmación del resumen (168 existentes + 36 nuevos); ninguna regresión en la suite. |

### Summary

Las cuatro revisiones de UX están aplicadas y son correctas, todas en la capa de vista SwiftUI sin tocar la lógica: (1) la fecha de venta es ahora un `ToolbarItem(.topBarLeading)` (`dateButton`) a la derecha de `sortMenu`, con `DSGlassIcon` `calendar`/`calendar.badge.clock` y un `.popover` con `DatePicker` gráfico acotado `in: Date()...` (FR4.1 preservada) más el reset "Hoy (quitar proyección)"; no queda card de proyección en el scroll y `daysAhead` lo sigue derivando el mismo `wholeDaysFromToday` → `viewModel.setDaysAhead`; (2) la píldora flotante `CalcSummaryPill` aparece vía `CalcScrollOffsetReader` (`onScrollGeometryChange` iOS 18+ / `GeometryReader` fallback) con un ÚNICO `Bool` `showCompactPill` que sólo conmuta al cruzar el umbral (sin re-evaluar el grid por frame) y el `PreferenceKey` legado usa `static let` (sin `static var`, apto Swift 6 device-strict); (3) el botón "Quitar selección" está eliminado del `countLabel` (sólo queda el texto de recuento y un `Spacer`); (4) `SellFloatingButton` es ya una píldora glass con hairline neón en `.overlay(alignment: .bottomTrailing)`, que sigue disparando la confirmación de venta (`action` → `confirmingSell`) y conserva `accessibilityIdentifier("calculator-sell-button")` y su label. Los invariantes de dinero (`CalculatorMath`) están intactos (activeBidsTotal siempre restado, profit nunca incluido, daysAhead clamped) y el build + los 204 tests siguen en verde.
