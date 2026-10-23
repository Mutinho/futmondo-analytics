# Initiative Brief — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (approval-handoff). Idioma: castellano; tokens técnicos verbatim en inglés.
> Cierre de Ideación; handoff a Inception.

## Resumen ejecutivo

Construir en SwiftUI (coste 0 €, sobre la librería de diseño de F1) la primera pantalla real tras el login — **Presupuesto** (saldos por equipo) — y un **selector de campeonato** nativo siempre accesible (menú en la navigation bar), con un andamiaje de navegación `TabView` de una sola pestaña (Liquid Glass iOS 26). Paridad funcional con la vista Angular `budget-overview`; sin cambios de backend.

## Alcance aprobado

- **In**: Presupuesto (lista nativa solo-lectura con métricas de `TeamBudget`, tokens de dinero, ordenación por las claves de la web, estados carga/error); selector en navigation bar (recarga + `UserDefaults`); capa de datos nativa reutilizando `NetworkClient`/auth de F1; andamiaje `TabView` 1-pestaña.
- **Out/follow-up**: detalle de equipo, diálogo de premios, pestañas/secciones adicionales, otras pantallas, toggle tabla/cards. Cero cambios de backend/infra/CI.

## Viabilidad y riesgos

Viable, sin bloqueantes. Riesgo dominante: patrón del selector sin sidebar (mitigado con menú en navigation bar, validable en dispositivo). Riesgo secundario: formateo de dinero M/K (lógica pura testeable).

## Restricciones durables

Coste 0 € (sólo SDK de Apple); tema Angular como fuente de verdad; sesión F1 intacta; verificación `swift test` + iPhone 13 Pro; gate de CI aplica; idioma (código EN, UI/commits ES).

## Findings advisory pendientes (para refined-mockups)

1. Fijar qué métricas de `TeamBudget` van en la lista vs. detalle diferido.
2. Añadir estado vacío (sin equipos / sin campeonatos / lista de selector vacía).
3. Extender accesibilidad a los estados de carga/error (anuncio VoiceOver, foco en Reintentar).

## Handoff a Inception

Siguiente fase: Reverse Engineering (brownfield) → Practices Discovery → Requirements → NFR → User Stories → Mockups refinados → Units/Delivery. La capa de código vive en `ios/` reutilizando `FutmondoKit`/`FutmondoApp` de F1.

## Sources

- Todos los artefactos de Ideación de este intent (`intent-statement`, `scope-document`, `intent-backlog`, `feasibility-assessment`, `constraint-register`, `raid-log`, `wireframes`, `user-flow`).

## Assumptions & Open Questions

None.
