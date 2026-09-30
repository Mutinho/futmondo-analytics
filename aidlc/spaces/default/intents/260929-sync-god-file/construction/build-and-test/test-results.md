# Test Results — Build and Test (sync god-file refactor)

Ejecución independiente por la QA lead en venv efímero (Python 3.14 local;
CI 3.12 es el gate autoritativo), workaround de coste 0 € (excluye
`libsql-experimental`, `JWT_SECRET` efímero). Comando: desde `backend/`,
`JWT_SECRET="…" python -m pytest -q --cov=app`.

## Estado del build

- **Éxito.** No hay build compilado (backend Python); la verificación es que la
  suite importa y corre. Dependencias instaladas sin `libsql-experimental` (no
  ejercitado por los tests).

## Resultados de test

- **Total: 251 passed, 3 xfailed** (0 failed, 0 errored). 11 warnings (filtradas).
- Los 3 `xfail` son legacy esperados de `test_futmondo_client_characterization.py`
  (deuda registrada de otro intent: reemplazo del `None` silencioso por excepción
  tipada), NO regresiones de este refactor.
- **Tests nuevos del dominio piloto**: `test_sync_match_odds_characterization.py`
  (7 tests) en verde, antes y después de la extracción (equivalencia estricta).

## Cobertura

- **Total: 34.56% ≥ piso `--cov-fail-under=27`.** "Required test coverage of 27%
  reached." El piso NO se relaja; solo sube por trinquete.
- Módulos nuevos al 100% de líneas: `sync/__init__.py`,
  `sync/match_odds/__init__.py`, `sync/match_odds/domain/ports.py`,
  `sync/match_odds/infrastructure/match_odds_adapter.py`,
  `sync/match_odds/orchestrator.py`.

## Lint

- `ruff check app/services/sync/ tests/test_sync_match_odds_characterization.py`
  → **All checks passed!** Sin `ruff format` masivo (solo ficheros nuevos).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| COV-BACKEND | `pytest.ini` `--cov-fail-under=27` | ≥ 27% line | 34.56% | `pytest --cov=app` output | build-and-test | Met |
| SUITE-GREEN | scope floor `refactor` | suite verde | 251 passed / 3 xfailed / 0 failed | pytest output | build-and-test | Met |
| EQUIV-MATCH_ODDS | FR5.1/FR5.1.1/BR3.2 | payload y clave `match_odds` idénticos | 7/7 caracterización verde pre y post | `test_sync_match_odds_characterization.py` | build-and-test | Met |
| LINT-NEW | NFR3 (`ruff check` limpio ficheros nuevos) | 0 findings | All checks passed | ruff output | build-and-test | Met |
| NO-GODFILE-GROWTH | NFR3/BR2.2 | `data_manager_v2.py` intacto | sin cambios (verificado en code-generation review) | git diff (review) | build-and-test | Met |

No hay targets `Pending`, `Not Met` ni `Unverified`. No aplica loop-back.
