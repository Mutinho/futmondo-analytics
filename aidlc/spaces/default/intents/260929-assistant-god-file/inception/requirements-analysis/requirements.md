# Requirements — Oleada 2 god-files: descomposición de `assistant_service.py`

Intent: **Oleada 2 god-files (FR13, Intent 3 del backlog)** · Scope: `refactor` (Minimal) ·
Brownfield `futmondo-analytics` · Conversation language: Spanish.

## Análisis de intención

El objetivo es **reducir deuda técnica sin cambiar comportamiento observable**:
descomponer el god-file `backend/app/services/assistant_service.py` (~51 KB / 1158
líneas, cobertura directa CERO) al patrón DDD ya establecido y probado en la Oleada 1
(`backend/app/services/analytics/` y `prizes/`). La meta no es una feature nueva sino
**testabilidad y aislamiento del SQL**: convertir un módulo procedural con SQL embebido,
I/O de red (LLM) y lógica pura entremezclados en un paquete con fachada delgada, dominio
sin SQL (`Protocol`), aplicación pura y adaptadores de infraestructura como único sitio con
SQL crudo. El éxito se mide por **paridad de comportamiento** (superficie pública idéntica,
suite verde, cobertura que no retrocede), no por funcionalidad añadida.

Motivación de negocio: mantener el sistema en producción evolucionable a **coste 0 €**,
respetando el mandato afirmado de NO ampliar los god-files ni el patrón SQL-en-router, y
la política de cobertura de trinquete (solo sube).

## Requisitos funcionales

### FR1 — Preservación de la superficie pública (contrato intacto)
- **FR1.1** El paquete resultante DEBE seguir exponiendo el singleton
  `get_assistant_service()` y el método `async def ask(...)` con **firma y contrato de
  respuesta idénticos** a los actuales (consumidos por
  `backend/app/api/v1/endpoints/assistant.py`).
- **FR1.2** `backend/app/services/assistant_service.py` DEBE quedar como **shim de
  re-export** que re-exporta la fachada del nuevo paquete, de modo que el import histórico
  `from app.services.assistant_service import get_assistant_service` siga funcionando sin
  cambios en el endpoint (patrón `analytics_service.py`).
- **FR1.3** El comportamiento observable de `ask()` (guardrails → identidad/factual → LLM
  con fallback) DEBE preservarse exactamente, incluidos los modos de degradación.

### FR2 — Estructura del paquete `assistant/` (patrón Oleada 1)
- **FR2.1** Crear `backend/app/services/assistant/` con: `__init__.py` (re-exporta la
  fachada), `facade.py` (fachada delgada que preserva la superficie pública y solo delega,
  con inyección por constructor con default), `domain/ports.py` (`Protocol`(s) sin SQL ni
  framework), `application/` (lógica pura) e `infrastructure/` (adaptadores con SQL crudo).
- **FR2.2** `ask()` DEBE quedar como **orquestador delgado** que coordina los seams sin
  contener SQL crudo ni lógica de negocio embebida.

### FR3 — Extracción de los 4 seams
- **FR3.1 Guardrails** — Extraer `_check_guardrails` + `ALLOWED_KEYWORDS`/`BLOCKED_PATTERNS`/
  `GUARDRAIL_RESPONSE` a un **módulo puro** (solo regex/strings, sin I/O), comportamiento
  idéntico.
- **FR3.2 Capa factual** — Extraer `_try_factual_answer` + los handlers `_factual_*` +
  `FACTUAL_PATTERNS`; sus lecturas de datos pasan por el port de dominio, no por
  `cursor.execute` directo.
- **FR3.3 ContextBuilder** — Extraer `_build_context` + los métodos `_ctx_*` (que concentran
  la mayoría de los ~42 `cursor.execute`); toda lectura de datos pasa por el port.
- **FR3.4 AssistantUsageTracker** — Extraer la clase (tabla `assistant_usage`:
  `_ensure_table`, `can_make_request`, `record_usage`, `get_usage_summary`) como agregado
  con su persistencia detrás de un port/adaptador.

### FR4 — Aislamiento del SQL crudo y del esquema en caliente
- **FR4.1** Todo el SQL crudo (los ~42 `cursor.execute`) DEBE residir **exclusivamente** en
  los adaptadores de infraestructura del paquete, detrás de `Protocol`(s) de dominio sin SQL.
- **FR4.2** El `CREATE TABLE IF NOT EXISTS` idempotente (p. ej. `assistant_usage`) DEBE
  preservarse en el adaptador correspondiente, manteniendo intacto el comportamiento
  observable (creación en caliente); las migraciones explícitas de esquema quedan fuera de
  alcance (deuda registrada).
- **FR4.3** El adaptador DEBE usar el patrón de placeholders del proyecto
  (`db_connection.adapt_params` + `?`), como en `analytics/infrastructure/`.

### FR5 — Aislamiento de la integración LLM
- **FR5.1** La integración LLM (Groq `openai/gpt-oss-120b` con **fallback a Gemini**
  `google-genai`) DEBE aislarse tras un **port/adaptador de LLM**, preservando el orden de
  fallback y el modo de degradación (`except Exception` amplio que degrada, no rompe) exactos.
- **FR5.2** Los nombres de modelo hardcodeados se mantienen tal cual en el adaptador (sacarlos
  a configuración es deuda registrada, fuera de alcance).

### FR6 — Caracterización previa (characterization-first just-enough)
- **FR6.1** Antes de mover cada seam DEBE existir un test de **caracterización just-enough**
  que congele su comportamiento observable actual, usando los fakes in-memory de
  `backend/tests/conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`, `fake_db`), sin red, sin BD
  real y sin credenciales/tokens reales.
- **FR6.2** La caracterización DEBE cubrir explícitamente los **modos de degradación** de los
  `except Exception` alrededor de la llamada LLM y de las lecturas de mercado (el efecto
  observable: degradar/continuar, no romper), no solo el happy-path.

## Requisitos no funcionales

### NFR1 — Paridad de comportamiento (criterio de "hecho")
- **NFR1.1** La suite de tests existente DEBE permanecer **verde** tras el refactor
  (test-after; sin regresiones).
- **NFR1.2** La cobertura de línea backend NO DEBE bajar: el piso `--cov-fail-under`
  (hoy `27`) solo sube por trinquete; nunca se relaja para pasar el gate.
- **NFR1.3** Los tests de caracterización nuevos (FR6) DEBEN pasar sobre el paquete ya
  extraído, demostrando paridad de comportamiento.

### NFR2 — Gate de CI bloqueante y coste 0 €
- **NFR2.1** El cambio DEBE pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`)
  antes de fusionar a `main`; un rojo nunca llega a producción.
- **NFR2.2** El refactor NO DEBE introducir dependencias de pago; cualquier librería nueva
  (no se prevé ninguna; stdlib suficiente) sería OSS y fijada a versión exacta.

### NFR3 — Estilo e higiene de diff
- **NFR3.1** Identificadores, docstrings y comentarios en **inglés**; prosa de usuario
  (`HTTPException.detail`) en **castellano**.
- **NFR3.2** NO reformatear en masa (`ruff format`/Prettier) ficheros brownfield; formatear
  **solo** los ficheros nuevos del paquete o de forma quirúrgica. La reviewer corre
  `ruff check` (no `format`).

### NFR4 — Testabilidad por inyección
- **NFR4.1** La fachada y los seams DEBEN ser testeables inyectando dobles/stubs de los
  `Protocol`(s) por constructor (patrón OCP de `analytics/`), **sin monkeypatching** de SQL
  ni de red.

## Restricciones

- **C1** Prohibido ampliar los god-files existentes (`assistant_service.py`,
  `data_manager_v2.py`, `data_sync_service.py`, `photo_service.py`) o extender el patrón
  SQL-en-router; el código nuevo va tras una capa/función estrecha testeable. (Regla afirmada.)
- **C2** Coste 0 € — solo tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions
  free). (Regla afirmada.)
- **C3** No bajar ni relajar umbrales/pisos de cobertura para pasar el gate; el trinquete solo
  sube. (Regla afirmada.)
- **C4** Los tests usan dobles/fakes in-memory (`conftest.py`), sin red, sin BD real, sin
  credenciales/tokens reales (gitleaks escanea los tests). (Regla afirmada.)
- **C5** Formateo brownfield quirúrgico: nada de `ruff format`/`--fix` masivo. (Regla afirmada.)

## Supuestos

- **A1** La superficie pública consumida por el endpoint se limita a `get_assistant_service()`
  + `await service.ask(...)`; no hay otros consumidores del módulo. (Rationale: inventario del
  handoff de reverse-engineering; confirmar en el diseño con una búsqueda de imports.)
- **A2** Los fakes in-memory de `conftest.py` bastan para caracterizar las lecturas SQL del
  asistente sin BD real. (Rationale: patrón ya usado por la suite de caracterización existente.)
- **A3** El patrón de la Oleada 1 (`analytics/`) es aplicable 1:1 a `assistant/` (fachada +
  domain/ports + application + infrastructure + shim). (Rationale: seams análogos; validado en
  code-structure.md.)

## Fuera de alcance

- **OOS1** Los otros god-files (`data_manager_v2.py`, `data_sync_service.py`,
  `photo_service.py`) — no se tocan en esta oleada.
- **OOS2** Los `except: pass` de otros módulos — permanecen como **deuda registrada**.
- **OOS3** Cualquier **cambio funcional** del asistente (respuestas, prompts, modelos, lógica
  de negocio).
- **OOS4** El frontend Angular — no se toca (su única acción en otros intents es subir ratchet
  de cobertura, no aplica aquí).
- **OOS5** Migraciones explícitas de esquema — se preserva el `CREATE TABLE IF NOT EXISTS` en
  caliente (deuda registrada).
- **OOS6** Sacar los nombres de modelo LLM hardcodeados a configuración — deuda registrada.
- **OOS7** La persistencia de conversaciones (`assistant_conversations`) — vive en el
  **endpoint** (`assistant.py`), no en `assistant_service.py`; queda fuera del objetivo del
  refactor y no se relocaliza.

## Preguntas abiertas

- **OQ1** ¿Cuántos y qué `Protocol`(s) de dominio conviene definir — uno unificado
  (`AssistantDataPort`) o varios por seam (factual/context/usage)? (Se decide en Functional
  Design.)
- **OQ2** ¿El adaptador de datos del asistente puede reutilizar/compartir el adaptador de
  `analytics/` o debe ser propio? (Se decide en Functional Design.)
- **OQ3** Granularidad del port de LLM (un método `complete(prompt)` vs. exponer el fallback):
  se resuelve en diseño preservando el comportamiento de FR5.1.

## Sources

- `[desc]` Initial description: descripción autoritativa del intent
  (`aidlc engine workspace project-description`, source `project-description.json`).
- `[scope]` Workflow-selected scope: `refactor` (depth Minimal), de `aidlc-state.md`.
- `[Q1]`–`[Q6]` Respuestas del usuario en
  `requirements-analysis-questions.md` (todas = A) y su Consolidated Summary Confirmation
  (`Looks correct`).
- Reverse-engineering codekb (brownfield):
  `aidlc/spaces/default/codekb/futmondo-analytics/business-overview.md`,
  `architecture.md`, `code-structure.md` (seams, patrón Oleada 1, superficie pública).
- `[memory:M1]` Reglas afirmadas en `aidlc/spaces/default/memory/{project,team}.md`
  (NO ampliar god-files/SQL-en-router; coste 0 €; trinquete de cobertura; fakes in-memory;
  formateo quirúrgico; idioma código EN / usuario ES).

## Assumptions & Open Questions

Ver secciones **Supuestos** (A1–A3) y **Preguntas abiertas** (OQ1–OQ3) arriba. Ninguna
bloquea la generación de requisitos; todas se resuelven en Functional Design sin cambiar el
alcance aquí fijado.

None.
