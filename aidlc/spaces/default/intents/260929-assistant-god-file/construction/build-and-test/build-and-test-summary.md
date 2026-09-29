# Build and Test Summary — refactor DDD de `assistant_service.py`

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), zero-Unit. Refactor sin cambio de
comportamiento observable; el objetivo es paridad (suite verde, cobertura que no baja, superficie
pública intacta), no funcionalidad nueva.

## Estado general del build y prerrequisitos

- **Build-ready**: sí. El paquete importa sin errores y el import histórico
  (`from app.services.assistant_service import get_assistant_service`) resuelve con `ask`,
  `usage_tracker` y `_save_market_to_db` presentes (NFR1.3).
- **Prerrequisitos**: Python 3.12 en CI; en local, venv efímero (coste 0) sin
  `libsql-experimental` + `JWT_SECRET` efímero. Sin dependencias nuevas.

## Inventario de tipos de test generados

| Tipo | Generado | Motivo |
|------|----------|--------|
| Unit (caracterización) | Ya existen (Code Generation) | 6 ficheros `test_assistant_*.py`, 26 tests |
| Integration | N/A | Estrategia Minimal; cross-seam cubierto por `test_assistant_facade.py` |
| Performance | N/A | Sin NFR de rendimiento; refactor sin cambio de comportamiento |
| Security | Cobertura mínima documentada | BR5.4 (sin credenciales en excepciones) + gitleaks en el gate + SQL parametrizado |

## Expectativas de cobertura

- Unidad única (zero-Unit): cada seam extraído (guardrails, usage, factual, context, LLM,
  fachada) tiene su test de caracterización. Cobertura de línea total **33.82%** ≥ piso **27**
  (`--cov-fail-under=27`, no tocado; trinquete solo sube).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| NFR1.1 | requirements.md > NFR1.1 | Suite verde, sin regresiones | 244 passed, 3 xfailed (preexistentes), 0 failed | `pytest --cov=app -q` | build-and-test | Met |
| NFR1.2 | requirements.md > NFR1.2 | Cobertura ≥ piso 27 | 33.82% | pytest-cov "Required test coverage of 27% reached" | build-and-test | Met |
| NFR1.3 | requirements.md > NFR1.3 | Caracterización verde + import histórico intacto | 26 passed; import OK | `pytest tests/test_assistant_*.py -q`; import check | build-and-test | Met |
| NFR2.1 | requirements.md > NFR2.1 | Gate CI bloqueante verde antes de `main` | pytest verde local; gitleaks/ng test en el gate | gate CI `ci.yml` | ci-pipeline / deployment-pipeline | Met (local verde; gitleaks + ng test los valida el gate) |
| NFR2.2 | requirements.md > NFR2.2 | Sin deps de pago; nuevas OSS + pin exacto | 0 deps nuevas; `requirements.txt` sin tocar | `source-manifest.json` | build-and-test | Met |
| NFR3.2 | requirements.md > NFR3.2 | Formateo solo de ficheros nuevos | `ruff check` limpio; sin reformateo brownfield | salida ruff "All checks passed!" | build-and-test | Met |
| NFR4.1 | requirements.md > NFR4.1 | Testable por inyección de `Protocol`s | stubs por constructor + `fake_db` | `test_assistant_facade.py` | build-and-test | Met |
| BR5.4 | rules.md > BR5.4 | Sin credenciales/tokens en excepciones | `str(e)[:80]`; test asevera ausencia de material de credencial | `test_assistant_llm.py` | build-and-test | Met |

## Evaluación de readiness

- **Build-ready**: sí. **Test-ready**: sí (suite verde, cobertura sobre el piso).
- **Deployment-ready**: sí a nivel de contenido; el release efectivo lo gobierna el gate de CI
  bloqueante (gitleaks + pytest + ng test) y el pipeline Fly.io on-merge — verificados en etapas
  de despliegue posteriores.

## Limitaciones conocidas / ítems pendientes

- **`ask_stream` ausente**: bug latente preexistente en el endpoint `/ask/stream` (no existe en el
  god-file original ni en el paquete); preservado sin fabricar (fuera de scope `refactor`),
  registrado `Deferred`. Recomendado un intent bugfix/feature separado.
- **gitleaks + `ng test`** no se ejecutan en este stage local (los ejerce el gate de CI en PR→`main`).
- **SAST/DAST dedicados** y paridad `--cov` en el job `verify`: deuda diferida, fuera de alcance.
