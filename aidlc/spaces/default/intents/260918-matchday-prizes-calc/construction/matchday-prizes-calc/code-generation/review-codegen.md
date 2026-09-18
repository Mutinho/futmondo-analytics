## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-09-18T11:20:08Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | backend/app/services/prizes/calculator.py > `calculate_round_prizes`, cálculo de `members` en el ramo `users_to_rank <= 0` | La extracción cambia la base del fallback sin empate: el código previo usaba `total_members = len(all_team_ids)` (equipos del standings) y el nuevo usa `len([e for e in entries if e.round_points > 0])` (activos de la ronda). Verificado que es **equivalente en comportamiento**: como los activos son un subconjunto del standings, `active_members = min(len(active_entries), members)` colapsa a `len(active_entries)` en ambos casos, y el tope `position <= members` no excluye a ningún activo en ninguna de las dos formas; los tests flop/top de caracterización (4 activos) lo confirman. No bloquea, pero la divergencia de fuente del dato no está anotada como cambio deliberado. | Añadir un comentario breve en `calculate_round_prizes` justificando que el fallback por activos preserva el `active_members` previo basado en `total_members`, para que un mantenedor futuro no lo lea como regresión silenciosa. | New |
| R-02 | Minor | backend/tests/test_prizes_calculator.py > `test_two_tied_teams_equal_split_jornada_5_example` | El ejemplo de jornada 5 (3ª=1.285.714 + 4ª=1.714.286 → 1.500.000/1.500.000) se codifica con `money_per_ranking=12M` y 7 activos (`total_pct=28`); aritmética verificada de forma independiente (`round(12M*3/28)=1285714`, `round(12M*4/28)=1714286`, suma=3.000.000, split=1.500.000). El test asegura los 1.500.000 pero no fija con una aserción los importes por posición 1.285.714/1.714.286 previos al reparto, que son la parte «reproduce la fórmula por posición». | Opcional: añadir una aserción sobre `_position_prize(3,...)`/`_position_prize(4,...)` o un comentario que ligue explícitamente los dos importes de origen al total repartido, para blindar la trazabilidad del ejemplo. | New |

### Criterios de aceptación (verificados)

- **(1) Pureza — cálculo sin I/O ni SQL**: `calculator.py` no importa DB, cliente API, `time`, ni ejecuta SQL; solo `dataclasses`/`typing`. La función es determinista sobre entradas ya materializadas. OK.
- **(2) Regla de empate (FR1/BR3.1/BR3.2)**: agrupa por `round_points`, suma `_position_prize(pos)` de las posiciones contiguas del grupo y reparte `round(sum/N)`; `N=1` colapsa al premio exacto de posición (sin regresión, FR1.3). El reparto es independiente del orden entre empatados (agrupa por valor de puntos, no por índice API), verificado por `test_two_tied_teams_split_is_order_independent`. OK.
- **(3) Ejemplo jornada 5 cubierto**: `test_two_tied_teams_equal_split_jornada_5_example` cubre 1.285.714+1.714.286 → 1.500.000/1.500.000. Aritmética confirmada. OK (ver R-02, no bloqueante).
- **(4) `sync_prizes` no gana lógica de cálculo (NFR4)**: el diff sustituye el bloque de cálculo inline por materialización de `RoundTeamEntry` + llamada a `calculate_round_prizes` + mapeo a fila; net -10 líneas. Mantiene ingesta (API) y persistencia (UPSERT + `DELETE ... NOT IN`). El god-file no engorda. OK.
- **(5) Caracterización cubre todas las ramas (Q2=A)**: `test_prizes_characterization.py` cubre `points_prize` siempre, gating `round_fully_played`, ranking flop y top, MVP, dream-team, pseudo-jornada negativa (0.5 → matchday -5) y `DELETE ... NOT IN`. El test de empates se actualizó de forma trazable (de congelar el bug a describir el reparto correcto) con comentario del cambio deliberado (Q3=C). OK.
- **(6) Sin secretos reintroducidos**: el único literal es `JWT_SECRET="test-secret-not-default-000"` en el arranque del test, exactamente el patrón no-default sancionado por NFR1.1; no es un secreto productivo. OK.
- **(7) Imports estáticos**: sin `__import__`/`importlib`; los imports en `calculator.py`, `__init__.py` y ambos tests son estáticos a nivel de módulo (el `os.environ.setdefault` antes del import de app en el test de caracterización es un pre-requisito de arranque, no un import dinámico). OK.

### Summary

Diseño e implementación sólidos e implementables: el cálculo puro está correctamente separado de ingesta y persistencia, la regla de empate es correcta y order-independent, y `sync_prizes` queda como orquestador sin engordar el god-file (NFR4). Cero Critical, cero Major; dos Minor de documentación/robustez de test, ninguno bloqueante. Veredicto advisory: READY.
