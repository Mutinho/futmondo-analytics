## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19T22:14:36Z
**Iteration:** 1

Revisión adversarial del código generado de `u1-budget-data` contra el plan aprobado, `functional-spec.md`, `rules.md` (R1–R6) y `security-design.md` (SR1–SR4), más la reutilización correcta del `NetworkClient` de F1. Verifiqué los 11 fuentes de `Budget/` y los 6 ficheros de test del manifest, traza por traza en los puntos de riesgo. El código coincide con el plan y las specs; no encontré defectos bloqueantes.

Comprobaciones clave verificadas:

- **(a) MoneyFormatter determinista/locale-independiente** — Redondeo entero half-away-from-zero (`tenths = magnitude*10/divisor`, `+1` si `remainder*2 >= divisor`); un decimal sólo si la décima ≠ 0; separador `,` fijo; signo `-` ASCII (U+002D); `+` sólo con `signed:true`. Bordes trazados a mano y confirmados: `11_990_000 → 120 décimas → "12M"`; `-1_250_000 → 13 décimas → "-1,3M"` (y su simétrico `1_250_000 → "1,3M"`). `UInt(amount.magnitude)` evita el overflow de `abs(Int.min)`. Sin `NumberFormatter`/locale. Correcto.
- **(b) TeamBudgetSort** — Descendente (`left > right`), estable por desempate con `offset` de `enumerated()`, y no mutante (devuelve un array nuevo; entrada `let`/value-type). Tests cubren orden por cada `SortKey`, empates totales y parciales, inmutabilidad y vacío. Correcto.
- **(c) DTOs** — `TeamBudget` con 12 props wire + `id = teamId` + `ops = purchasesCount + salesCount` derivado (no wire) y `CodingKeys` snake_case; `Championship` con 5 core + 6 extras opcionales (legacy-tolerant); `BalancesResponse`/`ChampionshipsResponse` con snake_case. Correcto.
- **(d) ChampionshipService** — `catch` sobre CUALQUIER throw (el fake mapea decode a `.decoding` y el servicio lo relanza) → fallback; si ambos lanzan, propaga el error DEL fallback. Verificado en tests 2–5 (incluido primario decode-throw + fallback error). Correcto.
- **(e) No-fuga en errores** — Los servicios propagan el `NetworkError` tipado de F1 tal cual, sin construir strings con URL/query; `NetworkError` sólo lleva `Int`/`String` (nunca credenciales), y `.decoding` lleva `localizedDescription` de un `DecodingError` (ruta de tipo/clave, no payload). Aserciones de no-fuga para la ruta `NetworkError` (test 4) y la ruta `DecodingError` (test 5), más chequeo de ausencia de `bearer`/`token`. Correcto.
- **(f) ActiveChampionshipResolver + store** — 4 casos (match / `nil`→primero / desconocido→primero / vacío→`nil`), función pura sin efectos sobre `UserDefaults`; `UserDefaultsActiveChampionshipStore` persiste sólo un `String` bajo `futmondo_active_championship` (test 5 lo asevera con `raw is String`). Correcto.
- **(g) Sin nuevas dependencias** — El manifest no toca `Package.swift`; `Networking/`, `Auth/`, `DesignSystem/` sólo se consumen (`NetworkClient`/`APIRequest`/`NetworkError`/`HTTPMethod` usados como en F1, y el puente `Result`→`throws` respeta que `send` nunca lanza). Correcto.
- **(h) Tests** — 7/6/5/5/6/5+5 por componente, dentro del rango 5–8; happy-path + ≥2 bordes; todas las aserciones verifican efectos reales (valores decodificados, orden, estabilidad, persistencia, no-fuga, propagación tipada). No hay `assert true` ni specs espejo.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | ios/Sources/FutmondoKit/Budget/MoneyFormatter.swift > scaled(_:divisor:suffix:) | Un valor como 999.999 se formatea como `1000K` en lugar de `1M`, porque el bucket se elige por `magnitude` antes de redondear y el umbral `M` es `>= 1_000_000` exacto. Es coherente con R1 (y así lo fija el test `testThousandsBoundary`), pero produce una etiqueta de 4 cifras + `K` que la UI de U2 podría mostrar de forma poco natural. | Opcional: si el propietario prefiere colapsar `999,95K+` a `1M`, decidirlo explícitamente en R1 y fijar el caso; si no, dejar el comportamiento documentado tal cual (no bloquea). | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| swift build && swift test (reportado por code-summary) | PASS: 82 tests, 0 fallos (43 F1 + 39 U1) en WSL | No reejecutado por el revisor (sólo lectura); la verificación numérica de cobertura no aplica en WSL por aprendizaje durable del proyecto. La traza manual de los bordes de MoneyFormatter y del fallback concuerda con los resultados reportados. |

### Summary

El código implementa fielmente R1–R6 y SR1–SR4, reutiliza correctamente el transporte de F1 sin tocarlo ni añadir dependencias, y los tests aseveran efectos reales con cobertura de happy-path + bordes por componente. Sin hallazgos Critical ni Major; una única observación Minor no bloqueante sobre la etiqueta `1000K` en el borde del millón.
