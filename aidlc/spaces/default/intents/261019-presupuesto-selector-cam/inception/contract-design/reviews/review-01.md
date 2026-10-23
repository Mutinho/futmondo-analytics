## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T15:00:45Z
**Iteration:** 1

Pase final ADVISORY sobre el contract-design de F2 (`261019-presupuesto-selector-cam`). El objetivo es confirmar que el contrato es sólido, implementable y que la corrección de la nota de conteo/lista quedó internamente consistente. Verificado contra `components.md`, `unit-of-work.md` y el backend real en `codekb/.../api-documentation.md`.

**Consistencia de la corrección (resuelta).** La nota de §1 de `contract-summary.md` ahora dice "la fila muestra el `team_name` más **4 métricas** (`balance`, `performance`, `max_bid`, `prizes`)": conteo (4) y lista (4) coinciden, y concuerdan con `BudgetRow` en `components.md` ("4 métricas visibles") y con U2 en `unit-of-work.md` ("BudgetRow (4 métricas…)"). El `TeamBudget` queda fijado en **12 propiedades**, y esa lista coincide 1:1 con el `teams[]` del contrato real de `GET /api/v1/analytics/balances`. La fórmula `performance = team_value + balance - initial_budget` coincide verbatim con el backend. El mismatch anterior conteo/lista está cerrado.

**Solidez del contrato.** Grafo de dependencias acíclico (`RootTabView → BudgetView → BudgetViewModel → {BudgetService, ChampionshipService, ActiveChampionshipStore, TeamBudgetSort}`; `FutmondoKit` sin dependencia de SwiftUI). La superficie pública de U1 consumida por U2 está completa y la inyección por protocolo hace U2 testeable. El fallback `/api/v1/user/championships` → `/api/v1/championships` y el paso de `championship_id` como query param reproducen fielmente el contrato existente. Invariantes de seguridad (Bearer inyectado por `NetworkClient` de F1, sin exponer tokens), coste 0 € (sin dependencias nuevas) y "sin cambios de backend" se sostienen. Un desarrollador puede implementar U1 y U2 desde estos contratos sin consultar al arquitecto.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/components.md > tabla "Modelos (DTOs)" fila `TeamBudget` | La etiqueta sigue diciendo "los **9 campos**" pero enumera 12 entre paréntesis; diverge de las "12 propiedades" ya fijadas en contract-summary. Advisory, no bloquea. | Alinear la etiqueta a "12 campos" en construcción para dejar una única fuente de conteo. | New |
| R-02 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/contract-design/contract-summary.md > §2 `ActiveChampionshipStore` (`activeId: String?`) | El invariante de no-nulidad de `championship_id` antes de llamar a `/analytics/balances` no está explicitado; `activeId` es opcional y el backend tiene default, lo que puede enmascarar un estado sin selección. Advisory. | En construcción, definir el comportamiento cuando `activeId == nil` (p. ej. no disparar `fetchBalances` o estado `empty`). | New |
| R-03 | Minor | aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/components.md > `BudgetViewModel` / `ActiveChampionshipStore` (FR3.3) | No queda nombrado qué componente dispara el re-fetch de balances al cambiar el campeonato activo (owner de FR3.3). Advisory. | En construcción, fijar explícitamente al `BudgetViewModel` como owner del re-fetch tras `setActive(_:)`. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para este pase ADVISORY) | N/A | Verificación hecha por cross-reference manual de IDs, campos y contratos de backend. |

### Summary

El contract-design es sólido e implementable y la corrección de la nota de conteo/lista ("team_name + 4 métricas") quedó internamente consistente con `components.md`, `unit-of-work.md` y el backend real; los tres residuales (etiqueta "9 campos", invariante de `championship_id` no-nulo, owner del re-fetch FR3.3) son Minor advisory para construcción y no bloquean.

**Verdict: READY**
