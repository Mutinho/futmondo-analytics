## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T15:40:43Z
**Iteration:** 2

Segundo pase adversarial (final) del Functional Design de `u1-budget-data` (library `FutmondoKit`, lógica pura testeable con `swift test` en WSL). Re-verifico los seis hallazgos abiertos de la iteración 1 contra los artefactos revisados. Los dos Major que bloqueaban READY están resueltos: `MoneyFormatter` es ahora determinista e independiente de locale, y la resolución del campeonato activo es una función pura de U1 con la propiedad de la persistencia asignada explícitamente a U2. Los cuatro Minor también quedan cerrados. Trazabilidad consistente: `SortKey` y `ActiveChampionshipResolver` figuran como elementos con sus FR. Sin Critical y sin Major abiertos.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | construction/u1-budget-data/functional-design/rules.md > R1 (MoneyFormatter) | La regla fija el separador decimal "el de la locale (coma en es)", pero la tabla de casos a testear espera literalmente `12,4M`/`−1,2M` y los tests corren en Linux/WSL, donde la locale por defecto no es `es` (suele dar punto). El contrato es ambiguo y los casos de `swift test` serían no deterministas o fallarían según el entorno. | Fijar en el contrato una locale/formato determinista para `MoneyFormatter` (p. ej. separador decimal `,` constante, independiente de la locale del runner), de modo que la tabla de casos sea reproducible en WSL. | Resolved (reviewer) |
| R-02 | Major | construction/u1-budget-data/functional-design/rules.md > R5 (ActiveChampionshipStore) | La regla de resolución del activo (activeId presente-y-en-lista → ese; presente-pero-no-en-lista o nil → primero; lista vacía → nil) se enuncia como "consumida por el VM en U2", pero la superficie pública de U1 sólo expone `activeId`/`setActive`: ninguna función de U1 implementa ni testea esa resolución, incluido el caso borde "activeId presente pero no en la lista". U2 tendría que reimplementarla adivinando (y no queda claro si debe auto-sanear el valor persistido obsoleto). | Añadir a U1 una función pura testeable que resuelva el campeonato activo contra la lista (devolviendo el id o `nil`), cubriendo los tres casos y decidiendo explícitamente si repersiste el id corregido; o declarar formalmente que la resolución es responsabilidad de U2 y moverla fuera de `rules.md` de U1. | Resolved (reviewer) |
| R-03 | Minor | construction/u1-budget-data/functional-design/rules.md > R1 (MoneyFormatter) | Interacción redondeo half-up ↔ "sin decimal si es entero" no definida en el borde: p. ej. `11.990.000` (→ 11,99 → redondea a 12,0 → ¿"12M" o "12,0M"?) y el half-up en negativos (`−1.250.000` → ¿`−1,2M` o `−1,3M`, hacia cero o alejándose). | Especificar el orden (redondear a 1 decimal y luego decidir entero) y la dirección del half-up en negativos, con un caso de tabla que lo fije. | Resolved (reviewer) |
| R-04 | Minor | construction/u1-budget-data/functional-design/rules.md > R1 y functional-spec.md > tabla de casos | El signo negativo se escribe con `−` (U+2212 MINUS SIGN) en toda la prosa, distinto del ASCII `-`. El contrato no dice qué glifo emite la función, así que un test podría afirmar contra el carácter equivocado. | Indicar explícitamente qué carácter de signo produce `MoneyFormatter` (U+2212 vs ASCII) para que las aserciones sean exactas. | Resolved (reviewer) |
| R-05 | Minor | construction/u1-budget-data/functional-design/traceability.json > elements | El tipo público `SortKey` (parte de la superficie de U1 y entrada de `TeamBudgetSort`) no aparece como elemento en `traceability.json`, aunque sí lo hacen el resto de tipos públicos. | Añadir `SortKey` a la trazabilidad (vinculado a FR2.1) o justificar su ausencia. | Resolved (reviewer) |
| R-06 | Minor | construction/u1-budget-data/functional-design/rules.md > R4 (ChampionshipService) | El fallback se dispara con "si lanza" (cualquier throw), lo que incluye errores de decodificación del primario, no sólo fallos de red. No es incorrecto, pero queda implícito. | Confirmar explícitamente que el fallback cubre cualquier error del primario (red y decode) o acotarlo a errores de transporte. | Resolved (reviewer) |

> R-01 Reviewer note: R1 fija separador decimal coma `,` constante (no de locale), signo ASCII `-` (U+002D) y redondeo half-away-from-zero por aritmética entera, sin `NumberFormatter`. La tabla de casos del spec es determinista y reproducible en WSL (`12,4M`, `8M`, `-1,3M`, `+3,1M`, etc.).

> R-02 Reviewer note: Añadido `ActiveChampionshipResolver.resolve(activeId:in:)` a la superficie pública de U1, puro y testeable, cubriendo los tres casos incluido activeId-presente-pero-no-en-lista → primero; la repersistencia del id resuelto se asigna formalmente al `BudgetViewModel` de U2.

> R-03 Reviewer note: R1 define el orden del borde: redondear a 1 decimal primero y luego decidir entero (`11.990.000` → 11,99 → 12,0 → `12M`); half-away-from-zero en negativos fijado con caso de tabla (`-1.250.000` → `-1,3M`).

> R-04 Reviewer note: R1 explicita que la función emite el carácter ASCII `-` (U+002D); la prosa usa `−` sólo por estética. Aserciones de test sin ambigüedad.

> R-05 Reviewer note: `traceability.json` incluye `SortKey` (FR2.1) y `ActiveChampionshipResolver` (FR3.2, FR3.3) como elementos.

> R-06 Reviewer note: R4 confirma que el fallback de `ChampionshipService` se dispara ante **cualquier** throw del primario (red, status no-2xx y fallo de decode) y propaga el error del fallback si ambos lanzan.

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada en el brief) | N/A | Verificación cruzada manual de artefactos (spec, rules, entities, traceability) y del review de iteración 1. |

### Summary

Los dos Major y los cuatro Minor de la iteración 1 están resueltos; el formato de dinero es determinista en WSL y la resolución del activo es una función pura de U1 con la propiedad de persistencia asignada a U2. Sin Critical ni Major abiertos: implementable sin guía arquitectónica adicional.

**Verdict: READY**
