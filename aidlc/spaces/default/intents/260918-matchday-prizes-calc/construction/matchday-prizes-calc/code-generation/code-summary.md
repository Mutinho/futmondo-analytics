# Code Generation — Resumen (matchday-prizes-calc)

## Ficheros creados

- `backend/app/services/prizes/__init__.py` — API pública del paquete (re-export del calculator).
- `backend/app/services/prizes/calculator.py` — función pura `calculate_round_prizes` + dataclasses `PrizeConfig`, `RoundTeamEntry`, `TeamRoundPrize`. Sin I/O ni SQL. Reproduce la fórmula por posición (BR2.2) e implementa la regla de empate FR1/BR3.1/BR3.2 (agrupar por `round_points`, sumar `prize(pos)` de posiciones contiguas, repartir `round(sum/N)`; N=1 = `prize(p)` exacto, sin regresión). Gating BR1.2, elegibilidad BR2.1, `points_prize` siempre BR1.1. Naming `*_points`/`*_prize`.
- `backend/tests/test_prizes_characterization.py` — 8 tests que congelan el comportamiento actual de la producción del premio (fake determinista del cliente Futmondo + `fake_db`; `time.sleep` a no-op). Cubre todas las ramas: points_prize, gating, ranking flop/top, MVP, dream-team, pseudo-jornada negativa, `DELETE ... NOT IN`.
- `backend/tests/test_prizes_calculator.py` — 7 tests unitarios de la función pura: sin empate (no regresión), 2 empatados (ejemplo jornada 5 = 1.500.000/1.500.000), independencia del orden, 3 empatados, gating no-premiable, 0 puntos, límite `users_to_rank`.

## Ficheros modificados (en sitio)

- `backend/app/services/data_sync_service.py` — `sync_prizes` reducido a orquestador: materializa `RoundTeamEntry` desde el ranking de la API, invoca `calculate_round_prizes` y mapea cada `TeamRoundPrize` a la fila `team_prizes` (`display_position` → `position`). Mantiene ingesta (API) y persistencia (UPSERT `ON CONFLICT` + `DELETE ... NOT IN`). Diff neto -10 líneas (el god-file no engorda; NFR4).

## Decisiones de implementación

- Cálculo puro en `services/prizes/` con dataclasses; import estático a nivel de módulo.
- La regla de empate agrupa por `round_points` y reparte la suma de los premios de las posiciones contiguas del grupo entre N, con `round()` por parte (BR3.2). El reparto es independiente del orden que devuelva la API entre empatados.
- El test de caracterización de empates se actualizó de forma trazable (de congelar el bug a describir el reparto correcto), con comentario del cambio deliberado (Q3=C).

## Cobertura de tests

- Unit-scoped: 15 passed (`test_prizes_characterization.py` + `test_prizes_calculator.py`).
- Suite completa del backend: **150 passed**, sin regresiones (NFR2). Verificado de forma independiente en venv efímero coste 0 €.

## Desviaciones del plan

- Ninguna material. El ejemplo exacto de la jornada 5 (1.285.714/1.714.286 → 1.500.000) se codifica en `test_prizes_calculator.py`; el test de caracterización de empates usa una config más simple por claridad. Ambos verifican la misma regla.
- Findings ruff preexistentes en `data_sync_service.py` dejados intactos (no formatear masivo brownfield).
