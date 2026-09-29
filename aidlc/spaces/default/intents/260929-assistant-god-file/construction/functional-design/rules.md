# Business Rules — unidad `assistant`

Reglas de negocio que el paquete `assistant/` DEBE preservar tras el refactor. Son el
comportamiento observable ACTUAL del god-file, ahora explicitado para que los tests de
caracterización (FR6) aseveren cada rama. No se introduce ninguna regla nueva: refactor sin
cambio de comportamiento. Formato `BR{group}.{seq}` para trazabilidad.

```yaml
rules:
  # Grupo 1 — Guardrails (seam puro, FR3.1)
  - id: BR1.1
    statement: "Un mensaje que coincide con un patrón bloqueado devuelve la respuesta de guardrail sin invocar factual ni LLM."
    category: authorization
    applies_to: AssistantQuery.message
    trigger: "ask() recibe un mensaje"
    logic: "IF message coincide con BLOCKED_PATTERNS THEN devolver GUARDRAIL_RESPONSE y terminar (no factual, no LLM)."
    violation_behavior: "N/A — es una barrera; su efecto es cortar el flujo."
    source: FR3.1
  - id: BR1.2
    statement: "Un mensaje permitido (dentro de ALLOWED_KEYWORDS / fuera de BLOCKED_PATTERNS) continúa al flujo factual/LLM."
    category: authorization
    applies_to: AssistantQuery.message
    trigger: "ask() recibe un mensaje"
    logic: "IF message NO está bloqueado THEN continuar a la fase factual."
    violation_behavior: "N/A"
    source: FR3.1
  - id: BR1.3
    statement: "El módulo de guardrails es puro: solo regex/strings, sin I/O de red ni de BD."
    category: constraint
    applies_to: "seam guardrails"
    trigger: "diseño/implementación del módulo"
    logic: "IF el módulo guardrails importa red o BD THEN es una violación del contrato de pureza."
    violation_behavior: "Rechazar en revisión; el guardrail debe ser testeable sin dobles."
    source: FR3.1

  # Grupo 2 — Capa factual (FR3.2)
  - id: BR2.1
    statement: "Si el mensaje coincide con un patrón factual, la respuesta se produce desde datos (vía AssistantReadPort), sin llamar al LLM."
    category: calculation
    applies_to: AssistantQuery.message
    trigger: "mensaje permitido tras guardrails"
    logic: "IF _try_factual_answer encuentra coincidencia (FACTUAL_PATTERNS) THEN devolver respuesta factual y NO invocar LLM."
    violation_behavior: "N/A"
    source: FR3.2
  - id: BR2.2
    statement: "Los handlers factual leen datos exclusivamente a través de AssistantReadPort (no cursor.execute directo)."
    category: constraint
    applies_to: "seam factual"
    trigger: "lectura de datos en un handler _factual_*"
    logic: "IF un handler factual ejecuta SQL crudo directo THEN es una violación (el SQL vive solo en el adaptador, FR4.1)."
    violation_behavior: "Rechazar en revisión."
    source: [FR3.2, FR4.1]

  # Grupo 3 — ContextBuilder (FR3.3)
  - id: BR3.1
    statement: "Si no hay respuesta factual, el ContextBuilder ensambla ChampionshipContext leyendo vía AssistantReadPort y se invoca al LLM con ese contexto."
    category: calculation
    applies_to: ChampionshipContext
    trigger: "mensaje permitido sin coincidencia factual"
    logic: "IF NO factual THEN _build_context(...) vía AssistantReadPort → invocar LLM con el contexto."
    violation_behavior: "N/A"
    source: FR3.3
  - id: BR3.2
    statement: "Todo el SQL de contexto reside en el adaptador de infraestructura, detrás de AssistantReadPort; el ContextBuilder no contiene SQL crudo."
    category: constraint
    applies_to: "seam ContextBuilder"
    trigger: "acceso a datos de contexto"
    logic: "IF ContextBuilder contiene cursor.execute THEN violación (SQL solo en adaptador, FR4.1/FR4.3)."
    violation_behavior: "Rechazar en revisión."
    source: [FR3.3, FR4.1, FR4.3]
  - id: BR3.3
    statement: "Un fallo en una lectura de contexto/mercado DEGRADA sin romper: se preserva el efecto observable del except Exception actual (omitir sección / contexto parcial), sin propagar un fallo nuevo."
    category: policy
    applies_to: "seam ContextBuilder / lecturas de mercado"
    trigger: "excepción durante una lectura de contexto o de mercado"
    logic: "IF una lectura de contexto/mercado lanza excepción THEN degradar según el comportamiento actual (omitir/parcial), sin abortar ask(); congelado por caracterización (FR6.2)."
    violation_behavior: "Un cambio en el modo de degradación observable de las lecturas de contexto es una regresión."
    source: [FR3.3, FR6.2]

  # Grupo 4 — Cuota de uso / AssistantUsage (FR3.4)
  - id: BR4.1
    statement: "Antes de servir una petición que consume cuota, se comprueba si el usuario puede hacer la petición dentro de su ventana."
    category: authorization
    applies_to: AssistantUsage
    trigger: "ask() va a consumir cuota (comportamiento actual de can_make_request)"
    logic: "IF request_count dentro de la ventana >= límite THEN denegar/limitar según el comportamiento actual; ELSE permitir."
    violation_behavior: "Se preserva EXACTAMENTE el comportamiento observable actual del tracker (congelado por caracterización, FR6)."
    source: FR3.4
  - id: BR4.2
    statement: "Tras servir una petición, se registra el consumo (record_usage) actualizando el contador de la ventana."
    category: calculation
    applies_to: AssistantUsage
    trigger: "petición servida que consume cuota"
    logic: "THEN incrementar request_count de la ventana vigente (o iniciar ventana nueva) según el comportamiento actual."
    violation_behavior: "N/A"
    source: FR3.4
  - id: BR4.3
    statement: "La persistencia de uso pasa por AssistantUsagePort; la tabla assistant_usage se crea de forma idempotente en el adaptador."
    category: constraint
    applies_to: AssistantUsage
    trigger: "lectura/escritura de uso"
    logic: "IF la escritura de uso no pasa por el port/adaptador THEN violación; el CREATE TABLE IF NOT EXISTS se preserva idempotente en el adapter (FR4.2)."
    violation_behavior: "Rechazar en revisión."
    source: [FR3.4, FR4.2, FR4.3]

  # Grupo 5 — Integración LLM y degradación (FR5)
  - id: BR5.1
    statement: "La llamada LLM intenta Groq primero y, si falla, cae a Gemini, preservando el orden de fallback exacto."
    category: policy
    applies_to: "seam LLM (LLMPort.complete)"
    trigger: "se necesita respuesta generativa (no factual)"
    logic: "IF Groq falla THEN intentar Gemini; el orden y el resultado observable se preservan (FR5.1)."
    violation_behavior: "N/A"
    source: FR5.1
  - id: BR5.2
    statement: "El fallback Groq→Gemini se encapsula dentro del adaptador de LLMPort; ask() no conoce los proveedores."
    category: constraint
    applies_to: "seam LLM"
    trigger: "diseño del port de LLM"
    logic: "IF ask() referencia proveedores LLM concretos THEN violación (encapsulación en el adaptador, Q3=A)."
    violation_behavior: "Rechazar en revisión."
    source: FR5.1
  - id: BR5.3
    statement: "Un fallo de la integración LLM DEGRADA sin romper: el comportamiento observable del except Exception actual se preserva exactamente."
    category: policy
    applies_to: "seam LLM"
    trigger: "excepción durante la llamada LLM"
    logic: "IF la llamada LLM lanza excepción THEN degradar según el comportamiento actual (no propagar un fallo nuevo); congelado por caracterización (FR6.2)."
    violation_behavior: "Un cambio en el modo de degradación observable es una regresión."
    source: [FR5.1, FR6.2]
  - id: BR5.4
    statement: "Ni el mensaje, ni el repr, ni el contexto de una excepción del asistente incluyen credenciales/tokens reales."
    category: constraint
    applies_to: "manejo de errores del asistente"
    trigger: "se construye/loguea una excepción"
    logic: "IF una excepción incluye material de credencial THEN violación (regla afirmada de no-credenciales-en-claro)."
    violation_behavior: "Rechazar en revisión."
    source: "memory:M1 (regla afirmada: nunca credenciales/tokens Futmondo en mensaje/repr/exc_info)"

  # Grupo 6 — Contrato público (FR1)
  - id: BR6.1
    statement: "get_assistant_service() + ask() preservan firma y contrato de respuesta idénticos; el módulo original queda como shim de re-export."
    category: constraint
    applies_to: "superficie pública del paquete"
    trigger: "cualquier cambio en la superficie pública"
    logic: "IF la firma de ask() o get_assistant_service() cambia, o el import histórico se rompe, THEN violación (FR1.1/FR1.2)."
    violation_behavior: "Rechazar; el endpoint assistant.py debe funcionar sin cambios."
    source: [FR1.1, FR1.2]
```

## Resumen de reglas

| ID | Categoría | Enunciado (resumen) | Origen |
|----|-----------|---------------------|--------|
| BR1.1 | authorization | Mensaje bloqueado → GUARDRAIL_RESPONSE, corta el flujo | FR3.1 |
| BR1.2 | authorization | Mensaje permitido → continúa a factual/LLM | FR3.1 |
| BR1.3 | constraint | Guardrails es módulo puro (sin I/O) | FR3.1 |
| BR2.1 | calculation | Coincidencia factual → respuesta desde datos, sin LLM | FR3.2 |
| BR2.2 | constraint | Factual lee solo vía AssistantReadPort | FR3.2, FR4.1 |
| BR3.1 | calculation | Sin factual → ContextBuilder + LLM con contexto | FR3.3 |
| BR3.2 | constraint | SQL de contexto solo en el adaptador | FR3.3, FR4.1, FR4.3 |
| BR3.3 | policy | Fallo de lectura de contexto/mercado degrada sin romper | FR3.3, FR6.2 |
| BR4.1 | authorization | Comprobar cuota antes de consumir | FR3.4 |
| BR4.2 | calculation | Registrar consumo tras servir | FR3.4 |
| BR4.3 | constraint | Uso vía AssistantUsagePort; CREATE TABLE idempotente en adapter | FR3.4, FR4.2, FR4.3 |
| BR5.1 | policy | LLM: Groq → fallback Gemini, orden preservado | FR5.1 |
| BR5.2 | constraint | Fallback encapsulado en el adaptador; ask() no ve proveedores | FR5.1 |
| BR5.3 | policy | Fallo LLM degrada sin romper (modo observable preservado) | FR5.1, FR6.2 |
| BR5.4 | constraint | Sin credenciales/tokens en excepciones | memory:M1 |
| BR6.1 | constraint | Superficie pública idéntica + shim de re-export | FR1.1, FR1.2 |
