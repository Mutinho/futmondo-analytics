## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T07:22:26Z
**Iteration:** 2

Iteración 2 (final, adversarial) del Functional Design de `u2-budget-ui`. El
autor ha resuelto el Major y los tres Minor de la iteración 1 de forma
verificable y coherente entre `functional-spec.md`, `frontend-components.md` y
`traceability.json`. La máquina de estados ya discrimina los dos casos vacíos;
las ramas de error, el no-op de orden fuera de `loaded` y el diferimiento
parcial de FR1.2 quedan explícitos. El VM sigue siendo delgado sobre los
protocolos públicos de U1 y respeta la propiedad de FR3.3 y el alcance (sin
pantalla de detalle). No queda ningún hueco que obligue a code-generation a
adivinar.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md > BudgetViewModel (enum BudgetState) | El estado vacío colapsa en un único `case empty`, pero los mockups e interaction-spec definen DOS situaciones vacías con mensaje distinto: campeonato sin equipos ("Este campeonato no tiene equipos aún.") y usuario sin campeonatos ("No tienes campeonatos. Añádelos desde Futmondo."). Con un solo `empty` sin discriminador, code-generation tiene que adivinar qué mensaje renderizar en `BudgetView`. | Distinguir los dos casos vacíos (p. ej. `case emptyTeams` y `case noChampionships`, o un valor asociado que indique el mensaje), o especificar explícitamente de qué estado/señal deriva `BudgetView` cada texto vacío. | Resolved (reviewer) |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md > BudgetViewModel (load()) | La descripción de `load()` encadena "carga campeonatos → resuelve activo → carga balances → loaded/empty/error", pero sólo ata explícitamente el error de la carga de balances. FR3.1/FR4.2 exigen que el fallo de AMBOS endpoints de campeonatos también vaya a `error` sin corromper el activo persistido; el spec no lo dice, dejando implícita la rama de error del leg de campeonatos. | Declarar explícitamente que un throw de `fetchChampionships()` enruta a `error(String)` sin alterar el id activo persistido (FR4.2), para no dejar la rama a inferencia. | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md > BudgetViewModel (setSort) | `setSort` se describe sólo como "reordena la lista cargada"; no se fija su comportamiento cuando el estado no es `loaded` (loading/empty/error). Es casi con certeza un no-op que guarda la clave, pero queda sin especificar. | Añadir una frase: `setSort` sólo reordena en `loaded`; en otros estados guarda `sortKey` sin reordenar (o es no-op). | Resolved (reviewer) |
| R-04 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/traceability.json > elements[BudgetRow] | `BudgetRow` traza FR1.2 (los 9 campos de `TeamBudget`), pero la fila muestra sólo 4 (mockups.md difiere los 5 restantes al detalle fuera de alcance). El mapeo es correcto como refinamiento documentado, pero el `traceability.json` no refleja el diferimiento parcial, lo que puede leerse como cobertura completa de FR1.2 en la fila. | Anotar en la trazabilidad (o en el spec) que FR1.2 en la LISTA cubre 4 campos y el resto queda `Deferred` al detalle, para que la cobertura no se lea como total. | Resolved (reviewer) |

> R-01 Reviewer note: `BudgetState` ahora discrimina `emptyTeams` (campeonato activo sin equipos → "Este campeonato no tiene equipos aún.", selector habilitado) y `noChampionships` (lista vacía → "No tienes campeonatos.", selector deshabilitado); spec y frontend-components.md coinciden y `BudgetView`/`ChampionshipMenu` enrutan cada mensaje sin ambigüedad.

> R-02 Reviewer note: `load()` declara explícitamente que un throw de `fetchChampionships()` va a `error(String)` sin alterar el id activo persistido (FR4.2); también reflejado en el estado `error` de frontend-components.md.

> R-03 Reviewer note: `setSort` especifica que sólo reordena vía `TeamBudgetSort` cuando el estado es `loaded`; en otros estados guarda `sortKey` para la próxima carga, sin efecto visible.

> R-04 Reviewer note: `traceability.json` anota en `BudgetRow` que la fila muestra 4 campos de 9 y los restantes quedan diferidos al detalle fuera de alcance; FR1.2 se cumple por disponibilidad en el DTO, no por presencia en la fila.

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta unidad/stage) | N/A | Revisión por cross-reference manual contra los contratos públicos de U1 y los artefactos de inception pasados. |

### Summary

El diseño está listo para implementación: el Major de la máquina de estados y
los tres Minor de la iteración 1 están resueltos de forma consistente entre los
tres artefactos, sin Critical ni Major abiertos. **Verdict: READY**
