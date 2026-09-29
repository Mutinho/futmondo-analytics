# Functional Design — Preguntas (unidad: assistant)

Diseño de la descomposición DDD de `assistant_service.py` al patrón Oleada 1.
Este es un refactor sin cambio de comportamiento observable; las preguntas resuelven las
**preguntas abiertas** de `requirements.md` (OQ1-OQ3) y afinan el modelo de seams.

> Responde cada `[Answer]:` con la letra elegida (o `X` + texto). Como es refactor, la
> superficie pública a preservar (`get_assistant_service()` + `ask()`) y el mandato
> characterization-first NO se re-preguntan (decididos en requisitos).

---

## Q1 — Granularidad de los `Protocol`(s) de dominio (resuelve OQ1)

Los seams factual, ContextBuilder y usage leen/escriben datos. ¿Cuántos ports de dominio
definimos?

- A. UN port unificado `AssistantDataPort` con todos los métodos de lectura de contexto/factual
  + un port separado `AssistantUsagePort` para el tracker (lectura vs. escritura de uso separadas).
- B. Un único port `AssistantDataPort` con TODO (contexto factual + uso) en una sola interfaz.
- C. Un port por seam: `FactualDataPort`, `ContextDataPort`, `UsagePort` (tres interfaces finas,
  ISP estricto).
- D. Dos ports por responsabilidad de datos: `AssistantReadPort` (factual + contexto, solo lectura)
  y `AssistantUsagePort` (uso, lectura+escritura).
- E. Sin `Protocol`; funciones de repositorio libres importadas por la aplicación.

[Answer]: D

X. Other (please specify)

---

## Q2 — Reutilización del adaptador de datos de `analytics/` (resuelve OQ2)

El asistente lee datos de campeonato que se solapan con lo que ya lee `analytics/`. ¿El
adaptador de infraestructura del asistente reutiliza el de `analytics/` o es propio?

- A. Adaptador PROPIO del asistente (`assistant/infrastructure/`), independiente del de
  `analytics/`; cada bounded context posee su acceso a datos (sin acoplamiento cruzado).
- B. Reutilizar el `AnalyticsDataPort`/adapter de `analytics/` donde el dato coincida, y añadir
  solo lo específico del asistente en un adaptador propio.
- C. Extraer un adaptador compartido común a ambos y que los dos contextos lo consuman.
- D. Reutilizar el `data_manager_v2` directamente (como hace hoy el god-file) desde el adapter.
- E. Indiferente; que lo decida code-generation.

[Answer]: A

X. Other (please specify)

---

## Q3 — Granularidad del port de LLM (resuelve OQ3)

`ask()` llama a Groq con fallback a Gemini. ¿Cómo modelamos el port de LLM?

- A. Un port `LLMPort` con un único método `complete(prompt, ...) -> str` que ENCAPSULA el
  fallback Groq→Gemini dentro del adaptador (la aplicación no conoce los proveedores).
- B. Un port que expone ambos proveedores y deja el orden de fallback en la aplicación/orquestador.
- C. Dos ports (`GroqPort`, `GeminiPort`) y el orquestador `ask()` compone el fallback.
- D. Sin port; mantener la llamada LLM inline en `ask()` (LLM como deuda registrada).
- E. Un port `LLMPort` con `complete()` + método para exponer el proveedor usado (observabilidad).

[Answer]: A

X. Other (please specify)

---

## Q4 — Modelo de entidad de `AssistantUsageTracker` (tabla `assistant_usage`)

El tracker gestiona cuota de uso por usuario con la tabla `assistant_usage`. En `entities.md`,
¿cómo lo modelamos?

- A. Como un agregado `AssistantUsage` (raíz) con atributos (user_id, championship_id, contador,
  ventana temporal), reglas de cuota como `BRx.y` y su persistencia tras `AssistantUsagePort`
  (el `CREATE TABLE IF NOT EXISTS` idempotente se preserva en el adapter).
- B. Como un value object sin identidad (solo un contador efímero), sin agregado.
- C. No modelar entidad; tratar el tracker como un servicio de infraestructura opaco.
- D. Como agregado pero además introducir migración explícita de esquema (fuera de alcance por OOS5 → descartar).
- E. Indiferente; que lo decida code-generation.

[Answer]: A

X. Other (please specify)

---

## Q5 — Orden de extracción de los seams (secuencia del refactor, characterization-first)

FR6 exige caracterizar cada seam antes de moverlo. ¿En qué orden extraemos?

- A. De menor a mayor acoplamiento: (1) guardrails (puro), (2) AssistantUsageTracker (aislado con
  tabla propia), (3) capa factual, (4) ContextBuilder (el más SQL-intensivo), (5) `ask()` orquestador
  + shim. Caracterizar just-enough justo antes de cada paso.
- B. Primero `ask()` end-to-end, luego desglosar hacia dentro (top-down).
- C. Primero los seams con SQL (ContextBuilder, factual, usage) y guardrails al final.
- D. Todo de una vez (big-bang), caracterizando el conjunto antes.
- E. Indiferente; que lo decida code-generation/delivery.

[Answer]: A

X. Other (please specify)

---

## Q6 — Aserción del criterio de paridad en la especificación funcional

`functional-spec.md` describe el workflow de `ask()`. Para asegurar paridad de comportamiento,
¿qué nivel de especificación de la máquina de estados/flujo fijamos?

- A. Especificar el flujo completo de `ask()` (guardrails→identidad/factual→context→LLM con
  fallback→persistencia en endpoint) como secuencia numerada + los modos de degradación observables
  de cada `except Exception`, de modo que los tests de caracterización aseveren cada rama.
- B. Solo el happy-path de `ask()` sin las ramas de degradación (más ligero).
- C. Solo un diagrama de secuencia sin especificar los modos de fallo.
- D. Igual que A + una tabla explícita entrada→salida por cada handler factual.
- E. Indiferente; que lo decida code-generation.

[Answer]: A

X. Other (please specify)

---

## Consolidated Summary Confirmation

Resumen de las decisiones de diseño antes de generar los artefactos:

- **Q1 (ports de dominio)**: DOS ports por responsabilidad — `AssistantReadPort` (factual +
  contexto, solo lectura) y `AssistantUsagePort` (uso, lectura+escritura). Consumer-owned, sin SQL.
- **Q2 (adaptador de datos)**: adaptador PROPIO del asistente en `assistant/infrastructure/`,
  independiente del de `analytics/` (cada bounded context posee su acceso a datos); internamente
  puede usar `db_connection.get_db()`.
- **Q3 (port de LLM)**: `LLMPort` con un único `complete(...)` que ENCAPSULA el fallback
  Groq→Gemini dentro del adaptador; `ask()` no conoce los proveedores.
- **Q4 (entidad de uso)**: agregado `AssistantUsage` (raíz) con user_id/championship_id/contador/
  ventana, reglas de cuota como `BRx.y`, persistencia tras `AssistantUsagePort`; `CREATE TABLE IF
  NOT EXISTS` idempotente preservado en el adapter.
- **Q5 (orden de extracción)**: de menor a mayor acoplamiento — (1) guardrails, (2)
  AssistantUsageTracker, (3) factual, (4) ContextBuilder, (5) `ask()` orquestador + shim;
  caracterización just-enough justo antes de cada paso.
- **Q6 (especificación de paridad)**: flujo completo de `ask()` como secuencia numerada +
  modos de degradación observables de cada `except Exception`, para que los tests de
  caracterización aseveren cada rama.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
