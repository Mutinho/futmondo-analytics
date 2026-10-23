## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T07:19:59Z
**Iteration:** 1

Revisión adversarial del Functional Design de `u2-budget-ui` (capa de
presentación SwiftUI en `FutmondoApp`). El diseño es, en general, sólido y
delgado: el `BudgetViewModel` sólo inyecta y consume los protocolos públicos de
U1 (`BudgetService`, `ChampionshipService`, `ActiveChampionshipStore`) más los
tipos puros `ActiveChampionshipResolver`/`TeamBudgetSort`/`MoneyFormatter`, sin
alcanzar las implementaciones `HTTP*` concretas; la propiedad de FR3.3 (persistir
vía `setActive` cuando el id resuelto difiere) es correcta y coincide con la
regla R5 de U1; `selectChampionship` (FR3.2) persiste y recarga; `setSort`
(FR2.1) reordena vía `TeamBudgetSort`; `BudgetRow` usa `MoneyFormatter` +
`DSColor.moneyPositive/Negative` con label VoiceOver compuesto (NFR5); el
alcance se respeta (sin pantalla de detalle, una sola pestaña). El bloqueo es un
hueco en la máquina de estados que obligaría a code-generation a adivinar.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md > BudgetViewModel (enum BudgetState) | El estado vacío colapsa en un único `case empty`, pero los mockups e interaction-spec definen DOS situaciones vacías con mensaje distinto: campeonato sin equipos ("Este campeonato no tiene equipos aún.") y usuario sin campeonatos ("No tienes campeonatos. Añádelos desde Futmondo."). Con un solo `empty` sin discriminador, code-generation tiene que adivinar qué mensaje renderizar en `BudgetView`. | Distinguir los dos casos vacíos (p. ej. `case emptyTeams` y `case noChampionships`, o un valor asociado que indique el mensaje), o especificar explícitamente de qué estado/señal deriva `BudgetView` cada texto vacío. | New |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md > BudgetViewModel (load()) | La descripción de `load()` encadena "carga campeonatos → resuelve activo → carga balances → loaded/empty/error", pero sólo ata explícitamente el error de la carga de balances. FR3.1/FR4.2 exigen que el fallo de AMBOS endpoints de campeonatos también vaya a `error` sin corromper el activo persistido; el spec no lo dice, dejando implícita la rama de error del leg de campeonatos. | Declarar explícitamente que un throw de `fetchChampionships()` enruta a `error(String)` sin alterar el id activo persistido (FR4.2), para no dejar la rama a inferencia. | New |
| R-03 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md > BudgetViewModel (setSort) | `setSort` se describe sólo como "reordena la lista cargada"; no se fija su comportamiento cuando el estado no es `loaded` (loading/empty/error). Es casi con certeza un no-op que guarda la clave, pero queda sin especificar. | Añadir una frase: `setSort` sólo reordena en `loaded`; en otros estados guarda `sortKey` sin reordenar (o es no-op). | New |
| R-04 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/traceability.json > elements[BudgetRow] | `BudgetRow` traza FR1.2 (los 9 campos de `TeamBudget`), pero la fila muestra sólo 4 (mockups.md difiere los 5 restantes al detalle fuera de alcance). El mapeo es correcto como refinamiento documentado, pero el `traceability.json` no refleja el diferimiento parcial, lo que puede leerse como cobertura completa de FR1.2 en la fila. | Anotar en la trazabilidad (o en el spec) que FR1.2 en la LISTA cubre 4 campos y el resto queda `Deferred` al detalle, para que la cobertura no se lea como total. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta unidad/stage) | N/A | Revisión por cross-reference manual contra los contratos públicos de U1 y los artefactos de inception pasados. |

### Summary

El diseño consume correctamente la superficie pública de U1 y respeta la
propiedad de FR3.3 y el alcance, pero la máquina de estados de `BudgetViewModel`
funde en un único `empty` dos situaciones vacías con mensajes y semántica de
selector distintos, lo que obliga a code-generation a adivinar: es el Major que
impide READY hasta que se discrimine.
