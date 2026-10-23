# Initiative Brief — F3 Mercado (app nativa iOS)

> Consolidación de la fase de Ideación para el handoff a Inception.

## Sources

- Ideación completa de F3: intent-statement, stakeholder-map, market-research
  (competitive-analysis / market-trends / build-vs-buy), feasibility
  (feasibility-assessment / constraint-register / raid-log), scope-definition
  (scope-document / intent-backlog), team-formation, rough-mockups (wireframes /
  user-flow).

## Qué construimos

La **pantalla de Mercado** de la app nativa iOS (SwiftUI), reproduciendo la vista
Angular, como **segunda pestaña** del `TabView` tras Presupuesto. Incluye
**lectura** (banner de usuario + cards de jugador + orden descendente),
**escritura** (pujar y cancelar, con validación y confirmación) y el **detalle
Sofascore** como sheet. Sin cambios de backend: consumo de `/api/v1/market/*`.

## Por qué

Lleva a nativo la pantalla de mayor valor accionable del producto (fichar con
datos: puja sugerida, Sofascore, titularidad, tendencia), cerrando el salto entre
consultar (F2) y actuar (pujar).

## Alcance (resumen MoSCoW)

- **Must**: 2ª pestaña, carga, banner, cards 1:1, orden descendente, pujar,
  cancelar.
- **Should**: detalle Sofascore (sheet), marca de favorito.
- **Could**: microinteracciones/hápticos.
- **Won't (este intent)**: tabla, Calculadora/Finanzas (= F4), pestañas extra,
  cambios de backend, distribución + asset catalog.

## Restricciones y riesgos (resumen)

- **Restricciones**: coste 0 € (SDK de Apple), tema Angular como fuente,
  credenciales en Keychain, idioma (inglés código / castellano usuario), iOS 26,
  WSL no compila SwiftUI (validación en dispositivo con `xtool`), sin `actool`.
- **Riesgos**: arm-only en WSL (R1), escritura con efecto económico real (R2),
  fallo/latencia de Sofascore (R3), deriva visual (R4) — con mitigaciones.

## Entrega

- Modelo F1/F2: conductor AI-DLC + sub-agente por etapa; construcción prevista en
  **2 unidades** (U1 datos en `FutmondoKit`, U2 UI en `FutmondoApp`); validación
  en dispositivo por el propietario.

## Estado de aprobación

- Ideación recorrida y aprobada etapa a etapa por el propietario; reviewers
  advisory READY en intent-statement y wireframes.
- **Listo para handoff a Inception** (Reverse Engineering → … → Units Generation).

## Assumptions & Open Questions

None.
