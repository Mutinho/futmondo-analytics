# Resumen de Build and Test — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, test strategy Minimal, zero-Unit. Conversation language: Spanish.

## Estado general de build

**Build-ready.** El backend Python no tiene paso de compilación; el "build" verificable (import de `app.main` + suite `pytest`) pasa. Prerrequisitos: venv con `requirements.txt` y `JWT_SECRET` efímero (ver `build-instructions.md`). Coste 0 €.

## Inventario de tipos de test

| Tipo | Generado en esta etapa | Motivo |
|------|------------------------|--------|
| Unit / caracterización | No (cubierto por Code Generation) | Estrategia Minimal: los unit tests se generan por unidad en Code Generation. 16 tests en `tests/test_analytics_service.py`. |
| Integración | N/A | Minimal + refactor sin fronteras nuevas (ver `integration-test-instructions.md`). |
| Rendimiento | N/A | Sin NFR de rendimiento nuevos (ver `performance-test-instructions.md`). |
| Seguridad | N/A (gate existente vigente) | Sin superficie de ataque nueva; gitleaks/gate se re-ejecutan en CI (ver `security-test-instructions.md`). |

## Expectativas de cobertura

- Piso bloqueante backend: **27%** (line-only, `pytest.ini`). Medido: **29.75%**. El ratchet solo sube; el piso no se toca.
- Paquete nuevo `analytics/`: fachada/puerto/shim 100%, adaptador 75%.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| COV-FLOOR | `pytest.ini` `--cov-fail-under` | ≥ 27% | 29.75% | `test-results.md` (línea de cobertura pytest) | build-and-test | Met |
| SUITE-GREEN | gate de CI / NFR2 | suite verde | 218 passed, 0 failed | `test-results.md` | build-and-test | Met |
| BR1.1 | `rules.md` | payload público preservado | 11 caracterización verdes | `tests/test_analytics_service.py` | build-and-test | Met |
| BR1.2 | `rules.md` | repositorio ≡ SQL inline | 2 contrato adaptador verdes | `tests/test_analytics_service.py` | build-and-test | Met |
| NFR4/BR5.1 | `requirements.md` | sin dependencias nuevas | `requirements.txt` sin cambios | inspección git | build-and-test | Met |
| BR5.2 | `rules.md` | sin reformateo brownfield | ruff solo en `analytics/` | `test-results.md` (lint) | build-and-test | Met |

Sin filas `Pending` ni `Unverified`. No hay objetivo aplicable que use `N/A` (los N/A son de tipos de test no requeridos, no de objetivos medibles).

## Evaluación de readiness

- **Build-ready**: sí.
- **Test-ready**: sí (suite verde, cobertura sobre el piso).
- **Deployment-ready**: sí para el ámbito de la Oleada 1 (comportamiento preservado, gate verde). El despliegue formal lo gobierna la fase Operation.

## Limitaciones / pendientes

- Oleadas 2–4 (`assistant`, `sync`, `data_manager`) quedan fuera de esta oleada (FR1.1, BR4.1).
- Deuda registrada fuera de alcance: SQL-en-router preexistente del endpoint `championship/classification-full`; `except: pass` de los god-files.
- `FR3.1` (caracterización amplia de `data_manager`) es de la Oleada 4.
