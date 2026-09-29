# Code Summary — Oleada 2: extracción DDD de `assistant_service.py`

Intent `260929-assistant-god-file`, scope `refactor`, depth Minimal, unidad única
(zero-Unit). Metodología `test-after` con `characterization-first` por seam (BR
del proyecto). Sin cambio funcional: superficie pública `get_assistant_service()`
+ `ask()` intacta; el módulo viejo queda como shim de re-export.

## Orden de extracción (menor→mayor acoplamiento)

guardrails → `AssistantUsageTracker` → factual → ContextBuilder → LLM → `ask()`
orquestador + fachada + shim. Cada seam: test de caracterización verde contra el
código ACTUAL, luego extracción, luego el mismo test verde contra el extraído.

## Ficheros creados

- `backend/app/services/assistant/__init__.py` — re-exporta la fachada; documenta el layering.
- `backend/app/services/assistant/domain/guardrails.py` — `check_guardrails` + `ALLOWED_KEYWORDS`/`BLOCKED_PATTERNS`/`GUARDRAIL_RESPONSE`, puro (sin I/O) — BR1.1-BR1.2.
- `backend/app/services/assistant/domain/ports.py` — `AssistantReadPort`, `AssistantUsagePort`, `LLMPort` (Protocols, sin SQL, sin framework) — BR2.2.
- `backend/app/services/assistant/application/factual.py` — `FactualAnswers` + `FACTUAL_PATTERNS` sobre el read port; formateo verbatim, sin LLM — BR2.1.
- `backend/app/services/assistant/application/context.py` — `ContextBuilder` sobre el read port; degradación por-rama preservada — BR3.1-BR3.3.
- `backend/app/services/assistant/infrastructure/usage_adapter.py` — ÚNICO sitio con SQL de `assistant_usage` (incluye `CREATE TABLE IF NOT EXISTS`) — BR4.1-BR4.3, FR4.2/FR4.3.
- `backend/app/services/assistant/infrastructure/read_adapter.py` — ÚNICO sitio con SQL de lectura (identity, factual, contexto) + `save_market_today` con el SEGUNDO `CREATE TABLE market_today` (R-04); `db.adapt_params` + `?` — FR4.1/FR4.3, BR2.2/BR3.2.
- `backend/app/services/assistant/infrastructure/llm_adapter.py` — `LLMProviderAdapter` (Groq→Gemini fallback + `except Exception`, `str(e)[:80]` sin credenciales) — BR5.1-BR5.4.
- `backend/app/services/assistant/facade.py` — `AssistantService` (orquestador `ask()`, inyección por constructor `read=/usage=/llm=` con defaults de producción, OCP), `AssistantUsageTracker`, singleton `get_assistant_service()` — BR6.1.
- 6 ficheros de test (`test_assistant_{guardrails,usage,factual,context,llm,facade}.py`).

## Ficheros modificados

- `backend/app/services/assistant_service.py` — reducido a **shim de re-export** (1152 líneas eliminadas → 54). Re-exporta cada nombre histórico (`get_assistant_service`, `AssistantService`, `AssistantUsageTracker`, `SYSTEM_PROMPT`, `FACTUAL_PATTERNS`, `ALLOWED_KEYWORDS`, `BLOCKED_PATTERNS`, `GUARDRAIL_RESPONSE`, `_check_guardrails`, `MONTHLY_TOKEN_LIMIT`, `DAILY_REQUEST_LIMIT`, `get_db`). Preserva el import path usado por los endpoints (FR2.2).
- El plan de code-generation — checkboxes [ ]→[x] (única edición permitida).

## Ficheros NO tocados (preservados)

- `backend/app/api/v1/endpoints/assistant.py` y `market.py` — consumidores intactos (FR2.2/NFR1.3); `market.py` sigue llamando `get_assistant_service()._save_market_to_db(...)` sin cambios.
- Otros god-files (`data_manager_v2.py`, `data_sync_service.py`), la Oleada 1 (`analytics/`), `pytest.ini`, `ruff.toml`, `requirements.txt` — sin tocar.

## Decisiones clave

- **Seam de DB para caracterización**: los tests inyectan el `fake_db` de `conftest.py` parcheando `app.services.assistant.facade.get_db` (donde se resuelven los `db_factory` de los adaptadores). Es inyección en la frontera de DB, no monkeypatch de SQL (NFR4.1).
- **Inyección de ports en la fachada (OCP)**: `AssistantService(read=, usage=, llm=)` con defaults de producción, igual patrón que `analytics/facade.py`. Los tests de fachada usan stubs de los Protocols; los de caracterización siguen usando la ruta de producción con `fake_db`.
- **Degradación NO uniforme (R-03)**: caracterizada rama a rama — `_ctx_market_from_db` degrada a `""` (`except Exception`), `_ctx_standings` NO traga (una tabla ausente propaga). Ambas formas congeladas y preservadas.
- **Segundo `CREATE TABLE market_today` (R-04)**: el DDL en caliente dentro de `save_market_to_db` va también al adaptador de infraestructura (FR4.1/FR4.2).
- **R-02**: los tests de fachada aseveran que una respuesta factual NO invoca `can_make_request`/`record_usage` (cortocircuita antes de la cuota), congelando el orden observable.
- **Seguridad (BR5.4)**: el adaptador LLM sólo loguea `str(e)[:80]`; nunca material de credencial en excepciones/repr/exc_info. Tests aseveran ausencia de `api_key`/`token`/`password`/`secret` en la respuesta degradada.
- **Entorno**: Python del sistema 3.14 (no 3.12); venv efímero con `requirements.txt` filtrado (sin `libsql-experimental`), `JWT_SECRET` efímero de arranque (práctica aprendida).

## Deviations respecto al plan

- Ninguna material. Precisión: el `ask_stream` que el endpoint `/ask/stream` invoca **no existe** en el código fuente actual (bug latente preexistente); preservar la superficie EXACTAMENTE implica NO añadirlo — queda como deuda registrada (ver Issues del handoff y `traceability.json` reverse).

## Verificación

- Unit-scoped (desde `backend/`): `pytest tests/test_assistant_guardrails.py tests/test_assistant_usage.py tests/test_assistant_factual.py tests/test_assistant_context.py tests/test_assistant_llm.py tests/test_assistant_facade.py -q` → **26 passed**.
- Regresión completa: `pytest --cov=app -q` → **244 passed, 3 xfailed**, cobertura total **33.82%** (antes 29.75%) ≥ piso **27** (no tocado; trinquete sólo sube).
- `ruff format` + `ruff check --config ruff.toml` SÓLO sobre `app/services/assistant/` y los tests nuevos → **All checks passed!**. Ningún brownfield reformateado.
- Superficie pública verificada por import del path histórico: `ask`, `usage_tracker` (+ métodos), `_save_market_to_db`, `client`, `groq_client`, `_get_user_identity`, `_try_factual_answer`, `_build_context`, `_ctx_budget`, `_format_market_context` presentes.
