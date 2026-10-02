# Test Results — `261001-sync-god-file-resto`

> Ejecución verificada de forma independiente por Build and Test (venv efímero,
> Python del sistema, `JWT_SECRET` efímero). Idioma: castellano.

## Estado del build

- Sin paso de compilación (Python). Verificación = suite de tests. **OK**.

## Resultados de tests

- `pytest tests/test_sync_clauses_characterization.py -q` → **8 passed** (0.05s).
  El test de caracterización de `clauses` pasa verde tras la extracción (y había
  pasado también contra el código previo a adelgazar — equivalencia probada).
- `pytest -q --cov=app --cov-fail-under=27` → **259 passed, 3 xfailed, 2 warnings**
  (4.57s).
  - Los 3 `xfailed` son preexistentes y esperados
    (`test_futmondo_client_characterization.py`, legacy `_make_request` None),
    no relacionados con este intent.
  - **0 failed, 0 errors.**
- Cobertura total: **35.73% ≥ piso 27%** (piso NO relajado). Cobertura del código
  nuevo: `clauses/orchestrator.py` 92%, `clauses/infrastructure/clauses_adapter.py`
  96%, `clauses/domain/ports.py` 100%.

## Detalle de fallos

Ninguno.

## Equivalencia / superficie

- `sync_all()` mantiene sus 10 claves literales en orden fijo; `clauses` en
  índice 2 (verificado por `test_sync_all_keeps_clauses_key_in_order`).
- `_run_sync_in_background` (router) intacto; firma de `sync_clauses` preservada.
- `data_manager_v2.py` sin cambios (adapter envuelve verbatim).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| NFR2.1 | requirements.md NFR2.1 | `--cov-fail-under=27` no relajado | 35.73% ≥ 27 | `pytest --cov-fail-under=27` → "Required test coverage of 27% reached" | build-and-test | Met |
| NFR2.2 | requirements.md NFR2.2 | gate CI (pytest) verde | 259 passed, 0 failed | suite run | build-and-test | Met |
| FR5.3 | requirements.md FR5.3 | `SyncResult` de clauses congelado | igual antes/después | 8 characterization tests passed | build-and-test | Met |
| FR5.1/FR5.2/FR5.4 | requirements.md | superficie pública + 10 claves + worker intactos | preservados | `test_sync_all_keeps_clauses_key_in_order`, suite verde | build-and-test | Met |
| FR7.3 | requirements.md FR7.3 | caracterización verde antes y después | sí | run previo (code-gen) + run actual | build-and-test | Met |
| NFR3.1 | requirements.md NFR3.1 | sin dependencias nuevas | `requirements.txt` sin cambios | diff | build-and-test | Met |

Todos los objetivos aplicables: **Met**. Sin `Pending` ni `Unverified`.
