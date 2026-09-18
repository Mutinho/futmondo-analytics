# Build and Test — Resumen (matchday-prizes-calc)

## Veredicto: PASS

La mejora del cálculo de premios de jornada ante empates está implementada,
verificada y sin regresiones.

## Qué se verificó

- **Tests**: 150 passed (135 baseline + 15 nuevos), 0 fallos. Cobertura del
  cálculo nuevo (`calculator.py`) = 98%.
- **Lint**: `ruff check` limpio en los 4 archivos nuevos.
- **Secretos**: sin secretos nuevos; gitleaks bloqueante en CI.
- **No regresión (NFR2)**: la suite completa del backend permanece en verde.

## Cumplimiento de la definición de "hecho" del intent

- `sync_prizes` pasó de **0 tests de producción** a caracterizado (todas las
  ramas) antes del cambio, y con tests del nuevo contrato después. ✓
- La fórmula se extrajo a una función pura testeable sin engordar el god-file. ✓
- La regla de empate (FR1) reparte equitativamente la suma de las posiciones
  contiguas del grupo; el caso de la jornada 5 da 1.500.000/1.500.000. ✓

## Deuda registrada (fuera de alcance)

- OQ1: reparto exacto del resto cuando `suma/N` no es entero (hoy `round()` por
  parte; se revisará si aparece un caso real).
- Paridad de `--cov` en el job `verify` (push→`main`): diferida a diseño de
  pipeline (Q5=A).
- Doble semántica de "puntos" e identidad por nombre en `player_finances`:
  documentadas como deuda, no tocadas (Q6=A).

## Nota de despliegue

El cambio se ejercita en el camino batch del cron de sync (`daily-sync`), no en
la ruta de lectura. Al desplegar y correr el próximo sync, las jornadas con
empates (incluida la 5 del campeonato de ejemplo) se recalculan y corrigen
retroactivamente (FR3.2).
