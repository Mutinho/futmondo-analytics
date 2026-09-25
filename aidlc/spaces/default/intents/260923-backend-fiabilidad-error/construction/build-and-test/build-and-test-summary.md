# Build and Test Summary — Construction (FR3.2 + FR4)

## Estado general

- **Build**: OK (verificación por imports; Python interpretado, sin compilación).
- **Tests**: **203 passed, 0 failed, 3 xfailed** (los 3 xfail son characterization
  legacy esperados tras la migración FR4.2). Sin regresión (baseline 186).
- **Prerequisitos**: `JWT_SECRET` no-default; venv Python 3.12 (o efímero
  excluyendo `libsql-experimental` en local); sin red, sin DB real, sin credenciales.

## Inventario de tipos de test generados

| Tipo | Fichero | Aplicabilidad |
|---|---|---|
| Build | `build-instructions.md` | Aplica |
| Integración (Standard) | `integration-test-instructions.md` | Aplica (fronteras U1↔U2 + sync) |
| Rendimiento | `performance-test-instructions.md` | NO-APLICA (batch; sin load test) |
| Seguridad | `security-test-instructions.md` | Aplica parcial (NFR3 no-credenciales + gitleaks) |
| Cross-unit coverage | `cross-unit-traceability.md` | PASS |

## Cobertura por unidad

- **u1-error-layer**: capa de errores (jerarquía + endurecimiento 1ª oleada) — tests U1 en verde.
- **u2-integrations**: clientes tipados + captura sync + `team_prizes` atómico — 17 tests nuevos en verde.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| NFR4-no-regresion | requirements NFR4 | suite en verde | 203 passed, 0 failed | `pytest tests -q` | build-and-test | Met |
| FR4.2-typed | requirements FR4.2 | tipadas, no `None` | tipadas (3 legacy xfail) | `test_futmondo_client_typed_failures.py` | build-and-test | Met |
| FR4.4-degraded-fatal | requirements FR4.4 | recuperable→DEGRADED / fatal→propaga | verificado por efecto | `test_sync_integration_failure_effect.py` | build-and-test | Met |
| NFR2-no-corrupcion | requirements NFR2 | team_prizes todo-o-nada | conjunto previo íntegro | `test_team_prizes_atomic_replacement.py` | build-and-test | Met |
| NFR3-no-credenciales | requirements NFR3 | sin credenciales en excepción/log | aserción de ausencia | `test_futmondo_client_typed_failures.py` | build-and-test | Met |
| NFR1-log-estructurado | requirements NFR1 | log clave=valor WARNING/ERROR | `_log_integration_failure` | code-summary + test | build-and-test | Met |
| NFR-perf.1-timeout | nfr-design NFR-perf.1 | timeout acotado | timeout→`IntegrationTimeoutError` | `test_futmondo_client_typed_failures.py` | build-and-test | Met |
| cov-floor-backend | team.md Testing Posture | sin piso bloqueante (observabilidad-only) | N/A por decisión (ratcheting diferido) | pytest.ini/ci.yml | ci-pipeline | Met |

## Readiness

- **Build-ready**: sí.
- **Test-ready**: sí (suite en verde, cobertura cross-unit PASS).
- **Deployment-ready**: sí, tras el gate de CI (gitleaks + pytest + ng test) en
  `ci-pipeline` (siguiente etapa) y el pipeline Fly.io existente.

## Limitaciones / pendientes

- `ruff check` reporta 5 `I` (orden de imports) en `futmondo_client.py`
  (brownfield): **advisory**, NO se corrige con `ruff format`/`--fix` masivo
  (regla afirmada).
- Deuda registrada (fuera de alcance): llamadores `roster.py` de `_make_request`
  no migrados; `except: pass` de god-files → Intent 3; asimetría `--cov` en
  `verify` → deuda de pipeline.
- Observación menor de revisión (code-gen): `_make_request` conserva `timeout=15`
  escalar vs connect~5s/read~30s del diseño; endurecimiento opcional futuro.
