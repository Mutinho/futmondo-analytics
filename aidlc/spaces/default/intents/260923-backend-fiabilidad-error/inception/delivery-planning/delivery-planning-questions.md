# Delivery Planning — Preguntas

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "FR3.2 + FR4, fiabilidad backend. Secuenciacion dependencia-primero: capa de errores -> clientes -> estado. Mantenedor unico, coste 0 EUR, walking skeleton OFF (sistema en produccion). Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Walking Skeleton`: "No se ejecuta ceremonia de walking skeleton para este intent (línea base OFF; el sistema ya está en producción)."

---

## Q1. ¿Qué construir primero?

Hay 2 unidades: U1 (capa de errores, base) → U2 (integraciones, depende de U1).

- A. **Por dependencia, U1 → U2** (un "Bolt" = una pasada de construcción sobre una pieza de trabajo que acaba en algo que corre): Bolt 1 = U1 (capa de errores caracterizada y endurecida), Bolt 2 = U2 (integraciones tipadas + estado + no-corrupción). Es el único orden que respeta el DAG y prioriza la base sobre la que se apoya el resto (y dentro de U2, primero los puntos de corrupción de datos = lo de mayor riesgo).
- B. Otra secuencia (indícala en Other).
- X. Other (please specify)

[Answer]: A. Por dependencia, U1 → U2: Bolt 1 = U1 (capa de errores caracterizada y endurecida), Bolt 2 = U2 (integraciones tipadas + estado + no-corrupción), priorizando dentro de U2 los puntos de corrupción de datos.

## Q2. ¿Modelo de puntuación formal (WSJF)?

- A. **No hace falta**: con 2 unidades y un DAG lineal, el orden es evidente por dependencia + riesgo; un modelo WSJF formal (puntuar valor/urgencia contra tamaño) sería overhead sin valor.
- B. Sí, puntuar con WSJF.
- X. Other (please specify)

[Answer]: A. No hace falta: con 2 unidades y DAG lineal, el orden es evidente por dependencia + riesgo; WSJF sería overhead sin valor.

## Q3. Tamaño de un Bolt

- A. **Un Bolt = una Unidad**: Bolt 1 = U1, Bolt 2 = U2. Coherente con la granularidad gruesa afirmada.
- B. Otro tamaño (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Un Bolt = una Unidad: Bolt 1 = U1, Bolt 2 = U2. Coherente con la granularidad gruesa afirmada.

## Q4. ¿Bolts en paralelo o en serie?

- A. **En serie**: U2 depende de U1, así que Bolt 2 va después de Bolt 1. Mantenedor único → sin paralelismo.
- B. Otra cosa.
- X. Other (please specify)

[Answer]: A. En serie: U2 depende de U1, así que Bolt 2 va después de Bolt 1. Mantenedor único, sin paralelismo.

## Q5. Dependencias externas que puedan bloquear

- A. **Ninguna que bloquee**: las APIs de Sofascore/Futmondo son dependencias en runtime (y los tests usan dobles, sin red); no hay hand-offs de otros equipos ni aprobaciones externas. Mapa de dependencias externas ligero/vacío.
- B. Hay una dependencia externa (indícala en Other).
- X. Other (please specify)

[Answer]: A. Ninguna que bloquee: las APIs de Sofascore/Futmondo son dependencias en runtime (tests con dobles, sin red); sin hand-offs ni aprobaciones externas. Mapa ligero/vacío.

## Q6. ¿Qué es lo que más te preocupa del build (para atacarlo pronto)?

- A. **El cambio de contrato de Futmondo (blast radius)**: por eso U2 empieza con el inventario de llamadores + caracterización antes de migrar, y prioriza los puntos de corrupción de datos.
- B. **La regresión al endurecer capturas de U1**: por eso U1 va characterization-first con el gate CI en verde en cada paso.
- C. **Ambas** (se atacan en el orden U1→U2 con characterization-first).
- X. Other (please specify)

[Answer]: C. Ambas: el cambio de contrato de Futmondo (blast radius) y la regresión al endurecer capturas de U1; se atacan en el orden U1→U2 con characterization-first (U2 empieza por el inventario+caracterización antes de migrar, priorizando corrupción).

## Q7. Staffing de construcción

- A. **Yo construyo todo aquí, una unidad a la vez, con tu aprobación** (mantenedor único, sin varios equipos). Modo de iteración por unidad o por etapa se decide abajo.
- B. Varios equipos (requiere ownership por unidad).
- X. Other (please specify)

[Answer]: A. Yo construyo todo aquí, una unidad a la vez, con tu aprobación (mantenedor único, sin varios equipos).

## Q8. Orden de iteración en construcción

Con 2 unidades dependientes y orden U1→U2, ¿prefieres diseñar y construir una unidad completa antes de la siguiente (unit-major, código funcionando antes), o correr cada etapa de diseño para ambas unidades y luego la siguiente etapa (stage-major, por defecto)?

- A. **Unit-major**: diseñar y construir U1 completa (funcional/nfr/código/tests), luego U2. Da código funcionando antes y coherencia por unidad; encaja con el orden dependencia-primero.
- B. **Stage-major (por defecto)**: cada etapa de diseño corre para ambas unidades, luego la siguiente etapa, con code-generation al final.
- X. Other (please specify)

[Answer]: A. Unit-major: diseñar y construir U1 completa (funcional/nfr/código/tests), luego U2. Código funcionando antes y coherencia por unidad; encaja con el orden dependencia-primero.

## Consolidated Summary Confirmation

Resumen del plan de entrega (antes de fijar los artefactos):

- **Secuencia (Q1=A)**: Bolt 1 = U1 (capa de errores), Bolt 2 = U2 (integraciones), priorizando corrupción dentro de U2. Respeta el DAG.
- **Sin WSJF (Q2=A)**; **un Bolt = una unidad (Q3=A)**; **en serie (Q4=A)**.
- **Sin dependencias externas bloqueantes (Q5=A)**: tests con dobles, sin red.
- **Riesgos a atacar pronto (Q6=C)**: contrato de Futmondo (inventario+caracterización antes de migrar) y regresión al endurecer (characterization-first U1).
- **Staffing (Q7=A)**: construcción aquí, una unidad a la vez, con tu aprobación.
- **Iteración (Q8=A)**: unit-major (U1 completa → U2). Gates por etapa en cascada al final de cada unidad; sin swarm autónomo.
- **Walking skeleton**: OFF (sistema en producción).
- **Verificación de fase Inception→Construction**: se consolidan las traceability.json (domain-design, units-generation) — se espera PASA.
- **Artefactos**: bolt-plan.md, team-allocation.md, risk-and-sequencing-rationale.md, external-dependency-map.md + phase-check-inception.md.

[Answer]: Looks correct
