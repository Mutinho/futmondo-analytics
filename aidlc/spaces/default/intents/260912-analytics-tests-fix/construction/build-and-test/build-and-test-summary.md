# Resumen de Build and Test

## Estado general
- Build: N/A (bugfix de tests; no hay artefacto compilado del backend).
- Tests: **54 passed, 0 failed** (suite completa de pytest del backend).
- Readiness: **deployment-ready** — el gate de CI `verify` de `fly-deploy.yml`
  (pytest + ng test) queda desbloqueado por la parte de pytest.

## Inventario de tipos de test
- Unit / caracterización (pytest): ejecutados. Los 3 objetivo + resto en verde.
- Integration / performance / security: no generados (Test Strategy = Minimal;
  scope bugfix; no aplican a este arreglo).

## Prerrequisitos
- Python 3.12, `requirements.txt`, `JWT_SECRET` no vacío.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| NFR1 | requirements.md §NFR1 | pytest exit code 0 | 54 passed, 0 failed | `python -m pytest tests -q` | build-and-test | Met |
| FR1 (caches) | requirements.md §FR1 | test_championship_trends, test_clause_network en verde | ambos pasan | pytest | build-and-test | Met |
| FR2 (latest_price) | requirements.md §FR2 | test_player_value_trend en verde | pasa | pytest | build-and-test | Met |
| FR3 (suite intacta) | requirements.md §FR3 | resto de la suite en verde | 54/54 | pytest | build-and-test | Met |
| NFR2 (blast radius) | requirements.md §NFR2 | solo test_analytics_service.py modificado | 1 fichero | source-manifest.json | build-and-test | Met |

## Limitaciones conocidas
- `libsql-experimental` no compila en Python 3.14 local; se omitió para ejecutar
  (no requerida por estos tests). El CI usa 3.12, donde no aplica esta limitación.
- Warnings preexistentes (Starlette/httpx deprecation, JWT key length) ajenos al arreglo.
