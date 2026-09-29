# Entities — unidad `assistant`

Modelo de entidades para la descomposición DDD de `assistant_service.py`. Refactor sin cambio
de comportamiento observable: las entidades reflejan el estado que el código ACTUAL ya maneja
(no se introduce estado nuevo). La única entidad con persistencia propia es `AssistantUsage`
(tabla `assistant_usage`); el resto del flujo de `ask()` opera sobre value objects efímeros.

```yaml
entities:
  - name: AssistantUsage
    kind: aggregate_root
    description: >
      Registro de consumo del asistente IA por usuario y campeonato dentro de una ventana
      temporal. Gobierna la cuota (rate limit) de peticiones. Persiste en la tabla
      assistant_usage (creada de forma idempotente por el adaptador). Comportamiento existente
      preservado: el AssistantUsageTracker actual ya lee/escribe estos datos.
    attributes:
      - name: user_id
        type: string
        required: true
        references: "identidad del usuario logado (JWT); no es una FK gestionada en este contexto"
      - name: championship_id
        type: string
        required: true
        references: "campeonato activo del usuario"
      - name: request_count
        type: integer
        required: true
        default: 0
        min: 0
        constraints: "contador de peticiones dentro de la ventana temporal vigente"
      - name: window_start
        type: timestamp
        required: true
        constraints: "inicio de la ventana de cuota; el reinicio de ventana es lógica del agregado"
    entity_constraints:
      - "La unicidad lógica es (user_id, championship_id) dentro de la ventana vigente."
      - "El esquema físico se materializa con CREATE TABLE IF NOT EXISTS idempotente en el adaptador (FR4.2); no hay migración explícita en este intent (OOS5)."
    relationships:
      - "AssistantUsage no referencia por objeto a otros agregados; se relaciona con user/championship por id (patrón DDD reference-by-id)."

  - name: AssistantQuery
    kind: value_object
    description: >
      Petición entrante al asistente (efímera, sin identidad). Entra por ask() y atraviesa
      guardrails → factual → contexto → LLM. No se persiste en este contexto (la conversación
      la persiste el endpoint, fuera de alcance OOS7).
    attributes:
      - name: user_id
        type: string
        required: true
      - name: championship_id
        type: string
        required: true
      - name: message
        type: string
        required: true
        constraints: "texto del usuario; sujeto a guardrails (BR1.x)"
      - name: history
        type: list
        required: false
        constraints: "historial de conversación provisto por el endpoint; opcional"
    relationships:
      - "AssistantQuery es la entrada del workflow ask() especificado en functional-spec.md."

  - name: AssistantResponse
    kind: value_object
    description: >
      Respuesta saliente de ask() (efímera). Contrato de respuesta idéntico al actual (FR1.1):
      el texto de respuesta y el contexto usado. Su forma exacta la fija el código existente y
      se congela por caracterización (FR6).
    attributes:
      - name: response
        type: string
        required: true
        constraints: "texto devuelto: respuesta factual, respuesta LLM, o GUARDRAIL_RESPONSE"
      - name: context_used
        type: object
        required: false
        constraints: "contexto/metadatos que el contrato actual ya devuelve; forma preservada"
    relationships:
      - "AssistantResponse es la salida del workflow ask()."

  - name: ChampionshipContext
    kind: value_object
    description: >
      Contexto de campeonato ensamblado por el ContextBuilder a partir de lecturas de datos
      (a través de AssistantReadPort). Efímero, de solo lectura; alimenta el prompt del LLM.
      Agrupa las lecturas que hoy hacen los métodos _ctx_* y los handlers factual _factual_*.
    attributes:
      - name: sections
        type: object
        required: false
        constraints: >
          Colección de fragmentos de contexto (balances, plantilla, clasificación, mercado, etc.)
          tal como los produce el ContextBuilder actual; la composición exacta se congela por
          caracterización y no cambia en este refactor.
    relationships:
      - "ChampionshipContext lo produce el ContextBuilder leyendo vía AssistantReadPort; lo consume el orquestador ask() para construir el prompt."
```

## Resumen del modelo de entidades

El refactor introduce **un** agregado con persistencia, `AssistantUsage` (tabla
`assistant_usage`), que encapsula la cuota de uso del asistente y cuyas reglas se detallan en
`rules.md`. El resto del flujo de `ask()` opera sobre **value objects efímeros**:
`AssistantQuery` (entrada), `AssistantResponse` (salida, contrato idéntico al actual) y
`ChampionshipContext` (contexto de solo lectura ensamblado por el ContextBuilder). Ninguna
entidad nueva se añade respecto al comportamiento actual: el modelo documenta el estado que el
god-file ya maneja, ahora con fronteras explícitas. El acceso a datos de `ChampionshipContext`
y de los handlers factual pasa por `AssistantReadPort` (solo lectura); la persistencia de
`AssistantUsage` pasa por `AssistantUsagePort` (ver `functional-spec.md` para los ports).
