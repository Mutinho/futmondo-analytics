# Business Rules — Functional Design (`261001-sync-god-file-resto`)

> Reglas que gobiernan el refactor de extracción por dominio. Son reglas de
> **equivalencia y estructura** (constraint/policy), no lógica de negocio nueva:
> el comportamiento observable no cambia. Cada regla traza a un FR de
> `requirements.md`. Idioma: castellano; identificadores en inglés.

## Source of truth

```yaml
rules:
  - id: BR1.1
    statement: >
      Cada dominio de sync pendiente se extrae a su propio contexto bajo
      backend/app/services/sync/<domain>/ con la terna orchestrator +
      domain/ports.py (Protocol consumer-owned) + infrastructure/<domain>_adapter.py.
    category: constraint
    applies_to: SyncDomain
    trigger: Extracción de un dominio
    logic: >
      IF se extrae un dominio THEN crear sync/<domain>/orchestrator.py,
      sync/<domain>/domain/ports.py y sync/<domain>/infrastructure/<domain>_adapter.py
      replicando la forma del piloto match_odds.
    violation_behavior: Diseño rechazado en revisión; no cumple el patrón objetivo.
    source: FR1.1, FR1.2

  - id: BR1.2
    statement: >
      El domain port declara EXACTAMENTE los métodos de DataManagerV2 que ese
      sync_* invoca hoy (nombres y firmas verbatim); el adapter los implementa
      delegando 1:1 a DataManagerV2.
    category: constraint
    applies_to: domain port / infrastructure adapter
    trigger: Diseño del port y adapter de un dominio
    logic: >
      IF el sync_* invoca dm.method(args) hoy THEN el port declara method(args)
      verbatim AND el adapter delega a self._dm.method(args) sin transformar.
    violation_behavior: Rompe la equivalencia de llamadas que la caracterización congela (BR4.2).
    source: FR3.1, FR7.2

  - id: BR2.1
    statement: >
      Tras extraer un dominio, su método público en DataSyncService queda como
      delegación fina al orchestrator del dominio.
    category: constraint
    applies_to: DataSyncService.sync_*
    trigger: Finalización de la extracción de un dominio
    logic: >
      IF el dominio está extraído THEN el cuerpo del método público NO contiene
      llamadas a FutmondoClient, NI SQL, NI time.sleep; sólo obtiene el
      orchestrator y devuelve su SyncResult.
    violation_behavior: El método sigue siendo god-code; incumple FR2.
    source: FR2.1, FR2.2

  - id: BR3.1
    statement: >
      La persistencia principal del dominio vive sólo en su infrastructure
      adapter, que envuelve DataManagerV2 verbatim. NUNCA se amplía ni modifica
      data_manager_v2.py.
    category: constraint
    applies_to: infrastructure adapter
    trigger: Movimiento del SQL de persistencia
    logic: >
      IF se mueve persistencia THEN va al adapter envolviendo DataManagerV2 verbatim;
      el método de servicio extraído NO contiene SQL.
    violation_behavior: Diseño rechazado; viola el mandato de no ampliar god-files.
    source: FR3.1

  - id: BR3.2
    statement: >
      Los ALTER TABLE / migraciones idempotentes y los helpers transversales
      (_enrich_market_values, _save_favorites, el SELECT user_championships de
      sync_prizes) quedan FUERA DE ALCANCE como deuda registrada.
    category: policy
    applies_to: SQL transversal / migraciones
    trigger: Extracción de un dominio con SQL no de persistencia principal
    logic: >
      IF el SQL es migración idempotente o helper transversal THEN NO se mueve en
      este intent; se deja donde está y se registra como deuda.
    violation_behavior: Amplía el blast radius más allá del alcance aprobado.
    source: FR3.2

  - id: BR4.1
    statement: >
      El manejo de errores y el throttling (time.sleep) se preservan VERBATIM al
      reubicarlos en el orchestrator; no se reclasifica ni se mejora ningún except.
    category: constraint
    applies_to: orchestrator
    trigger: Reubicación de la orquestación de un dominio
    logic: >
      IF se mueve lógica de error/throttling THEN se copia verbatim al orchestrator;
      recoverable degrada (StepStatus.DEGRADED vía sync_step_status) y fatal
      (IntegrationBanError) propaga, sólo donde ya existe hoy.
    violation_behavior: Cambia comportamiento observable; viola equivalencia estricta.
    source: FR6.1, FR6.2

  - id: BR4.2
    statement: >
      Ninguna credencial ni token Futmondo aparece en el mensaje, repr, exc_info
      ni logs de una excepción.
    category: authorization
    applies_to: manejo de errores / logging
    trigger: Registro o propagación de un fallo de integración
    logic: >
      IF se registra o propaga un fallo THEN el contexto es modo-de-fallo +
      datos no sensibles (status, endpoint); NUNCA material de credencial
      (_log_integration_failure).
    violation_behavior: Fuga de secretos; bloqueado por gitleaks y revisión.
    source: FR6.3, NFR1.2

  - id: BR5.1
    statement: >
      La superficie pública se preserva byte-a-byte: DataSyncService con 10
      métodos sync_* y sync_all(), que devuelve las 10 claves literales en orden fijo.
    category: constraint
    applies_to: DataSyncService (superficie pública)
    trigger: Cualquier cambio durante la extracción
    logic: >
      IF se refactoriza THEN las firmas públicas y las 10 claves literales de
      sync_all() (players, transactions, clauses, punishments_bonuses, dream_teams,
      player_performance, rosters, team_standings, match_odds, prizes) y su orden
      permanecen idénticas; el worker _run_sync_in_background no se rompe.
    violation_behavior: Rompe el worker del router y el frontend; viola FR5.
    source: FR5.1, FR5.2, FR5.4

  - id: BR5.2
    statement: >
      El SyncResult observable de cada dominio conserva su forma exacta (claves y
      tipos por dominio).
    category: constraint
    applies_to: SyncResult
    trigger: Extracción de un dominio
    logic: >
      IF se extrae un dominio THEN su SyncResult mantiene las mismas claves con
      los mismos tipos que hoy.
    violation_behavior: Cambio observable; viola equivalencia estricta.
    source: FR5.3

  - id: BR6.1
    statement: >
      Antes de extraer un dominio existe un test de caracterización que congela
      el SyncResult observable Y las llamadas a DataManagerV2, verde antes y
      después, con fakes en memoria.
    category: validation
    applies_to: proceso de extracción por dominio
    trigger: Inicio de la extracción de un dominio
    logic: >
      IF se va a extraer un dominio THEN escribir primero el test de
      caracterización (SyncResult + llamadas a DataManagerV2) con dobles/fakes en
      memoria, sin red/BD real/credenciales; debe estar verde antes y seguir
      verde después.
    violation_behavior: Extracción sin red de seguridad; incumple characterization-first.
    source: FR7.1, FR7.2, FR7.3

  - id: BR7.1
    statement: >
      prizes/ se uniforma con un facade/orchestrator (como analytics/ y assistant/),
      conservando calculator.py y team_prizes_writer.replace_team_prizes;
      sync_prizes queda como delegación fina preservando su SyncResult.
    category: constraint
    applies_to: prizes context / sync_prizes
    trigger: Unidad de uniformación de prizes
    logic: >
      IF se uniforma prizes THEN añadir facade/orchestrator que delega al cálculo
      puro y a la escritura atómica existentes; sync_prizes delega finamente y
      preserva rounds_processed + stale_prizes_removed.
    violation_behavior: prizes queda inconsistente con el patrón del resto.
    source: FR4.1, FR4.2

  - id: BR8.1
    statement: >
      No se ejecuta ruff format masivo sobre ficheros brownfield ya modificados;
      sólo se formatean los ficheros nuevos de cada dominio o de forma quirúrgica.
    category: policy
    applies_to: ficheros fuente
    trigger: Generación/edición de código del refactor
    logic: >
      IF se formatea THEN sólo los ficheros nuevos del dominio o cambios quirúrgicos;
      NUNCA reformateo masivo del god-file.
    violation_behavior: Infla diffs, expone avisos preexistentes, invalida la revisión en vuelo.
    source: FR3.2 (nota), NFR4.1

  - id: BR8.2
    statement: >
      El piso de cobertura --cov-fail-under=27 (line-only) no se relaja; el gate
      de CI bloqueante debe seguir verde.
    category: constraint
    applies_to: gate de CI / cobertura
    trigger: Cierre de cada unidad
    logic: >
      IF se mide cobertura THEN el piso no baja (ratchet sólo sube) AND el gate
      (gitleaks + pytest + ng test) está verde antes de fusionar.
    violation_behavior: Un rojo llegaría a main; prohibido.
    source: NFR2.1, NFR2.2
```

## Resumen de reglas

| ID | Categoría | Resumen | Fuente |
|----|-----------|---------|--------|
| BR1.1 | constraint | Extraer cada dominio a `sync/<domain>/` con orchestrator+port+adapter | FR1.1, FR1.2 |
| BR1.2 | constraint | El port declara los métodos de `DataManagerV2` verbatim; adapter delega 1:1 | FR3.1, FR7.2 |
| BR2.1 | constraint | El método público queda como delegación fina (sin ingesta/SQL/sleep) | FR2.1, FR2.2 |
| BR3.1 | constraint | Persistencia sólo en el adapter; nunca ampliar `data_manager_v2.py` | FR3.1 |
| BR3.2 | policy | Migraciones idempotentes y helpers transversales fuera de alcance | FR3.2 |
| BR4.1 | constraint | Errores y throttling preservados verbatim; sin reclasificar `except` | FR6.1, FR6.2 |
| BR4.2 | authorization | Sin credenciales/tokens en mensajes, `repr`, `exc_info` ni logs | FR6.3, NFR1.2 |
| BR5.1 | constraint | Superficie pública byte-a-byte; 10 claves literales y orden fijo | FR5.1, FR5.2, FR5.4 |
| BR5.2 | constraint | `SyncResult` por dominio conserva su forma exacta | FR5.3 |
| BR6.1 | validation | Caracterización (SyncResult + llamadas a DataManagerV2) verde antes/después | FR7.1-FR7.3 |
| BR7.1 | constraint | Uniformar `prizes/` al patrón facade; `sync_prizes` delegación fina | FR4.1, FR4.2 |
| BR8.1 | policy | Sin `ruff format` masivo; sólo ficheros nuevos o quirúrgico | NFR4.1 |
| BR8.2 | constraint | Piso de cobertura no se relaja; gate de CI verde | NFR2.1, NFR2.2 |
