## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-10-19T13:56:33Z
**Iteration:** 1

Revisión advisory (1 pasada) de los mockups refinados de F2. Los cuatro
artefactos refinados (mockups, interaction-spec, design-system-mapping,
accessibility-checklist) son coherentes entre sí y trazables a los requisitos
y a las historias. Los findings advisory pendientes de las etapas previas
quedan resueltos:

- **rough-mockups #1 (qué métricas van en la lista vs diferido)**: resuelto —
  la sección "Métricas visibles" fija jerarquía primaria/secundaria (4 de 9) y
  declara explícitamente el resto como diferido al detalle.
- **rough-mockups #2 / user-stories #1 (estado vacío)**: resuelto — Pantalla 2
  distingue campeonato sin equipos (estado vacío, no error) y usuario sin
  campeonatos (mensaje + selector deshabilitado).
- **rough-mockups #3 / user-stories #3 (accesibilidad de carga/error)**:
  resuelto — Pantalla 3 + checklist especifican anuncio VoiceOver de carga y
  movimiento de foco a [Reintentar] en error.
- **user-stories (orden sólo descendente explícito)**: resuelto — FR2.1 e
  interaction-spec lo marcan como decisión, no omisión, con el toggle diferido.
- **user-stories (NFR4/NFR5 anclados a ítems verificables)**: resuelto — la
  accessibility-checklist ancla NFR5 (VoiceOver, Dynamic Type, contraste) y
  NFR4 (60 fps, <100 ms) a ítems por pantalla.

Sobre el tradeoff señalado (lista 4 de 9, DTO lleva 9): es un manejo
**coherente**, no una contradicción. FR1.2 pide los 9 campos "disponibles" y
su criterio de aceptación habla de presencia/mapeo en el DTO, no de renderizado
en fila; los mockups separan limpiamente "el DTO/mapeo lleva 9" de "la lista
muestra 4, resto a detalle". No bloquea.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/user-stories/stories.md > AC1.1 | AC1.1 sigue diciendo que la fila muestra los 9 campos, pero los mockups refinados ya deciden mostrar 4 en la lista y diferir 5 al detalle. Queda una incoherencia de trazabilidad entre la historia y el mockup. | Reajustar AC1.1 (o añadir una AC de detalle de equipo) para que la fila refleje las 4 métricas visibles y el detalle diferido lleve las 5 restantes, alineándola con los mockups refinados. | New |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/refined-mockups/mockups.md > "No en la fila (diferido a detalle)" | El detalle de equipo diferido que aloja las 5 métricas restantes (`team_value`, `total_spent`, `total_income`, ops) se menciona como follow-up pero no hay wireframe ni nota de alcance de esa pantalla. | Dejar constancia (nota de alcance o placeholder) de dónde viven esas 5 métricas, para que el diferido sea explícito y no una pérdida silenciosa de FR1.2. | New |
| R-03 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/refined-mockups/interaction-spec.md > "Ordenación" | El menú de orden lista 6 claves pero el mockup de la fila sólo muestra 4 métricas; ordenar por `team_value`/`total_spent`/`total_income` reordena por un valor no visible en la fila. | Nota breve que confirme que ordenar por una clave no visible es intencional (coherente con FR2.1) para evitar confusión en implementación. | New |

### Summary

Los mockups refinados están listos: coherentes, trazables y resuelven los
findings advisory previos. El único punto a vigilar es alinear AC1.1 con la
decisión de mostrar 4 de 9 en la lista; el resto son mejoras menores, no
bloqueantes.
