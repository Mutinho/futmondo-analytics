# Test Results — Build and Test

## Build status

**Success.** Backend Python sin paso de compilación; paquete nuevo importable;
lint quirúrgico limpio.

- Importabilidad: `import app.services.sync_read.favorites_read, market_read` OK.
- `ruff check` sobre los ficheros nuevos/tocados: **All checks passed!** (ruff 0.16.9).

## Test results

- **Suite completa** (`pytest --cov=app` desde `backend/`, `JWT_SECRET` efímero,
  `.venv-verify`): **440 passed, 3 xfailed, 0 failed**, 30 warnings, 4.90 s.
  - Los 3 `xfailed` son legacy preexistentes (`test_futmondo_client_characterization.py`,
    el contrato futuro FR4.2 de excepciones tipadas) — no introducidos por este intent.
- **Unit-scoped** (4 ficheros nuevos): **18 passed, 0 failed**.
- **Cobertura total: 60,76%** (`Required test coverage of 27% reached`). Piso
  `--cov-fail-under=27` **intacto** (no se bajó; baseline previo 58,30% → sube).
  - `app/services/sync_read/favorites_read.py` 94%; `market_read.py` 100%;
    `__init__.py` 100%.

## Failure details

Ninguno. 0 tests fallidos.

## Coverage report

Total 60,76% (líneas). La capa nueva queda ampliamente cubierta por sus tests
(happy-path + fallback sync-miss + degradación de pujas + ausencia de credenciales).

## Target Verification Matrix (finalizada)

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| T-TESTS | código + conftest | suite verde | 440 passed, 3 xfailed, 0 failed | `pytest --cov=app` | build-and-test | **Met** |
| T-COV | team.md / pytest.ini | ≥ `--cov-fail-under=27` (no bajar) | 60,76% | salida pytest-cov | build-and-test | **Met** |
| T-LINT | ruff.toml (gate CI) | `ruff check` limpio en ficheros nuevos | All checks passed | ruff 0.16.9 | build-and-test | **Met** |
| T-CONTRACT | BR6.1 / rules.md | contrato byte-identical | congelado por caracterización (3 tests verdes contra código sin tocar) | `test_favorites_read_characterization.py` | build-and-test | **Met** |
| T-SEC-CREDS | NFR5.4 | sin credenciales en logs | aserción explícita verde | `test_sync_read_endpoints.py` | build-and-test | **Met** |
| T-SEC-SQL | NFR5.3 | SQL parametrizado | verificado (adapt_params; IN-clause solo `?`) | lectura + tests capa | build-and-test | **Met** |
| T-PERF | NFR1.1/NFR1.2 | p95 < 0,5 s / < 0,8 s | pendiente de medir en entorno | método en performance-requirements.md | **performance-validation** | **Unverified** (diferido, con owning stage programado) |

## Nota sobre T-PERF

El target de rendimiento requiere un entorno desplegado/comparable y la stage
**Performance Validation** lo posee explícitamente (programada a continuación).
Queda `Unverified` en Build and Test por diseño; no contribuye al resultado de
esta stage pero tiene dueño programado — no es un `Unverified` sin dueño.
