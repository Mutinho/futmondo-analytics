# Decision Log — Ideación (App nativa iOS Swift + xtool)

> Registro de las decisiones tomadas durante la fase de ideación de este intent.

| ID | Decisión | Etapa | Fecha | Source |
|----|----------|-------|-------|--------|
| DEC-01 | El intent es análisis/planificación (no construcción); entregables = documentos. | intent-capture | 2026-10-16 | [desc] [Q3] |
| DEC-02 | iOS-only, uso personal, decisor único. | intent-capture | 2026-10-16 | [Q2] [Q7] |
| DEC-03 | Objetivo de éxito = go/no-go + viabilidad coste 0 € + comparativa de distribución + ruta por fases. | intent-capture | 2026-10-16 | [Q3] |
| DEC-04 | 5 funciones núcleo: Login, Mercado, Presupuesto, Favoritos, Calculadora. | intent-capture | 2026-10-16 | [Q6] |
| DEC-05 | Fuera: App Store pública, Android, cambios de backend; UI nativa dentro como portabilidad. | intent-capture | 2026-10-16 | [Q8] |
| DEC-06 | Ruta técnica = **Swift/SwiftUI nativo puro** + `xtool`; Angular como especificación de referencia, no código a migrar. | feasibility | 2026-10-16 | [QF1] |
| DEC-07 | `xtool` en Windows **vía WSL** (Swift 6.4 + usbmuxd + USB passthrough); WSL ya operativo. Documentación oficial verificada. | feasibility | 2026-10-16 | [QF2] [QF3b] |
| DEC-08 | Firma gratuita al máximo con Apple ID gratuito (caducidad ~7 días aceptada). | feasibility | 2026-10-16 | [QF3] |
| DEC-09 | Refresh token en **iOS Keychain**; posible ajuste mínimo de `/auth/refresh` como dependencia (D-01), sin tocar backend ahora. | feasibility | 2026-10-16 | [QF4] [memory:M2] |
| DEC-10 | Sin plazo; optimizar por esfuerzo razonable y aprendizaje. | feasibility | 2026-10-16 | [QF5] |
| DEC-11 | Veredicto preliminar: **GO condicionado** al spike `xtool` (R-01). | feasibility | 2026-10-16 | [QF2] |
| DEC-12 | Secuenciación **risk-first**: F0 spike + F1 Login antes de pantallas de datos. | scope-definition | 2026-10-16 | [QS1] |
| DEC-13 | MVP = Login + Presupuesto + Mercado. | scope-definition | 2026-10-16 | [QS2] |
| DEC-14 | MoSCoW: Must = Login+Mercado+Presupuesto; Should = Favoritos+Calculadora. | scope-definition | 2026-10-16 | [QS3] |
| DEC-15 | Push **fuera** (coste); widgets **documentados** como fast-follow, no v1. | scope-definition | 2026-10-16 | [QS4] |
| DEC-16 | Decisión final de la ideación: **GO condicionado** al spike F0. | approval-handoff | 2026-10-16 | [QA3] |

## Assumptions & Open Questions

- None.
