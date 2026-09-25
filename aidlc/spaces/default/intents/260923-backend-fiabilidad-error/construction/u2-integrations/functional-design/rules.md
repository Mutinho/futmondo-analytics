# Business Rules — u2-integrations (Integraciones)

Reglas de negocio que gobiernan el comportamiento de fallo de las integraciones
externas y su reflejo en el estado del sync, para la unidad `u2-integrations`.
Trazan a FR4.2–FR4.5, NFR1, NFR2 (ver `requirements.md`) y honran las prácticas
afirmadas del equipo (excepciones tipadas propagadas, no swallow silencioso,
sin credenciales en excepciones, no-corrupción de datos).

## Part A — Source of truth (machine-readable)

```yaml
rules:
  - id: BR1.1
    statement: >
      FutmondoClient nunca devuelve None como señal de fallo; señala el fallo
      lanzando un subtipo tipado de IntegrationError.
    category: constraint
    applies_to: FutmondoClient
    trigger: fallo al contactar/parsear la respuesta de Futmondo
    logic: >
      IF Futmondo devuelve error de red/conexión, timeout o respuesta no parseable
      THEN lanzar el subtipo IntegrationError correspondiente (timeout →
      IntegrationTimeoutError; no parseable → IntegrationUnparseableError;
      RequestException de conexión → IntegrationRequestError) con
      `except <Typed>: raise` ANTES del `except Exception` genérico. Todo modo de
      fallo del contrato (incl. `request_exception`) tiene un subtipo tipado; el
      enum `other` cubre modos no previstos, de modo que ningún fallo se enmascara
      como None.
    on_violation: el fallo quedaría enmascarado como None; prohibido.
    source: FR4.2

  - id: BR1.2
    statement: >
      SofascoreClient señala baneo (403) como IntegrationBanError y sus
      excepciones heredan de la raíz común IntegrationError.
    category: constraint
    applies_to: SofascoreClient
    trigger: respuesta 403 (baneo), 404 (recurso ausente) o fallo recuperable de Sofascore
    logic: >
      IF Sofascore responde 403 THEN lanzar/propagar IntegrationBanError (fatal);
      el SofascoreIPBanError existente se re-parenta bajo IntegrationBanError,
      conservando su nombre y captores. IF responde 404 (recurso ausente) THEN NO
      es un fallo de integración: se trata como "sin datos" (ausencia legítima),
      no lanza excepción tipada ni marca DEGRADED (Contrato 2); la regla "nunca
      None como señal de FALLO" (BR1.1) no aplica a un 404, que es ausencia, no
      fallo. Los timeouts/respuestas no parseables/errores de conexión usan los
      subtipos recuperables.
    on_violation: excepción de Sofascore fuera de la raíz común, o tratar un 404 como fallo fatal.
    source: FR4.1, FR4.4, FR4.5

  - id: BR2.1
    statement: >
      El subtipo de excepción da la clasificación recuperable/fatal POR DEFECTO:
      IntegrationBanError es fatal; IntegrationTimeoutError e
      IntegrationUnparseableError son recuperables; IntegrationRequestError es
      recuperable por defecto (ver BR2.3 para la elevación en punto de escritura).
    category: policy
    applies_to: IntegrationErrors (contrato), SyncService (consumo)
    trigger: SyncService captura una excepción de integración
    logic: >
      La clasificación por defecto NO se calcula ad hoc: viene dada por el subtipo.
      La única excepción a "por tipo" es la elevación contextual de BR2.3.
    on_violation: clasificación por defecto inconsistente entre puntos de captura.
    source: FR3.2.1, FR4.1

  - id: BR2.3
    statement: >
      Un fallo de integración por defecto recuperable que alcanza un punto de
      escritura que podría dejar datos a medias se ELEVA a fatal.
    category: policy
    applies_to: SyncService (puntos de escritura), DbConnection
    trigger: excepción de integración recuperable dentro de una operación de escritura con riesgo de corrupción
    logic: >
      IF una excepción recuperable (p. ej. IntegrationRequestError) ocurre en un
      punto de escritura donde continuar dejaría datos parciales/corruptos THEN
      tratarla como FATAL: no continuar, abortar limpio, garantizar todo-o-nada
      (transacción, ver BR5.1). La elevación la decide el punto de captura por su
      contexto (Contrato 3: `request_exception` recuperable salvo que corrompa
      datos; `write_point_failure` fatal), no un atributo del tipo.
    on_violation: >
      degradar-y-continuar tras un fallo en escritura que corrompe datos; prohibido (NFR2).
    source: FR4.4, NFR2

  - id: BR2.2
    statement: >
      SyncService traduce el fallo de integración en acción con dos ramas except
      explícitas: fatal primero, recuperable después, antes del `except Exception`.
    category: constraint
    applies_to: SyncService
    trigger: excepción de integración durante un paso del sync
    logic: >
      IF excepción fatal (IntegrationBanError) THEN propagar/abortar limpio sin
      escribir datos a medias; ELSE IF excepción recuperable
      (IntegrationTimeoutError | IntegrationUnparseableError) THEN marcar el paso
      DEGRADED vía SyncStepStatus y CONTINUAR; el `except Exception` genérico
      queda como red de seguridad final.
    on_violation: >
      capturar por el genérico antes que por el tipado, o degradar un fallo fatal;
      prohibido.
    source: FR3.2.1, FR4.4

  - id: BR3.1
    statement: >
      Un fallo recuperable marca el paso como DEGRADED (StepStatus.DEGRADED vía
      SyncStepStatus) y la operación de sync NO falla.
    category: policy
    applies_to: SyncService, SyncStepStatus
    trigger: rama recuperable de BR2.2
    logic: >
      IF fallo recuperable THEN record_degraded_step(sink, task_id, step, reason,
      extra) y continuar con el siguiente paso; el sync termina sin error.
    on_violation: un recuperable que aborta el sync; prohibido.
    source: FR3.2.1, FR4.4

  - id: BR3.2
    statement: >
      Un fallo fatal aborta limpio: la excepción tipada se propaga y NO quedan
      datos a medias escritos.
    category: constraint
    applies_to: SyncService
    trigger: rama fatal de BR2.2
    logic: >
      IF fallo fatal THEN propagar la excepción tipada; garantizar que ningún
      punto de escritura quedó a medias (ver BR5.1).
    on_violation: datos parciales corruptos tras un fatal; prohibido.
    source: FR3.2.1, NFR2

  - id: BR4.1
    statement: >
      Cada fallo de integración (recuperable o fatal) emite un log estructurado
      con modo de fallo + contexto no sensible.
    category: policy
    applies_to: SyncService, clientes de integración
    trigger: cualquier excepción de integración capturada/propagada
    logic: >
      Emitir un log estructurado con campos sync_step, reason, failure_mode,
      status?, endpoint?, task_id, para observabilidad vía `fly logs` + `grep`.
    on_violation: fallo sin log estructurado, u observabilidad no filtrable.
    source: NFR1

  - id: BR4.2
    statement: >
      Ninguna excepción de integración ni su log incluye password ni token del
      usuario en mensaje, repr o exc_info.
    category: authorization
    applies_to: IntegrationErrors, clientes de integración, SyncService (logging)
    trigger: construcción de excepción o emisión de log
    logic: >
      El contexto se limita a failure_mode, status, endpoint y campos no
      sensibles; nunca material de credencial.
    on_violation: filtración de credenciales; prohibido (NFR3, práctica afirmada).
    source: NFR3

  - id: BR5.1
    statement: >
      El reemplazo de team_prizes es una transacción única atómica: borrado
      (DELETE ... NOT IN (...)) y repoblado ocurren en la misma transacción.
    category: constraint
    applies_to: SyncService (punto de escritura team_prizes), DbConnection
    trigger: recomputación/reemplazo del conjunto de premios por equipo
    logic: >
      IF cualquier paso del reemplazo falla THEN rollback completo de la
      transacción (todo-o-nada); la tabla nunca queda en estado mixto.
    on_violation: >
      caché/tabla team_prizes en estado mixto tras un fallo; prohibido (NFR2).
    source: NFR2

  - id: BR5.2
    statement: >
      La no-corrupción de team_prizes es verificable por spec que fuerza el fallo
      en el punto de escritura y asvera el estado resultante.
    category: constraint
    applies_to: test suite de u2-integrations
    trigger: caracterización/verificación del punto de escritura
    logic: >
      Un spec fuerza un fallo dentro de la transacción de reemplazo y asvera que
      la tabla queda consistente (estado previo íntegro), no a medias.
    on_violation: spec que captura la excepción sin aseverar el efecto; prohibido.
    source: NFR2

  - id: BR6.1
    statement: >
      Antes de migrar el contrato de _make_request se entrega un inventario
      verificable de llamadores y se caracteriza su comportamiento actual.
    category: policy
    applies_to: FutmondoClient (_make_request) y sus llamadores
    trigger: cambio de contrato de _make_request (None/bool → excepción tipada)
    logic: >
      La migración cubre el núcleo (_make_request + llamadores donde un None no
      detectado corrompe datos); el resto de llamadores queda como deuda
      registrada.
    on_violation: cambiar el contrato sin inventario/caracterización previos.
    source: FR4.3

  - id: BR7.1
    statement: >
      Se documentan los contratos y modos de fallo esperados de Sofascore y
      Futmondo.
    category: policy
    applies_to: documentación de contratos de integración
    trigger: entrega de U2
    logic: >
      Documentar Sofascore (API no oficial vía curl_cffi, baneo 403) y Futmondo
      (endpoints heterogéneos, login, getters) con sus modos de fallo esperados.
    on_violation: contrato de fallo no documentado.
    source: FR4.5
```

## Part B — Vista humana (resumen de reglas)

| Regla | Categoría | Enunciado | Fuente |
|---|---|---|---|
| BR1.1 | constraint | `FutmondoClient` no devuelve `None`; lanza subtipo tipado (incl. `request_exception`) | FR4.2 |
| BR1.2 | constraint | `SofascoreClient`: 403 → `IntegrationBanError` (fatal); 404 → sin datos (no fallo); hereda de la raíz | FR4.1, FR4.4, FR4.5 |
| BR2.1 | policy | El subtipo da la clasificación recuperable/fatal **por defecto** | FR3.2.1, FR4.1 |
| BR2.3 | policy | Recuperable en punto de escritura con riesgo de corrupción → se **eleva a fatal** | FR4.4, NFR2 |
| BR2.2 | constraint | `SyncService`: dos ramas `except` (fatal, recuperable) antes del genérico | FR3.2.1, FR4.4 |
| BR3.1 | policy | Recuperable → `DEGRADED` + continuar (el sync no falla) | FR3.2.1, FR4.4 |
| BR3.2 | constraint | Fatal → propagar; sin datos a medias | FR3.2.1, NFR2 |
| BR4.1 | policy | Log estructurado con modo de fallo + contexto no sensible | NFR1 |
| BR4.2 | authorization | Nunca password/token en excepción ni log | NFR3 |
| BR5.1 | constraint | Reemplazo `team_prizes` como transacción única atómica | NFR2 |
| BR5.2 | constraint | No-corrupción verificable por spec que asvera el efecto | NFR2 |
| BR6.1 | policy | Inventario + caracterización de `_make_request` antes de migrar | FR4.3 |
| BR7.1 | policy | Documentar contratos/modos de fallo de Sofascore y Futmondo | FR4.5 |
