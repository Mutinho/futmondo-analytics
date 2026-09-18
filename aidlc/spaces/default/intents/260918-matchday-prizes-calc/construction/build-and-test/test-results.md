# Build and Test — Resultados (matchday-prizes-calc)

## Resumen de ejecución

- **Backend `pytest`**: **150 passed**, 0 failed (venv efímero coste 0 €, `JWT_SECRET` de arranque efímero, excluyendo `libsql-experimental`).
- **Baseline previo**: 135 tests; +15 nuevos (8 caracterización + 7 nuevo contrato). Sin regresiones (NFR2).
- **Cobertura del código nuevo**: `app/services/prizes/calculator.py` = **98%** (1 línea sin cubrir). La lógica del reparto de premios y la regla de empate está cubierta.
- **Cobertura global**: 26% (referencia no-bloqueante; el resto es código brownfield preexistente sin tests, coherente con la postura afirmada; no hay `cov-fail-under` en el repo).
- **Lint (`ruff check`)** sobre los 4 archivos nuevos: **All checks passed**.
- **Escaneo de secretos (gitleaks)**: corre en CI (bloqueante en el gate de PR→`main`); no se introdujeron secretos (verificado por revisión: único literal es el `JWT_SECRET` de arranque efímero de test, no productivo).

## Detalle de tests del área de premios

| Test | Cubre |
|---|---|
| `test_prizes_characterization.py` (8) | points_prize, gating ronda completa, ranking flop/top, MVP, dream-team, pseudo-jornada negativa, `DELETE ... NOT IN` |
| `test_prizes_calculator.py` (7) | sin empate (no regresión), 2 empatados (jornada 5 = 1.500.000/1.500.000), independencia de orden, 3 empatados, gating no-premiable, 0 puntos, `users_to_rank` |

## Verificación de la mejora

El caso reportado (campeonato `592416daa3a2dd871a7a9956`, jornada 5) queda cubierto por un test que verifica el reparto equitativo 1.500.000/1.500.000 ante empate en posiciones 3ª/4ª (`ranking_mode = flop`).
