# Requirements Analysis — Preguntas clarificadoras

Intent: **Oleada 2 god-files (FR13)** — descomponer `backend/app/services/assistant_service.py`
(~51 KB / 1158 líneas) al patrón DDD de la Oleada 1 (`analytics/`, `prizes/`),
preservando la superficie pública `get_assistant_service()` + `async ask(...)`.
Scope: `refactor` (Minimal). Brownfield, cobertura directa CERO del objetivo.

> Responde cada pregunta rellenando su `[Answer]:` con la letra elegida (o `X` + texto).
> Estas respuestas alimentan `requirements.md`. La superficie pública a preservar y
> el mandato characterization-first NO se re-preguntan (ya decididos en la descripción).

---

## Q1 — Frontera de extracción de seams (¿qué se mueve en este intent?)

El objetivo declara 4 seams: **guardrails** (módulo puro), **capa factual**
(`_try_factual_answer`/`_factual_*`), **ContextBuilder** (`_build_context`/`_ctx_*`,
la mayoría de los 42 `cursor.execute`) y **AssistantUsageTracker** (agregado con
tabla `assistant_usage`). ¿Qué alcance fijamos para esta oleada?

- A. Los 4 seams completos + `ask()` como orquestador delgado + `assistant_service.py`
  como shim de re-export (descomposición completa al patrón de la Oleada 1).
- B. Solo los seams sin I/O de red primero (guardrails + factual + ContextBuilder tras
  un data-port), dejando `AssistantUsageTracker` para una sub-oleada posterior.
- C. Solo guardrails + AssistantUsageTracker (los dos más aislados), dejando la capa
  factual y ContextBuilder como deuda registrada.
- D. Descomposición completa PERO sin crear el shim de re-export (actualizar el import
  del endpoint directamente al nuevo paquete).
- E. Un único seam de prueba (guardrails) como piloto del patrón antes de comprometer el resto.

[Answer]: A

X. Other (please specify)

---

## Q2 — Alcance de la caracterización (characterization-first just-enough)

La cobertura directa del objetivo es CERO y el mandato es congelar comportamiento
antes de mover. ¿Qué nivel de caracterización fijamos como requisito de este intent?

- A. Just-enough por seam: caracterizar el comportamiento observable de CADA seam
  (incluida la degradación de los `except Exception` alrededor de LLM y lecturas de
  mercado) justo antes de moverlo, con los fakes in-memory de `conftest.py`.
- B. Caracterizar solo la superficie pública `ask()` end-to-end (guardrails→factual→LLM
  con fallback) y confiar en ella para todos los seams.
- C. Caracterización exhaustiva de todo `assistant_service.py` antes de mover una sola línea.
- D. Solo caracterizar los seams con SQL/persistencia (ContextBuilder, AssistantUsageTracker);
  guardrails y factual se testean tras extraer.
- E. Sin caracterización previa; escribir tests nuevos sobre el paquete ya extraído.

[Answer]: A

X. Other (please specify)

---

## Q3 — Tratamiento del SQL crudo y las tablas creadas en caliente

`assistant_service.py` concentra ~42 `cursor.execute` (mayoría en ContextBuilder) y
crea tablas en caliente (`assistant_usage`, y el endpoint crea `assistant_conversations`;
`_save_market_to_db` crea `market_today`). ¿Cómo lo tratamos al reubicar?

- A. Todo el SQL crudo va SOLO al adaptador de infraestructura (patrón `analytics/`),
  detrás de un `Protocol` de dominio sin SQL; el `CREATE TABLE IF NOT EXISTS`
  idempotente se preserva en el adapter (comportamiento observable intacto).
- B. Igual que A, pero además introducir migraciones explícitas de esquema
  (eliminar el `CREATE TABLE IF NOT EXISTS` en caliente).
- C. Mantener el SQL donde está y solo mover la lógica pura; el SQL se migra en otra oleada.
- D. Consolidar los repositorios de contexto en un único adaptador compartido con `analytics/`.
- E. Extraer el SQL a funciones libres sin `Protocol` (más ligero que el patrón hexagonal).

[Answer]: A

X. Other (please specify)

---

## Q4 — Frontera del cliente LLM (Groq → Gemini) dentro del refactor

`ask()` llama a Groq (`openai/gpt-oss-120b`) con fallback a Gemini (`google-genai`),
rodeado de `except Exception` amplio; hay listas de modelo hardcodeadas. ¿Qué hacemos
con esa integración en ESTE intent?

- A. Aislarla tras un port/adaptador de LLM (como las integraciones de datos), preservando
  el fallback Groq→Gemini y el modo de degradación exactos; sin tocar los modelos hardcodeados.
- B. Igual que A + sacar los nombres de modelo hardcodeados a configuración.
- C. Dejar la llamada LLM dentro del orquestador `ask()` sin extraer (solo mover guardrails/
  factual/context/usage); el LLM queda como deuda registrada.
- D. Extraer solo el manejo de errores del LLM a una excepción tipada propagada, sin port.
- E. Reemplazar el fallback por un único proveedor (fuera de alcance de refactor).

[Answer]: A

X. Other (please specify)

---

## Q5 — Criterio de "hecho" del refactor (cómo se verifica sin cambiar comportamiento)

Siendo un refactor sin cambio de comportamiento observable, ¿cuál es el criterio de
aceptación que fijamos como requisito?

- A. Superficie pública idéntica (`get_assistant_service()` + `ask()` con misma firma y
  contrato de respuesta), suite existente verde, cobertura NO baja (piso `--cov-fail-under`
  solo sube), y los tests de caracterización nuevos pasan sobre el paquete extraído.
- B. Igual que A + paridad de gate PR↔push verificada (gitleaks + pytest + ng test).
- C. Solo "la suite existente sigue verde y el endpoint responde igual".
- D. Igual que A + una prueba de contrato explícita que compare respuestas antes/después
  para un conjunto de mensajes representativos.
- E. Métrica de reducción de tamaño del god-file (p. ej. `assistant_service.py` < 1 KB shim).

[Answer]: A

X. Other (please specify)

---

## Q6 — Fuera de alcance explícito (qué NO tocamos en esta oleada)

Para acotar el refactor, ¿qué confirmamos como explícitamente fuera de alcance?

- A. Los otros god-files (`data_manager_v2.py`, `data_sync_service.py`, `photo_service.py`),
  los `except: pass` como deuda registrada, cualquier cambio funcional del asistente,
  el frontend, y las migraciones de esquema (salvo lo que decida Q3).
- B. Igual que A pero SÍ incluir el saneamiento de los `except Exception` amplios del asistente.
- C. Igual que A pero SÍ incluir mejoras de rendimiento del ContextBuilder (menos queries).
- D. Solo excluir los otros god-files; todo lo demás del asistente es candidato.
- E. Excluir además la persistencia de conversaciones (`assistant_conversations`), que se
  queda en el endpoint tal cual.

[Answer]: A

X. Other (please specify)

---

## Consolidated Summary Confirmation

Resumen de las decisiones antes de generar `requirements.md`:

- **Q1 (frontera de seams)**: descomposición COMPLETA al patrón Oleada 1 — los 4 seams
  (guardrails, capa factual, ContextBuilder, AssistantUsageTracker) + `ask()` como
  orquestador delgado + `assistant_service.py` como shim de re-export.
- **Q2 (caracterización)**: characterization-first just-enough POR SEAM (incluida la
  degradación de los `except Exception` de LLM y lecturas de mercado), con los fakes
  in-memory de `conftest.py` (sin red, sin BD real, coste 0 €).
- **Q3 (SQL y tablas)**: todo el SQL crudo SOLO en el adaptador de infraestructura, tras
  un `Protocol` de dominio sin SQL; el `CREATE TABLE IF NOT EXISTS` idempotente se
  preserva en el adapter (comportamiento observable intacto); migraciones explícitas
  quedan como deuda registrada.
- **Q4 (cliente LLM)**: aislar la integración LLM tras un port/adaptador, preservando el
  fallback Groq→Gemini y el modo de degradación exactos; nombres de modelo hardcodeados
  intactos (a configuración = deuda registrada).
- **Q5 (criterio de hecho)**: superficie pública idéntica (`get_assistant_service()` +
  `ask()`), suite existente verde, cobertura NO baja (piso `--cov-fail-under` solo sube),
  y tests de caracterización nuevos verdes sobre el paquete extraído.
- **Q6 (fuera de alcance)**: otros god-files (`data_manager_v2.py`, `data_sync_service.py`,
  `photo_service.py`), `except: pass` como deuda registrada, cambios funcionales del
  asistente, frontend y migraciones de esquema. Nota: la creación de
  `assistant_conversations` vive en el endpoint (no en `assistant_service.py`), fuera del
  objetivo del refactor.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
