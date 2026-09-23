# Resultados de build y test — Fiabilidad de la sync

> Conversation language: Spanish. Ejecución en contenedor `python:3.12`
> (coste 0 €), `JWT_SECRET` efímero no productivo, sin red ni BD reales.

## Estado del build

- **Éxito**. `python -m compileall app` sin errores de sintaxis; la app importa
  y arranca vía `TestClient` (cubierto por la suite). Backend puro, sin paso de
  bundling.

## Resultados de test

| Métrica | Valor |
|---|---|
| Total | 166 |
| Passed | 166 |
| Failed | 0 |
| Skipped | 0 |
| Warnings | 1 (`StarletteDeprecationWarning`, preexistente, ajena a la unidad) |

Comando (fuente de verdad):

```bash
docker run --rm -v "$PWD":/repo -w /repo/backend \
  -e JWT_SECRET=test-secret-not-default-000 -e PYTHONDONTWRITEBYTECODE=1 \
  python:3.12 bash -c "pip install --quiet -r requirements.txt; python -m pytest tests -ra -p no:cacheprovider"
```

Salida: `166 passed, 1 warning in ~4.2s`.

Tests nuevos de la unidad (subconjunto, incluidos en los 166):
`test_sync_step_status.py` (5), `test_sync_degraded_steps.py` (4),
`test_market_bid_sanity_cap.py` (4), `test_token_store_migrations.py` (3).

## Detalle de fallos

Ninguno. Suite completa en verde, sin regresión respecto a la línea base previa
(163) tras añadir los 3 tests de la unidad de esta ronda (166).

## Cobertura

Sin piso de cobertura bloqueante en backend (como hoy). Aserciones significativas
en todos los tests nuevos (estado, payload, status code, propagación); ningún
`assert True`.

## Matriz de verificación de targets

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| FR3.1 | requirements.md §FR3.1 | Paso non-critical que falla → `degraded` + `reason` + log; `done` conserva `done` | Cumplido | `test_sync_step_status.py`, `test_sync_degraded_steps.py` (9 tests verde) | build-and-test | Met |
| FR3.2 | requirements.md §FR3.2 | `except` recuperable/fatal acotado; fatal se propaga | Cumplido | `test_token_store_migrations.py` (3 verde: propagación + idempotencia) | build-and-test | Met |
| FR6 | requirements.md §FR6 | `price > PRICE_SANITY_CAP` → 422 antes de proxyar; `price<=0` intacto | Cumplido | `test_market_bid_sanity_cap.py` (4 verde) | build-and-test | Met |
| NFR1 | requirements.md §NFR1 | Estado de tarea fiel; fallo parcial no se reporta como éxito | Cumplido | `progress[step].status` distingue `done`/`degraded` (tests) | build-and-test | Met |
| NFR2 | requirements.md §NFR2 | Código nuevo tras función estrecha; god-files intactos | Cumplido | `git diff` aditivo; `data_sync_service.py`/`data_manager_v2.py` sin tocar | build-and-test | Met |
| NFR3 | requirements.md §NFR3 | Specs `pytest` significativas, sin `assert True` | Cumplido | 16 tests nuevos con aserciones reales | build-and-test | Met |
| NFR4 | requirements.md §NFR4 | Coste 0 € (solo `pytest`) | Cumplido | Ejecución en `python:3.12` free; sin herramientas de pago | build-and-test | Met |
| NFR5 | requirements.md §NFR5 | Validación de `price` reforzada en backend (defensa en profundidad) | Cumplido | `test_market_bid_sanity_cap.py` (422 + cliente no invocado) | build-and-test | Met |

Sin filas `Pending` ni `Unverified`. Todos los targets aplicables: **Met**.

## Loop-Back Log

(Sin entradas — no hubo loop-back a code-generation; el build y la suite
pasaron en el primer intento de esta etapa.)

## Sources

- `construction/sync-reliability/code-generation/{code-summary,unit-test-instructions,traceability}.json/.md`,
  `inception/requirements-analysis/requirements.md`.

## Assumptions & Open Questions

None.
