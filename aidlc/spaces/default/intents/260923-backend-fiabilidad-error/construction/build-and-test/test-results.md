# Test Results — Build and Test (FR3.2 + FR4)

Ejecución en venv efímero (Python 3.14 local excluyendo `libsql-experimental`;
CI usa 3.12), `JWT_SECRET` efímero, sin red, sin DB real, sin credenciales.
Coste 0 €.

## Build status

- **Verificación de build (imports)**: OK — `app.services.integration_errors` y
  `app.services.prizes.team_prizes_writer` importan sin error;
  `IntegrationRequestError` presente en la jerarquía. Backend Python interpretado
  (sin paso de compilación).

## Test results

- **Comando**: `cd backend && python -m pytest tests -q`
- **Total**: 206 · **Passed**: 203 · **Failed**: 0 · **xfailed**: 3 · **Skipped**: 0
- Los 3 `xfail` son los tests de characterization LEGACY de
  `test_futmondo_client_characterization.py` (comportamiento `None` silencioso),
  correctamente marcados `xfail` porque Step 3 (FR4.2) los reemplazó por
  excepciones tipadas — es la señal esperada de la migración, no un fallo.
- **Sin regresión**: baseline previa 186 passed; ahora 203 passed (+17 tests
  nuevos de U2), 0 fallos.

## Failure details

Ninguno.

## Coverage

- `--cov` observabilidad-only, **sin piso bloqueante** en este intent (ratcheting
  diferido). No se ejecuta como gate; no se relaja ningún umbral.

## Lint (advisory)

- `ruff check` de los ficheros nuevos: limpio.
- `ruff check app/services/futmondo_client.py` (brownfield mínimamente editado):
  5 findings `I` (orden de imports) — **advisory**, NO se corrigen con
  `ruff format`/`--fix` masivo (regla afirmada de no reformatear brownfield en
  masa). `E722` ya está fuera de `ignore` en `ruff.toml` (advisory por trinquete).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| NFR4-no-regresion | requirements.md NFR4 | suite existente en verde | 203 passed, 0 failed | `pytest tests -q` | build-and-test | Met |
| FR4.2-typed | requirements.md FR4.2 | `_make_request` lanza tipadas, no `None` | tipadas; 3 legacy xfail | `test_futmondo_client_typed_failures.py` | build-and-test | Met |
| FR4.4-degraded-fatal | requirements.md FR4.4 | recuperable→DEGRADED (no falla); fatal→propaga | verificado por efecto | `test_sync_integration_failure_effect.py` | build-and-test | Met |
| NFR2-no-corrupcion | requirements.md NFR2 | team_prizes todo-o-nada tras fallo | conjunto previo íntegro | `test_team_prizes_atomic_replacement.py` | build-and-test | Met |
| NFR3-no-credenciales | requirements.md NFR3 | sin password/token en excepción/log | aserción de ausencia | `test_futmondo_client_typed_failures.py` | build-and-test | Met |
| NFR1-log-estructurado | requirements.md NFR1 | log clave=valor WARNING/ERROR | helper `_log_integration_failure` | code-summary + test de efecto | build-and-test | Met |
| NFR-perf.1-timeout | nfr-design NFR-perf.1 | timeout acotado por petición | timeout→`IntegrationTimeoutError` | `test_futmondo_client_typed_failures.py` | build-and-test | Met |
| cov-floor-backend | team.md Testing Posture | sin piso bloqueante (observabilidad-only) | N/A (diferido por decisión) | pytest.ini/ci.yml | ci-pipeline | Met |

Todos los targets aplicables **Met**. Sin `Pending`/`Not Met`/`Unverified`.

## Loop-Back Log

(No aplica — la suite pasó a la primera; no se disparó ningún loop-back.)
