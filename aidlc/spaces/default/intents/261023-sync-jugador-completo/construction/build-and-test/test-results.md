# Test Results — Build and Test

## Build status

**Success.** Backend Python sin compilación; paquete importable; lint quirúrgico
limpio (`ruff check` sobre los 8 ficheros tocados → All checks passed, ruff 0.16.9).

## Test results

- **Suite completa** (`pytest --cov=app` desde `backend/`, `JWT_SECRET` efímero,
  `.venv-verify`): **463 passed, 3 xfailed (legacy), 0 failed**, 6.12 s.
  - Los 3 `xfailed` son legacy preexistentes (no de este intent).
  - Base previa 440 passed → **+23** nuevos.
- **Unit-scoped** (4 ficheros nuevos): **23 passed, 0 failed**.
- **Cobertura total: 60,82%** (`Required 27% reached`). Piso `--cov-fail-under=27`
  intacto. `favorites_read.py` 100%.

## Failure details

Ninguno.

## Target Verification Matrix (finalizada)

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| T-TESTS | código + conftest | suite verde | 463 passed, 0 failed | `pytest --cov=app` | build-and-test | **Met** |
| T-COV | pytest.ini / team.md | ≥ 27% (no bajar) | 60,82% | pytest-cov | build-and-test | **Met** |
| T-LINT | ruff.toml | `ruff check` limpio (ficheros tocados) | All checks passed | ruff 0.16.9 | build-and-test | **Met** |
| T-CONTRACT | BR4.2 / NFR1 | contrato 20 claves byte-identical | congelado por caracterización | `test_favorites_read_enriched.py`, `test_favorites_read_characterization.py` | build-and-test | **Met** |
| T-MIGRATION | BR2.1 / NFR6 | ALTER idempotente no destructivo | verificado (correr 2x sin fallo) | `test_schema_players_columns.py` | build-and-test | **Met** |
| T-EXTRACT | BR1.1 / BR1.2 | 6 campos extraídos + normalización NaN | verificado; SyncResult byte-identical | `test_sync_players_enrichment.py` | build-and-test | **Met** |
| T-SEC-CREDS | BR5.3 | sin credenciales en logs | aserción verde | `test_sync_players_enrichment.py` | build-and-test | **Met** |

Todos los targets aplicables en **Met**. Sin targets diferidos ni `Unverified`.
