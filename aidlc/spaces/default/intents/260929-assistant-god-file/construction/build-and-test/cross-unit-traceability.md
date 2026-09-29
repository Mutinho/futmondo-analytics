# Cross-Unit Traceability — Build and Test (gate de cobertura de etapa)

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), **zero-Unit**. No se ejecutó
Units Generation ni User Stories (por scope), así que no hay `AC` de tres segmentos que enumerar;
la trazabilidad se verifica contra los `FR`/`NFR` de `requirements.md` y el
`traceability.json` de Code Generation a nivel de etapa (`construction/code-generation/`).

## Veredicto: PASS

Todos los `FR` y `NFR` enumerados de `requirements.md` están cubiertos con status `OK` en el
`traceability.json` de Code Generation, con un fichero de implementación o de test existente por
cada uno. El único ítem no implementado (`ask_stream`) es un **bug latente preexistente** fuera
del alcance del refactor, registrado como `Deferred` (no es un `FR`/`NFR` de este intent).

## Cobertura por elemento

| ID | Estado | Stage/Unit dueño | Fichero destino |
|----|--------|------------------|-----------------|
| FR1.1 | OK | code-generation (stage-level) | `backend/app/services/assistant/facade.py` |
| FR1.2 | OK | code-generation | `backend/app/services/assistant_service.py` (shim) + `test_assistant_facade.py` |
| FR1.3 | OK | code-generation | facade `ask()` (orden observable preservado) |
| FR2.1 | OK | code-generation | paquete `backend/app/services/assistant/` (capas DDD) |
| FR2.2 | OK | code-generation | shim de re-export; endpoints sin tocar |
| FR3.1 | OK | code-generation | `domain/guardrails.py` |
| FR3.2 | OK | code-generation | `application/factual.py` |
| FR3.3 | OK | code-generation | `application/context.py` |
| FR3.4 | OK | code-generation | `facade.py::AssistantUsageTracker` + `infrastructure/usage_adapter.py` |
| FR4.1 | OK | code-generation | `infrastructure/read_adapter.py` (único sitio SQL de lectura) |
| FR4.2 | OK | code-generation | `infrastructure/usage_adapter.py` (`CREATE TABLE assistant_usage`) |
| FR4.3 | OK | code-generation | `read_adapter.save_market_today` + `usage_adapter._ensure_table` (2º DDL, R-04) |
| FR5.1 | OK | code-generation | `infrastructure/llm_adapter.py` (Groq→Gemini) |
| FR5.2 | OK | code-generation | `infrastructure/llm_adapter.py` (fallback encapsulado tras `LLMPort`) |
| FR6.1 | OK | code-generation | `facade.py::AssistantService.ask` (orden de orquestación) |
| FR6.2 | OK | code-generation | degradación por-rama contexto/LLM (BR3.3/BR5.3) |
| NFR1.1 | OK | build-and-test | suite verde: 244 passed, 3 xfailed |
| NFR1.2 | OK | build-and-test | cobertura 33.82% ≥ piso 27 |
| NFR1.3 | OK | build-and-test | endpoints importan `get_assistant_service` sin cambios |
| NFR2.1 | OK | ci-pipeline (gate) | SQL fuera de la fachada; pytest verde; gitleaks+ng test en el gate |
| NFR3.2 | OK | build-and-test | `ruff check` solo sobre el paquete nuevo; sin reformateo brownfield |
| NFR4.1 | OK | build-and-test | tests con stubs de ports + `fake_db`; sin monkeypatch, sin deps nuevas |

## Elementos sin cubrir

- Ninguno de los `FR`/`NFR` del intent queda sin cubrir.
- **Nota de deuda (no es un elemento del intent):** el endpoint `/ask/stream` invoca
  `service.ask_stream(...)`, inexistente en el god-file original — bug latente preexistente que
  el refactor preserva sin fabricar (fuera de scope `refactor`). Registrado `Deferred` en
  `traceability.json` (`reverse`). Se recomienda un intent bugfix/feature separado.
