# Test Results — Build and Test

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), zero-Unit. Ejecutado con el venv
efímero de coste 0 (Python 3.14 local; `requirements.txt` sin `libsql-experimental`; `JWT_SECRET`
efímero de arranque).

## Estado del build

- **Import del paquete + import histórico**: OK. `from app.services.assistant_service import
  get_assistant_service` resuelve; `get_assistant_service()` expone `ask`, `usage_tracker` y
  `_save_market_to_db` (NFR1.3). Aviso preexistente benigno del fallback de pool de conexiones
  (`psycopg2 ... 'pool'`), no relacionado con el refactor.
- **Lint quirúrgico** (`ruff check app/services/assistant/`, ruff 0.14.0): **All checks passed!**
  Ningún fichero brownfield reformateado (NFR3.2).

## Resultados de tests

- **Unit-scoped** (`pytest tests/test_assistant_*.py -q`, desde `backend/`):
  **26 passed** (guardrails, usage, factual, context, llm, facade).
- **Suite completa** (`pytest --cov=app -q`, desde `backend/`):
  **244 passed, 3 xfailed, 0 failed, 0 errores**.
  - Los 3 `xfailed` son expected-failures **preexistentes** en
    `test_futmondo_client_characterization.py` (`*_LEGACY`), ajenos a este refactor. Sin
    regresiones (NFR1.1).
- **Cobertura de línea total**: **33.82%** ≥ piso `--cov-fail-under=27` → "Required test coverage
  of 27% reached." El piso NO se toca ni se relaja; el trinquete solo sube (NFR1.2).

## Detalle de fallos

- Ninguno. 0 tests fallidos, 0 errores de colección. (Los 3 xfailed son esperados y preexistentes.)

## Reporte de cobertura

- Cobertura total 33.82% (previa al refactor 29.75% según `code-summary.md`); sube por el
  paquete nuevo caracterizado. Piso 27 respetado.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| NFR1.1 | requirements.md > NFR1.1 | Suite existente verde, sin regresiones | 244 passed, 3 xfailed (preexistentes), 0 failed | `pytest --cov=app -q` | build-and-test | Met |
| NFR1.2 | requirements.md > NFR1.2 (piso `--cov-fail-under=27`) | Cobertura de línea backend no baja del piso 27 | 33.82% ≥ 27 | salida pytest-cov "Required test coverage of 27% reached" | build-and-test | Met |
| NFR1.3 | requirements.md > NFR1.3 | Los tests nuevos de caracterización pasan sobre el paquete extraído + import histórico intacto | 26 passed unit-scoped; import `get_assistant_service` OK con `ask`/`usage_tracker`/`_save_market_to_db` | `pytest tests/test_assistant_*.py -q`; import check | build-and-test | Met |
| NFR2.1 | requirements.md > NFR2.1 | Pasa el gate de CI bloqueante (gitleaks + pytest + ng test) antes de fusionar a `main` | pytest verde localmente; gitleaks/ng test los ejerce el gate de CI en PR→`main` | gate CI `ci.yml` job `quality` | ci-pipeline / deployment-pipeline | Met (parte local verde; gitleaks + ng test los valida el gate de CI) |
| NFR2.2 | requirements.md > NFR2.2 | Sin dependencias de pago; librería nueva OSS y pin exacto | 0 dependencias nuevas; `requirements.txt` sin tocar | `source-manifest.json` (not_touched); code-summary | build-and-test | Met |
| NFR3.2 | requirements.md > NFR3.2 | Solo ficheros nuevos formateados; reviewer corre `ruff check` (no format) | `ruff check app/services/assistant/` limpio; ningún brownfield reformateado | salida ruff "All checks passed!" | build-and-test | Met |
| NFR4.1 | requirements.md > NFR4.1 | Fachada y seams testeables por inyección de `Protocol`s, sin monkeypatch de SQL/red | tests de fachada usan stubs de ports por constructor; caracterización usa `fake_db` | `test_assistant_facade.py`; code-summary decisiones clave | build-and-test | Met |
| BR5.4 | rules.md > BR5.4 (seguridad) | Sin credenciales/tokens en excepciones del asistente | adaptador LLM loguea solo `str(e)[:80]`; test asevera ausencia de api_key/token/password/secret | `test_assistant_llm.py` | build-and-test | Met |

## Loop-Back Log

(Ninguno — la ejecución pasó en verde sin loop-back.)
