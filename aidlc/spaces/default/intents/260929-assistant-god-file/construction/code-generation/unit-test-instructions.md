# Unit Test Instructions — descomposición del asistente

Instrucciones de test para el refactor DDD de `assistant_service.py`. Estrategia **Minimal**,
metodología **test-after** con **characterization-first por seam**. Coste 0 €: sólo `pytest`
existente + fakes in-memory de `conftest.py`.

## Framework y configuración

- **Framework**: `pytest` + `pytest-cov` (ya en `backend/requirements.txt`), desde `backend/`.
- **Fixtures** (de `backend/tests/conftest.py`, sin red/BD real/credenciales):
  - `fake_db` — `_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:` con `adapt_params`.
  - `clean_jwt_env` — entorno JWT efímero de arranque.
- **Sin dependencias nuevas.** Cualquier doble de LLM/port se implementa en el propio test (stub de
  `Protocol`), no como paquete nuevo.

## Cómo correr los tests de ESTA unidad (comando exacto, unit-scoped)

Runnable ANTES del primer test de caracterización (Step 3 del plan). Desde `backend/`:

```bash
pytest tests/test_assistant_guardrails.py tests/test_assistant_usage.py tests/test_assistant_factual.py tests/test_assistant_context.py tests/test_assistant_llm.py tests/test_assistant_facade.py -q
```

(Equivalente por patrón: `pytest tests/test_assistant_*.py -q`.) **NO** usar un `pytest` de proyecto
completo como comando de unidad; Build and Test correrá la suite completa por separado.

Verificación previa (Step 2): confirmar que el runner arranca sin error de colección con
`pytest tests/test_assistant_guardrails.py -q` (aunque el fichero aún no exista, el runner debe estar
operativo con `conftest.py`).

## Cobertura

- **NO** se introduce piso de cobertura nuevo en este intent; el piso `--cov-fail-under=27` de
  `pytest.ini` **no se toca ni se relaja** (el trinquete solo sube).
- La suite existente debe permanecer **verde** tras el refactor (NFR1.1); la cobertura de línea backend
  **no debe bajar** (NFR1.2). Objetivo cualitativo: cubrir cada seam extraído con su test de
  caracterización (happy-path + ramas de degradación de LLM y de lecturas de contexto/mercado).

## Mocking / stubbing

- **Ports de dominio** (`AssistantReadPort`, `AssistantUsagePort`, `LLMPort`): inyectar un stub que
  implemente el `Protocol` por constructor de la fachada (patrón OCP de `analytics/`), **sin
  monkeypatching** de SQL ni de red (NFR4.1).
- **Datos**: usar `fake_db` para los adaptadores de infraestructura (lecturas de contexto/factual y
  persistencia de uso); el `CREATE TABLE IF NOT EXISTS` debe ejercitarse contra el fake.
- **LLM**: doble del `LLMPort` que simule Groq OK, Groq-falla→Gemini-OK, y ambos-fallan (para aseverar
  la degradación sin romper). **Nunca** llamar a un LLM real ni usar claves reales.

## Gestión de datos de test

- Datos sintéticos mínimos por seam (un usuario/campeonato ficticio), construidos en el propio test.
- Sin credenciales/tokens reales (gitleaks escanea los tests); usar valores fake evidentes.
- Cada test asevera el EFECTO observable (respuesta/estado/modo de degradación), nunca `assert True`
  ni specs espejo.
