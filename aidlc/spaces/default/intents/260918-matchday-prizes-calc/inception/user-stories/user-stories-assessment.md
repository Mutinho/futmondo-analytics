# User Stories — Assessment (matchday-prizes-calc)

## Decisión (recomendada)

**Skip** — con confirmación del usuario.

## Racional

El intent es una **corrección acotada de lógica de negocio** en un único punto:
el reparto del premio de ranking por jornada cuando hay equipos empatados a
puntos. Características que empujan a Skip (según la condición del stage):

- **No hay features nuevas de cara al usuario ni pantallas nuevas**: el frontend
  ya muestra las finanzas/premios leyendo `team_prizes`; no cambia la UI.
- **No hay personas nuevas ni múltiples personas**: el único actor es el usuario
  del campeonato que consulta sus finanzas; ya existe y no cambia su flujo.
- **La lógica, aunque de negocio, es una sola regla bien definida** y ya está
  capturada de forma testable en `requirements.md` (FR1–FR3, NFR1–NFR5) con
  criterios pass/fail y un ejemplo numérico concreto (jornada 5, campeonato
  `592416daa3a2dd871a7a9956`).
- **El trabajo es batch/interno** (`sync_prizes` en el camino de sync), no un
  workflow de usuario nuevo.

## Factores considerados

- Tipo de proyecto: brownfield, intervención acotada (scope `classic`).
- Alcance de cara al usuario: nulo en UI; solo cambian los importes calculados.
- Señales de complejidad: una regla de negocio (empate → suma de posiciones /
  N), con redondeo y aplicación retroactiva ya decididos.

## Cobertura alternativa si se salta

Los **requisitos** (`requirements.md`) ya son cobertura suficiente: cada FR/NFR
es verificable, trazable a la petición del usuario y al reverse-engineering, y
la fase de caracterización + tests del nuevo contrato (test-after) proveerá la
verificación conductual. No se pierde trazabilidad al saltar historias.

## Si el usuario prefiere ejecutar

Si se decide ejecutar, las historias aportarían valor sobre todo en explicitar
el criterio de aceptación del reparto ante 2 y 3 empatados (Given/When/Then)
como puente a los tests de caracterización.
