# Rules — Invariantes del refactor de `data_manager_v2`

> Las "reglas de negocio" de este refactor son los **invariantes de
> equivalencia y de patrón** que gobiernan cada extracción. Son verificables
> (pass/fail) y trazan a los requisitos. No hay reglas de dominio nuevas: las
> reglas de negocio funcionales de Futmondo (cálculo de finanzas, premios, etc.)
> se preservan verbatim y no se rediseñan aquí.

## Source of truth

```yaml
rules:
  - id: BR1.1
    statement: "La superficie publica de DataManagerV2 se preserva byte-a-byte."
    category: constraint
    applies_to: PublicSurface
    trigger: "cada extraccion de un ResponsibilityModule"
    logic: >
      IF una extraccion cambia el nombre, la firma o el constructor de cualquiera
      de los 57 metodos THEN la extraccion es invalida.
    violation_behavior: "los consumidores (8 routers + adapters DDD + data_sync_service + data_initializer_v2 + futmondo_service) dejan de compilar/invocar; rechazar."
    source: FR1.2

  - id: BR1.2
    statement: "El SQL extraido se envuelve verbatim en el infrastructure-adapter."
    category: constraint
    applies_to: DDDLayerComponent
    trigger: "al mover el cuerpo de un metodo fuera del god-file"
    logic: >
      IF el SQL (incluida la rama if db_type in ['postgresql','postgres'] else SQLite)
      se reescribe o se altera THEN violacion. El adapter envuelve el SQL tal cual.
    violation_behavior: "posible cambio de comportamiento observable; rechazar la extraccion."
    source: FR1.4

  - id: BR1.3
    statement: "Solo el infrastructure-adapter contiene SQL."
    category: constraint
    applies_to: DDDLayerComponent
    trigger: "diseno de cada modulo extraido"
    logic: >
      IF facade, orchestrator o domain-port contienen SQL o dependencias de
      framework/DB THEN violacion del patron de referencia.
    violation_behavior: "no cumple el molde DDD probado; rechazar."
    source: FR1.1

  - id: BR1.4
    statement: "No se anade ningun metodo nuevo al god-file durante la extraccion."
    category: constraint
    applies_to: PublicSurface
    trigger: "edicion de data_manager_v2.py"
    logic: "IF data_manager_v2.py crece en metodos THEN violacion (regla afirmada NEVER ampliar god-files)."
    violation_behavior: "rechazar; el god-file solo se vacia por extraccion, no se amplia."
    source: FR1.4

  - id: BR2.1
    statement: "Characterization-first: congelar el comportamiento antes de extraer."
    category: policy
    applies_to: ResponsibilityModule
    trigger: "antes de extraer un modulo"
    logic: >
      IF se extrae un modulo sin characterization tests verdes previos que
      aseveren su efecto THEN violacion del ciclo (congelar -> extraer -> verde).
    violation_behavior: "sin red de seguridad no hay prueba de equivalencia; bloquear la extraccion."
    source: FR2.1, FR2.2

  - id: BR2.2
    statement: "Los characterization tests aseveran el efecto, no la mera no-excepcion."
    category: validation
    applies_to: CharacterizationTest
    trigger: "escritura de un characterization test"
    logic: "IF un test es assert True o spec espejo (captura sin aseverar payload/estado/filas/fallo) THEN invalido."
    violation_behavior: "no congela comportamiento; rechazar el test."
    source: FR2.3

  - id: BR2.3
    statement: "Los tests usan los fakes in-memory, sin red/BD/credenciales reales."
    category: constraint
    applies_to: CharacterizationTest
    trigger: "ejecucion de characterization"
    logic: "IF un test abre red, BD real o usa credenciales/tokens reales THEN violacion (gitleaks escanea tests)."
    violation_behavior: "rechazar; usar _FakeInMemoryDB/_FakeCursor/fake_db."
    source: FR2.1, NFR6

  - id: BR3.1
    statement: "Equivalencia funcional estricta: comportamiento observable identico."
    category: constraint
    applies_to: ResponsibilityModule
    trigger: "tras extraer un modulo"
    logic: >
      IF tras la extraccion cambia alguna fila devuelta, efecto de escritura,
      excepcion o valor de retorno (incluido return None donde hoy ocurre)
      THEN violacion.
    violation_behavior: "los characterization tests fallan; revertir/corregir la extraccion."
    source: FR3.1

  - id: BR3.2
    statement: "El manejo de errores heredado se preserva verbatim (deuda diferida)."
    category: policy
    applies_to: ResponsibilityModule
    trigger: "al mover un metodo con except amplio/desnudo o return None"
    logic: >
      IF una extraccion cambia un except Exception, un except: desnudo o una
      senal return None del god-file THEN sale de alcance (OQ1); se preserva tal cual.
    violation_behavior: "cambio de comportamiento observable no autorizado; rechazar."
    source: FR3.2

  - id: BR3.3
    statement: "Los puntos de corrupcion por reemplazo de conjunto se preservan verbatim (deuda diferida)."
    category: policy
    applies_to: ResponsibilityModule
    trigger: "extraccion de delete_orphan_players u otro DELETE ... NOT IN / <> ALL"
    logic: >
      IF una extraccion eleva el reemplazo de conjunto al patron atomico en ESTE
      intent THEN sale de alcance (OQ2); se mueve verbatim, el riesgo queda registrado.
    violation_behavior: "cambio de comportamiento no autorizado; rechazar (diferir a OQ2)."
    source: FR3.3

  - id: BR4.1
    statement: "Los consumidores no se tocan."
    category: constraint
    applies_to: PublicSurface
    trigger: "cualquier paso del refactor"
    logic: >
      IF se modifican los adapters DDD existentes, los 8 routers consumidores o
      su SQL-en-router THEN fuera de alcance; siguen invocando el facade delgado.
    violation_behavior: "amplia blast radius; rechazar (FR4)."
    source: FR4.1, FR4.2

  - id: BR5.1
    statement: "El inventario y orden exactos de extraccion se cierran en Plan Approval."
    category: policy
    applies_to: ResponsibilityModule
    trigger: "antes de ejecutar la descomposicion"
    logic: >
      IF la ejecucion empieza sin inventario y orden (menor->mayor acoplamiento)
      confirmados en Plan Approval THEN bloquear.
    violation_behavior: "falta la confirmacion humana del plan; bloquear la generacion de codigo."
    source: FR5.1

  - id: BR6.1
    statement: "El piso de cobertura solo sube; la suite queda verde en cada paso."
    category: constraint
    applies_to: CharacterizationTest
    trigger: "cada paso de extraccion / gate de CI"
    logic: >
      IF se relaja --cov-fail-under o la suite backend/tests queda en rojo al
      fusionar THEN violacion. El characterization nuevo solo sube el piso por trinquete.
    violation_behavior: "un rojo nunca llega a main; bloquear el merge."
    source: NFR1, NFR2
```

## Resumen de reglas

| ID | Categoría | Invariante | Fuente |
|----|-----------|------------|--------|
| BR1.1 | constraint | Superficie pública byte-a-byte | FR1.2 |
| BR1.2 | constraint | SQL envuelto verbatim en el adapter | FR1.4 |
| BR1.3 | constraint | Sólo el adapter contiene SQL | FR1.1 |
| BR1.4 | constraint | No ampliar el god-file | FR1.4 |
| BR2.1 | policy | Characterization-first (congelar antes de extraer) | FR2.1, FR2.2 |
| BR2.2 | validation | Tests aseveran el efecto, no `assert True` | FR2.3 |
| BR2.3 | constraint | Fakes in-memory, sin red/BD/credenciales | FR2.1, NFR6 |
| BR3.1 | constraint | Equivalencia funcional estricta | FR3.1 |
| BR3.2 | policy | Error-handling heredado verbatim (diferido) | FR3.2 |
| BR3.3 | policy | Puntos de corrupción verbatim (diferido) | FR3.3 |
| BR4.1 | constraint | Consumidores y SQL-en-router intactos | FR4.1, FR4.2 |
| BR5.1 | policy | Inventario/orden exactos en Plan Approval | FR5.1 |
| BR6.1 | constraint | Cobertura sólo-sube; suite verde | NFR1, NFR2 |
