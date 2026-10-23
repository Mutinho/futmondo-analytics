## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T15:37:34Z
**Iteration:** 1

Revisión adversarial del Functional Design de `u1-budget-data` (library `FutmondoKit`, lógica pura testeable con `swift test`). La superficie pública, los DTOs y el contrato con el backend están bien alineados con `contract-summary.md`: snake_case mapeado, opcionales para legacy, fallback de endpoints y propagación de `NetworkError` sin credenciales. Sin embargo, aparecen dos puntos que fuerzan a U2 a adivinar o rompen la testabilidad determinista prometida, y que como esta es la capa de datos de la que depende U2, se marcan como Major bloqueantes para un pase adversarial.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | construction/u1-budget-data/functional-design/rules.md > R1 (MoneyFormatter) | La regla fija el separador decimal "el de la locale (coma en es)", pero la tabla de casos a testear espera literalmente `12,4M`/`−1,2M` y los tests corren en Linux/WSL, donde la locale por defecto no es `es` (suele dar punto). El contrato es ambiguo y los casos de `swift test` serían no deterministas o fallarían según el entorno. | Fijar en el contrato una locale/formato determinista para `MoneyFormatter` (p. ej. separador decimal `,` constante, independiente de la locale del runner), de modo que la tabla de casos sea reproducible en WSL. | New |
| R-02 | Major | construction/u1-budget-data/functional-design/rules.md > R5 (ActiveChampionshipStore) | La regla de resolución del activo (activeId presente-y-en-lista → ese; presente-pero-no-en-lista o nil → primero; lista vacía → nil) se enuncia como "consumida por el VM en U2", pero la superficie pública de U1 sólo expone `activeId`/`setActive`: ninguna función de U1 implementa ni testea esa resolución, incluido el caso borde "activeId presente pero no en la lista". U2 tendría que reimplementarla adivinando (y no queda claro si debe auto-sanear el valor persistido obsoleto). | Añadir a U1 una función pura testeable que resuelva el campeonato activo contra la lista (devolviendo el id o `nil`), cubriendo los tres casos y decidiendo explícitamente si repersiste el id corregido; o declarar formalmente que la resolución es responsabilidad de U2 y moverla fuera de `rules.md` de U1. | New |
| R-03 | Minor | construction/u1-budget-data/functional-design/rules.md > R1 (MoneyFormatter) | Interacción redondeo half-up ↔ "sin decimal si es entero" no definida en el borde: p. ej. `11.990.000` (→ 11,99 → redondea a 12,0 → ¿"12M" o "12,0M"?) y el half-up en negativos (`−1.250.000` → ¿`−1,2M` o `−1,3M`, hacia cero o alejándose). | Especificar el orden (redondear a 1 decimal y luego decidir entero) y la dirección del half-up en negativos, con un caso de tabla que lo fije. | New |
| R-04 | Minor | construction/u1-budget-data/functional-design/rules.md > R1 y functional-spec.md > tabla de casos | El signo negativo se escribe con `−` (U+2212 MINUS SIGN) en toda la prosa, distinto del ASCII `-`. El contrato no dice qué glifo emite la función, así que un test podría afirmar contra el carácter equivocado. | Indicar explícitamente qué carácter de signo produce `MoneyFormatter` (U+2212 vs ASCII) para que las aserciones sean exactas. | New |
| R-05 | Minor | construction/u1-budget-data/functional-design/traceability.json > elements | El tipo público `SortKey` (parte de la superficie de U1 y entrada de `TeamBudgetSort`) no aparece como elemento en `traceability.json`, aunque sí lo hacen el resto de tipos públicos. | Añadir `SortKey` a la trazabilidad (vinculado a FR2.1) o justificar su ausencia. | New |
| R-06 | Minor | construction/u1-budget-data/functional-design/rules.md > R4 (ChampionshipService) | El fallback se dispara con "si lanza" (cualquier throw), lo que incluye errores de decodificación del primario, no sólo fallos de red. No es incorrecto, pero queda implícito. | Confirmar explícitamente que el fallback cubre cualquier error del primario (red y decode) o acotarlo a errores de transporte. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada en el brief) | N/A | Revisión basada en verificación cruzada manual de artefactos y contratos. |

### Summary

Los contratos de datos y de servicios casan con el backend y con `contract-summary.md`, pero el formato de dinero depende de la locale del runner (rompe la tabla determinista en WSL) y la regla de resolución del campeonato activo se enuncia sin una función de U1 que la implemente y testee, forzando a U2 a adivinar; ambos son Major y bloquean READY en este pase adversarial.

**Verdict: NOT-READY**
