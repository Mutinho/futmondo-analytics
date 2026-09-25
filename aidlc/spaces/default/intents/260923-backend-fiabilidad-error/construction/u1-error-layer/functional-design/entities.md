# Entities — U1 `u1-error-layer`

La "entidad" de esta unidad es la **jerarquía de excepciones de integración**
(no una entidad de datos persistida). Se modela su forma: raíz, subtipos y el
contexto no sensible que llevan. Sin SQL, sin framework.

```yaml
entities:
  - name: IntegrationError
    description: >
      Raíz común de las excepciones de integración externa. Es la que capturan
      los consumidores (la ruta de sync). No se lanza directamente; se lanzan sus
      subtipos. Los mensajes van en inglés (diagnóstico de desarrollador).
    attributes:
      - name: failure_mode
        type: enum
        required: true
        allowed_values: [ban, timeout, unparseable]
        constraints: "identifica el modo de fallo; base de la clasificación recuperable/fatal"
      - name: status
        type: integer
        required: false
        constraints: "código HTTP si aplica (p. ej. 403); nunca material de credencial"
      - name: endpoint
        type: string
        required: false
        constraints: "ruta/endpoint NO sensible; nunca incluye token/password (NFR3)"
    entity_constraints:
      - "NUNCA incluir password ni token del usuario en el mensaje, repr o exc_info (NFR3)"
    relationships:
      - "IntegrationBanError es-un IntegrationError"
      - "IntegrationTimeoutError es-un IntegrationError"
      - "IntegrationUnparseableError es-un IntegrationError"
      - "SofascoreIPBanError (existente, FR2.1) es-un IntegrationBanError"

  - name: IntegrationBanError
    description: "Baneo de la integración (p. ej. Sofascore 403). Clasificación: FATAL."
    attributes:
      - name: failure_mode
        type: enum
        required: true
        allowed_values: [ban]
    relationships:
      - "hereda de IntegrationError"

  - name: IntegrationTimeoutError
    description: "Timeout puntual de la integración. Clasificación: RECUPERABLE."
    attributes:
      - name: failure_mode
        type: enum
        required: true
        allowed_values: [timeout]
    relationships:
      - "hereda de IntegrationError"

  - name: IntegrationUnparseableError
    description: "Respuesta heterogénea o no parseable. Clasificación: RECUPERABLE."
    attributes:
      - name: failure_mode
        type: enum
        required: true
        allowed_values: [unparseable]
    relationships:
      - "hereda de IntegrationError"
```

## Resumen

Cuatro tipos: una raíz `IntegrationError` (punto de captura) y tres subtipos por
modo de fallo. El baneo es fatal; timeout y no-parseable son recuperables. El
`SofascoreIPBanError` existente se re-parenta bajo `IntegrationBanError`
preservando su comportamiento FR2.1. Todo el conjunto vive en el módulo estrecho
`integration_errors`, fuera de los god-files, y ninguna instancia expone
credenciales (NFR3).

## Assumptions & Open Questions

None.
