# Business Rules — Descomposición DDD de `data_sync_service.py`

> Reglas que la descomposición DEBE respetar. En un refactor, las "reglas de
> negocio" son sobre todo **invariantes de equivalencia** y **restricciones de
> estructura**: lo que no puede cambiar de comportamiento y dónde puede (y no
> puede) vivir cada responsabilidad. Cada regla traza a un FR/NFR de
> `requirements.md`.

```yaml
rules:
  - id: BR1.1
    statement: >
      DataSyncService conserva la clase, las 10 operaciones publicas sync_* con
      sus firmas, sync_all() y la ruta de import actuales.
    category: constraint
    applies_to: DataSyncService (facade)
    trigger: Cualquier extraccion de dominio.
    logic: >
      IF se mueve logica de un dominio a su modulo THEN el metodo sync_* publico
      sigue existiendo en DataSyncService con la misma firma y delega en el modulo.
    violation_behavior: >
      Un llamador existente que rompe su import o firma es un fallo del refactor.
    source: FR1.1, FR1.2

  - id: BR1.2
    statement: >
      El facade DataSyncService es delgado: solo delega; no contiene ingesta,
      calculo ni SQL propios.
    category: constraint
    applies_to: DataSyncService (facade)
    trigger: Diseno de cada metodo sync_* del facade.
    logic: >
      IF un metodo del facade contiene logica de ingesta/calculo/SQL/errores
      THEN esa logica pertenece al orquestador del dominio, no al facade.
    violation_behavior: Facade que reengorda; rechazar en revision.
    source: FR1.2

  - id: BR1.3
    statement: >
      Antes de mover codigo se produce un inventario de imports de los simbolos
      de data_sync_service.py consumidos desde fuera del modulo; se anade shim de
      re-export solo para los que se muevan y esten consumidos externamente.
    category: policy
    applies_to: Migracion de simbolos
    trigger: Inicio de la extraccion.
    logic: >
      IF un simbolo consumido externamente se mueve THEN dejar shim de re-export
      en su ruta historica; ELSE no crear shim.
    violation_behavior: Import roto en un llamador; o shim innecesario (ruido).
    source: FR1.3, FR1.3.1

  - id: BR2.1
    statement: >
      Cada dominio accede a la persistencia solo a traves de su port estrecho
      (Protocol) implementado por un adaptador de infraestructura; la capa de
      aplicacion no llama a DataManagerV2 directamente.
    category: constraint
    applies_to: Todos los dominios (full-layered y lightweight)
    trigger: Cualquier lectura/escritura de datos del dominio.
    logic: >
      IF la aplicacion necesita datos THEN los pide al port; el SQL vive solo en
      el adaptador que implementa el port.
    violation_behavior: SQL o llamada directa a DataManagerV2 en application; rechazar.
    source: FR3.1

  - id: BR2.2
    statement: >
      El SQL existente de cada dominio se envuelve en su adaptador, no se
      reescribe; data_manager_v2.py no se toca ni se amplia.
    category: constraint
    applies_to: infrastructure/*_adapter por dominio
    trigger: Extraccion del acceso a datos de un dominio.
    logic: >
      IF hay SQL/cursor.execute inline hoy THEN moverlo verbatim al adaptador;
      NUNCA anadir codigo a data_manager_v2.py.
    violation_behavior: God-file ampliado o SQL reescrito; viola regla afirmada.
    source: FR3.2, NFR3

  - id: BR2.3
    statement: >
      La ingesta externa (FutmondoClient/Sofascore) permanece en el orquestador
      de aplicacion del dominio (patron sync_prizes), no tras un port.
    category: policy
    applies_to: Orquestador de aplicacion por dominio
    trigger: Diseno del flujo ingesta->calculo->persistencia del dominio.
    logic: >
      IF el dominio ingesta de un cliente externo THEN el orquestador llama al
      cliente (inyectable via DataSyncService.__init__) y delega calculo/escritura.
    violation_behavior: Ingesta escondida tras un port que se desvia del patron FR2.3.
    source: FR2.3

  - id: BR3.1
    statement: >
      sync_all() invoca los 10 sync_* en el orden actual (players primero por FK)
      y agrega bajo las 10 claves literales sin renombrar.
    category: constraint
    applies_to: sync_all() coordinador
    trigger: Ejecucion de sync_all().
    logic: >
      IF se construye el SyncAllReport THEN el orden y las 10 claves literales
      (players, transactions, clauses, punishments_bonuses, dream_teams,
      player_performance, rosters, team_standings, match_odds, prizes) son fijos;
      rankings -> clave team_standings.
    violation_behavior: >
      Reordenar o renombrar una clave rompe la equivalencia observable.
    source: FR2.2, FR5.1.1, FR5.2

  - id: BR3.2
    statement: >
      Cada sync_* devuelve el mismo payload de resultado (estructura y campos)
      que antes del refactor.
    category: constraint
    applies_to: SyncResult de cada dominio
    trigger: Retorno de cualquier sync_*.
    logic: >
      IF cambia la forma del SyncResult de un dominio THEN es una regresion de
      equivalencia; congelar la forma con caracterizacion antes de extraer.
    violation_behavior: Payload divergente; fallo de equivalencia estricta.
    source: FR5.1

  - id: BR4.1
    statement: >
      El manejo de Integration*Error (recuperable/fatal) y el throttling
      (time.sleep) viven en el orquestador de aplicacion del dominio, con
      except <Typed>: (propaga/degrada segun caso) antes del except Exception
      generico, preservando la semantica observable actual.
    category: policy
    applies_to: Orquestador de aplicacion por dominio
    trigger: Fallo de integracion externa o pausa de throttling durante la ingesta.
    logic: >
      IF ocurre un Integration*Error recuperable en punto de escritura THEN
      PROPAGATE (BR2.3 de errores: abortar limpio, no degradar sobre escritura
      que podria corromper datos); IF recuperable fuera de escritura THEN degrada
      y continua; el except Exception generico es la red final que NUNCA enmascara
      las ramas tipadas.
    violation_behavior: >
      Cambiar donde se captura o si se propaga altera el efecto observable (FR5.3).
    source: FR5.3

  - id: BR4.2
    statement: >
      Ninguna excepcion de integracion incluye el password ni el token Futmondo
      del usuario en mensaje, repr ni exc_info; solo modo de fallo + contexto no
      sensible (status, endpoint).
    category: authorization
    applies_to: Manejo de errores del orquestador
    trigger: Construccion/propagacion de una excepcion de integracion.
    logic: IF se registra o propaga un fallo THEN sin material de credencial.
    violation_behavior: Fuga de credencial en logs/excepcion; viola regla afirmada.
    source: FR5.3 (extiende reglas afirmadas de no-credenciales)

  - id: BR5.1
    statement: >
      La escritura atomica set-replacement de prizes (replace_team_prizes: upsert
      del conjunto + DELETE ... NOT IN en una sola transaccion, all-or-nothing) se
      preserva como patron de referencia para reemplazos de conjunto.
    category: constraint
    applies_to: prizes (y cualquier dominio con reemplazo de conjunto cacheado)
    trigger: Persistencia de un conjunto que sustituye al anterior.
    logic: >
      IF se persiste un conjunto que reemplaza filas previas THEN upsert + DELETE
      del stale en UNA transaccion; NUNCA try/except->warning que deje estado mixto.
    violation_behavior: Estado mixto sin senal; corrupcion de datos.
    source: FR5.4

  - id: BR6.1
    statement: >
      Cada dominio se congela con tests de caracterizacion (efecto observable:
      payload/estado/modo de fallo) usando fakes en memoria antes de extraerse; la
      suite queda en verde y el piso de cobertura --cov-fail-under=27 no se relaja.
    category: policy
    applies_to: Proceso de extraccion por dominio
    trigger: Antes de mover el codigo de un dominio.
    logic: >
      IF se va a extraer un dominio THEN existe primero su caracterizacion en
      verde; el piso de cobertura solo sube por trinquete, nunca baja.
    violation_behavior: Extraccion sin red; o piso relajado para pasar el gate.
    source: FR4.1, FR4.2, FR4.3, NFR2
```

## Resumen de reglas

| ID | Categoría | Regla (resumen) | Fuente |
|----|-----------|-----------------|--------|
| BR1.1 | constraint | Preservar clase, 10 `sync_*`, `sync_all()`, firmas e import | FR1.1, FR1.2 |
| BR1.2 | constraint | Facade delgado: solo delega | FR1.2 |
| BR1.3 | policy | Inventario de imports → shim de re-export solo donde haga falta | FR1.3, FR1.3.1 |
| BR2.1 | constraint | Datos solo tras port estrecho por dominio | FR3.1 |
| BR2.2 | constraint | Envolver SQL en adaptador; no tocar `data_manager_v2.py` | FR3.2, NFR3 |
| BR2.3 | policy | Ingesta externa en el orquestador (patrón `sync_prizes`) | FR2.3 |
| BR3.1 | constraint | Orden fijo + 10 claves literales en `sync_all()` (`rankings`→`team_standings`) | FR2.2, FR5.1.1, FR5.2 |
| BR3.2 | constraint | Mismo payload por `sync_*` | FR5.1 |
| BR4.1 | policy | Errores tipados + throttling en el orquestador; propaga/degrada preservado | FR5.3 |
| BR4.2 | authorization | Sin credenciales en excepciones/logs | FR5.3 |
| BR5.1 | constraint | Escritura atómica set-replacement (`replace_team_prizes`) preservada | FR5.4 |
| BR6.1 | policy | Characterization-first por dominio; piso de cobertura solo sube | FR4, NFR2 |
