# Business Rules — U1 `u1-error-layer`

```yaml
rules:
  - id: BR1.1
    statement: "Un baneo de integración es un fallo FATAL y se propaga."
    category: policy
    applies_to: IntegrationBanError
    trigger: "un cliente detecta un baneo (p. ej. Sofascore HTTP 403)"
    logic: "IF respuesta indica baneo THEN lanzar IntegrationBanError (fatal), NO devolver None ni continuar"
    violation_behaviour: "tragar el baneo o devolver None es una violación (fallo silencioso)"
    source: FR3.2.1, FR4.4

  - id: BR1.2
    statement: "Un timeout puntual es un fallo RECUPERABLE."
    category: policy
    applies_to: IntegrationTimeoutError
    trigger: "una llamada de integración supera su timeout"
    logic: "IF timeout THEN lanzar IntegrationTimeoutError (recuperable); el consumidor degrada el paso y continúa"
    violation_behaviour: "abortar todo el sync por un timeout puntual sería incorrecto"
    source: FR3.2.1

  - id: BR1.3
    statement: "Una respuesta heterogénea o no parseable es un fallo RECUPERABLE."
    category: policy
    applies_to: IntegrationUnparseableError
    trigger: "la respuesta de la integración no se puede parsear (JSON inválido, forma inesperada)"
    logic: "IF no parseable THEN lanzar IntegrationUnparseableError (recuperable); el consumidor degrada el paso"
    violation_behaviour: "devolver None silencioso enmascara el fallo"
    source: FR3.2.1, FR4.2

  - id: BR1.4
    statement: "Ninguna excepción de integración expone credenciales."
    category: constraint
    applies_to: IntegrationError (y todos sus subtipos)
    trigger: "construcción/serialización de la excepción (mensaje, repr, exc_info)"
    logic: "IF se construye una excepción de integración THEN su mensaje/repr/exc_info NO contiene password ni token; solo failure_mode + contexto no sensible (status, endpoint)"
    violation_behaviour: "incluir credencial es una violación de NFR3 (gitleaks/revisión lo detectan)"
    source: NFR3

  - id: BR1.5
    statement: "Un fallo tras un commit previo en un punto de escritura es FATAL y no deja datos a medias."
    category: constraint
    applies_to: puntos de escritura de la ruta de sync (p. ej. DELETE ... NOT IN de team_prizes)
    trigger: "un fallo ocurre después de un commit previo dentro de una operación de escritura multi-paso"
    logic: "IF fallo en punto de escritura tras commit THEN tratar como fatal (propagar); el diseño de U2 usa reemplazo transaccional atómico para no dejar estado mixto"
    violation_behaviour: "tragar el fallo dejando la caché/tabla en estado mixto corrompe datos (NFR2)"
    source: FR3.2.1, NFR2

  - id: BR1.6
    statement: "Reclasificar capturas amplias de la primera oleada, sin cambiar la semántica transaccional correcta."
    category: policy
    applies_to: capturas amplias de arranque (main.py), migraciones (scripts/migrate_*), db_connection.py
    trigger: "endurecimiento de una captura amplia existente"
    logic: "IF se endurece una captura THEN distinguir recuperable (loguear/degradar, seguir) de fatal (propagar/abortar limpio), characterization-first; NO alterar el rollback+raise correcto ya presente"
    violation_behaviour: "reescribir o ampliar el god-file, o romper la semántica transaccional, es una violación"
    source: FR3.2.2, FR3.2.3
```

## Resumen de reglas

| ID | Regla | Categoría | Fuente |
|---|---|---|---|
| BR1.1 | Baneo = fatal, propagar | policy | FR3.2.1, FR4.4 |
| BR1.2 | Timeout = recuperable | policy | FR3.2.1 |
| BR1.3 | No parseable = recuperable | policy | FR3.2.1, FR4.2 |
| BR1.4 | Sin credenciales en excepciones | constraint | NFR3 |
| BR1.5 | Fallo tras commit = fatal, sin datos a medias | constraint | FR3.2.1, NFR2 |
| BR1.6 | Reclasificar sin romper transacciones | policy | FR3.2.2, FR3.2.3 |

## Assumptions & Open Questions

None.
