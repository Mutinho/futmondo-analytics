# Build and Test Summary — sync god-file refactor

## Estado general del build

- **Build-ready y test-ready.** Backend Python (sin build compilado); la suite
  importa y corre. Dependencias instalables (workaround coste 0 € para Python
  local ≠ 3.12: excluir `libsql-experimental`). `JWT_SECRET` efímero para tests.

## Inventario de tipos de test generados

Estrategia activa: **Minimal** (scope `refactor`). Según la etapa, Minimal no
genera ficheros de instrucciones de test adicionales; los tests
unitarios/caracterización se cubren por dominio en Code Generation.

- **Unit / characterization**: `test_sync_match_odds_characterization.py` (7 tests)
  — creado en Code Generation, ejecutado y verde aquí.
- **Integration / performance / security instructions**: NO APLICA a estrategia
  Minimal (ficheros marcadores con la decisión y justificación).
- Suite completa existente ejecutada como verificación de no-regresión.

## Expectativas de cobertura

- Piso backend `--cov-fail-under=27` (line-only), medido **34.56%** → **cumplido**.
- Módulos nuevos del dominio piloto al 100% de líneas.
- El piso solo sube por trinquete; no se relaja.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| COV-BACKEND | `pytest.ini` `--cov-fail-under=27` | ≥ 27% line | 34.56% | `pytest --cov=app` output (test-results.md) | build-and-test | Met |
| SUITE-GREEN | scope floor `refactor` | suite verde | 251 passed / 3 xfailed / 0 failed | pytest output | build-and-test | Met |
| EQUIV-MATCH_ODDS | FR5.1/FR5.1.1/BR3.2 | payload y clave `match_odds` idénticos | 7/7 caracterización verde pre y post extracción | `test_sync_match_odds_characterization.py` | build-and-test | Met |
| LINT-NEW | NFR3 (`ruff check` limpio ficheros nuevos) | 0 findings | All checks passed | ruff output | build-and-test | Met |
| NO-GODFILE-GROWTH | NFR3/BR2.2 | `data_manager_v2.py` intacto | sin cambios (git diff en review) | code-generation review record | build-and-test | Met |

Sin verdictos `Pending`, `Not Met` ni `Unverified`.

## Evaluación de readiness

- **deployment-ready** para el alcance de esta pasada (dominio piloto `match_odds`
  extraído; superficie pública y equivalencia preservadas; gate verde).
- **Alcance parcial declarado**: 9 dominios restantes en pasadas posteriores
  (ver `cross-unit-traceability.md`). No es un fallo; es el alcance secuenciado
  aprobado.

## Limitaciones / pendientes

- Verificación local en Python 3.14; CI en 3.12 es el gate autoritativo (riesgo
  residual bajo; dependencias completas instaladas y suite verde).
- Los `xfail` legacy de `test_futmondo_client_characterization.py` son deuda
  registrada de otro intent, no de este refactor.
