# Resultados de Build and Test — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Estrategia: Minimal ·
> Ejecutado: 2026-09-12. Entorno: venv aislado Python 3.14 con deps de test
> (`fastapi`, `pytest`, `curl_cffi`, `psycopg2-binary`, etc.; sin
> `libsql-experimental`/Turso, no usado por los tests).

## Estado del build

- **py_compile** de los 4 ficheros tocados → **exit 0 (OK)**.
- Sin paso de compilación/bundling (backend Python interpretado).

## Resultados de tests

### Regresión dirigida del bug (unit-scoped)

Comando: `python -m pytest tests/test_sofascore_sync_characterization.py -ra`
(desde `backend/`).

- **Total: 13 · Passed: 13 · Failed: 0 · Skipped: 0.**

### Suite completa (no regresión — NFR4)

Comando: `python -m pytest tests -ra` (desde `backend/`).

- **Total: 54 · Passed: 51 · Failed: 3 · Skipped: 0.**

### Detalle de fallos

Los 3 fallos están **exclusivamente** en `tests/test_analytics_service.py`,
fichero NO tocado por este bugfix:

| Test | Error |
|---|---|
| `test_championship_trends` | `AttributeError: 'AnalyticsService' object has no attribute '_team_cache'` |
| `test_player_value_trend` | `KeyError: 'latest_price'` |
| `test_clause_network` | `AttributeError: ... '_team_cache'` (`analytics_service.py:57`) |

**Análisis de no-regresión:** los ficheros que este bugfix modificó/creó son
`constants.py`, `sofascore_client.py`, `sofascore_sync.py` y el nuevo
`test_sofascore_sync_characterization.py`. `git diff` confirma que
`analytics_service.py` y `test_analytics_service.py` están **idénticos a HEAD**
(sin cambios de este trabajo). Por tanto los 3 fallos son **preexistentes en el
baseline del repositorio**, no una regresión introducida por este cambio. El
bugfix no toca `AnalyticsService`.

## Cobertura

Cobertura como métrica informativa (sin piso bloqueante en scope bugfix, per
`pytest.ini`). La lógica del bug queda cubierta por la regresión dirigida
(13 tests).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| TC-METHODOLOGY | code-generation-plan.md → Testing Contract | methodology=test-after respetada | test-after (implementación + tests por capa) | code-summary.md; 13 tests test-after | build-and-test | Met |
| SUITE-GREEN-BUGFIX | code-generation-plan.md → obligations.scope_floor | Regresión dirigida del bug en verde | 13/13 passed | pytest test_sofascore_sync_characterization.py | build-and-test | Met |
| SUITE-NO-REGRESSION | org.md Testing Posture (bugfix); requirements NFR4 | Sin regresión introducida por el cambio | Sin regresión; 3 fallos preexistentes ajenos (analytics) | pytest tests (51 passed / 3 preexistentes) + git diff | build-and-test | Met |
| BUILD-OK | build-instructions.md | py_compile de ficheros tocados exit 0 | exit 0 | py_compile OK | build-and-test | Met |

Nota: no existen artefactos `nfr-requirements/` ni `nfr-design/` en este scope
bugfix (etapas no ejecutadas), por lo que la única fuente de targets medibles es
el Testing Contract aprobado y las obligaciones de scope. No hay targets
diferidos ni `Unverified`.

## Assessment de readiness

- **Build-ready:** sí. **Test-ready:** sí. **Deployment-ready:** sí (a reserva
  de los 3 fallos preexistentes de analytics, que son deuda previa ajena a este
  bugfix y no lo bloquean).

## Limitaciones / pendientes conocidos

- Los 3 fallos preexistentes en `test_analytics_service.py` (`_team_cache`,
  `latest_price`) son anteriores a este trabajo y quedan fuera de su alcance;
  conviene abrir un arreglo separado.
- La integridad concurrente (NFR1) se apoya en el aislamiento transaccional del
  motor; el test evidencia el orden DELETE→INSERT en una sola conexión, no una
  prueba de concurrencia real (aceptable para bugfix Minimal; hallazgo advisory
  R-04 del reviewer).
