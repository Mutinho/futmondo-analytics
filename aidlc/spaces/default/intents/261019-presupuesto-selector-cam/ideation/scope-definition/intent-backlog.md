# Intent Backlog — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (scope-definition). Idioma: castellano; tokens técnicos verbatim en inglés.
> MoSCoW sobre el alcance de ESTE intent.

## Must

| ID | Item |
|----|------|
| M1 | Pantalla de Presupuesto: lista nativa de equipos con las métricas de `TeamBudget` y tokens de dinero. |
| M2 | Selector de campeonato en navigation bar; cambio recarga + persiste en `UserDefaults`. |
| M3 | Capa de datos nativa (modelos `Codable` + llamadas a `balances`/`championships` reutilizando `NetworkClient`/auth de F1). |
| M4 | Formateo de dinero M/K con signo (lógica pura testeable en `FutmondoKit`). |
| M5 | Estados de carga y error de la pantalla. |
| M6 | Andamiaje de navegación: `TabView` nativo (Liquid Glass iOS 26, coste 0 €) con una sola pestaña "Presupuesto" + `NavigationStack`/`.toolbar` que aloja el selector. |

## Should

| ID | Item |
|----|------|
| S1 | Ordenación por las claves de la web vía control nativo. |

## Could

| ID | Item |
|----|------|
| C1 | Afinados visuales de fidelidad con la web (densidad, badges de rendimiento). |

## Won't (this intent — follow-up)

| ID | Item |
|----|------|
| W1 | Detalle de equipo (`budget-detail`) y diálogo de premios. |
| W2 | Pestañas/secciones adicionales del `TabView` y sus pantallas (el andamiaje de una pestaña sí entra, M6). |
| W3 | Otras pantallas (Mercado, Finanzas, Sync…). |
| W4 | Toggle tabla/cards. |

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/scope-definition/scope-document.md`.

## Assumptions & Open Questions

None.
