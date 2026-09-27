# Reglas de Negocio — Descomposición DDD de los god files (FR13)

> Intent `260927-god-files-refactor`, unidad única. Conversation language: Spanish.
>
> En este refactor las "reglas de negocio" son de dos clases: (1) **invariantes de preservación de comportamiento** que la caracterización debe congelar antes de mover código, y (2) **reglas de arquitectura DDD/SOLID** que gobiernan los límites de responsabilidad entre capas. Ambas son verificables (pass/fail) por tests o por inspección estructural. IDs estables `BRx.y`.

## Sources

- `inception/requirements-analysis/requirements.md` — FR2, FR2.1, FR2.2, FR2.3, FR3, FR4, NFR1, NFR2, NFR3.
- `codekb/futmondo-analytics/code-structure.md`, `code-quality-assessment.md` — superficie pública y patrón de referencia `prizes/`.
- Petición del usuario (DDD/SOLID/DRY).

```yaml
rules:
  # --- Grupo BR1: Preservación de comportamiento observable (characterization-first) ---
  - id: BR1.1
    statement: "Cada método público preservado de las fachadas conserva su firma y su efecto observable tras la extracción."
    category: constraint
    applies_to: "Fachadas DataManagerV2, AnalyticsService, DataSyncService, get_assistant_service()/ask()"
    trigger: "Un consumidor (router/sync/analytics/initializer) invoca un método público."
    logic: "IF se invoca un método de la superficie pública THEN el resultado observable es idéntico al del código pre-refactor (mismo payload, mismo estado persistido, mismo modo de fallo)."
    violation: "Regresión de comportamiento — bloquea el Bolt (test de caracterización en rojo)."
    source: [FR2.1, NFR2]
  - id: BR1.2
    statement: "Un repositorio produce exactamente el mismo resultado que el SQL inline que reemplaza."
    category: constraint
    applies_to: "Repositorios de infrastructure/ que sustituyen cursor.execute inline"
    trigger: "La fachada/servicio de aplicación consulta o persiste vía el repositorio."
    logic: "IF una operación de datos se migra de SQL inline a un método de repositorio THEN devuelve/persiste el mismo resultado para las mismas entradas."
    violation: "Divergencia de datos — bloquea el Bolt."
    source: [FR2.2, NFR2]
  - id: BR1.3
    statement: "El comportamiento debe estar caracterizado (congelado con tests) ANTES de mover el código de un seam."
    category: policy
    applies_to: "Todo seam extraído en un Bolt"
    trigger: "Inicio de la extracción de un dominio/seam."
    logic: "IF se va a mover un seam THEN existe caracterización de su comportamiento observable previa al primer movimiento; para data_manager, caracterización AMPLIA de su superficie pública (Q5=C previo)."
    violation: "Se detiene el Bolt hasta añadir la caracterización."
    source: [FR3, FR3.1, FR3.2]
  - id: BR1.4
    statement: "Los except: pass silenciados de data_manager (deuda preservada fuera de alcance) mantienen su comportamiento actual: se mueven textualmente con su método, sin caracterizar la rama silenciada ni cambiar su semántica."
    category: constraint
    applies_to: "~29 except: pass de data_manager_v2.py (y equivalentes)"
    trigger: "Extracción de un método que contiene un except: pass preservado."
    logic: "IF un método con except: pass se reubica THEN el bloque se traslada verbatim (misma excepción capturada, mismo silenciado); NO se caracteriza la rama de error silenciada (es deuda fuera de alcance) NI se convierte en manejo tipado en este intent. La caracterización cubre el efecto observable del camino feliz del método, no la rama silenciada."
    violation: "Cambiar la semántica del silenciado (p. ej. propagar donde antes se tragaba) — rechazo: introduce cambio de comportamiento no autorizado."
    source: [FR2.1, NFR2]

  # --- Grupo BR5: Restricciones afirmadas del proyecto (coste, formato) ---
  - id: BR5.1
    statement: "La descomposición no introduce dependencias de pago ni tooling con coste recurrente; coste 0 €."
    category: constraint
    applies_to: "Todo el intent"
    trigger: "Introducción de una librería o servicio."
    logic: "IF se necesita una librería nueva THEN es OSS, fijada a versión exacta, dentro de tiers gratuitos; no se prevé ninguna (stdlib suficiente)."
    violation: "Coste recurrente — rechazo."
    source: [NFR4]
  - id: BR5.2
    statement: "No se reformatea en masa (ruff format / Prettier) los ficheros brownfield; solo los módulos nuevos o de forma quirúrgica."
    category: policy
    applies_to: "Ficheros god existentes tocados"
    trigger: "Movimiento/edición de código en un god file."
    logic: "IF se edita un fichero brownfield THEN no se aplica reformateo masivo; se formatean solo los módulos nuevos extraídos."
    violation: "Diff inflado / avisos preexistentes expuestos — rechazo (regla afirmada)."
    source: [FR2, NFR1]

  # --- Grupo BR2: Límites de responsabilidad DDD/SOLID ---
  - id: BR2.1
    statement: "La capa domain/ no depende de infrastructure/ ni de framework (FastAPI, driver de BD)."
    category: constraint
    applies_to: "Módulos bajo <contexto>/domain/"
    trigger: "Import en un módulo de dominio."
    logic: "IF un módulo vive en domain/ THEN no importa infrastructure/, psycopg2/cursor, ni FastAPI (Dependency Inversion)."
    violation: "Violación de capas — rechazo en revisión."
    source: [NFR1]
  - id: BR2.2
    statement: "El SQL crudo vive exclusivamente en los repositorios de infrastructure/."
    category: constraint
    applies_to: "Todos los bounded contexts"
    trigger: "Aparición de cursor.execute / SQL string."
    logic: "IF hay SQL crudo THEN está dentro de una implementación de repositorio en infrastructure/; nunca en application/, domain/, ni en un router (no SQL-en-router)."
    violation: "Anti-patrón SQL fuera de sitio — rechazo en revisión."
    source: [FR2.2]
  - id: BR2.3
    statement: "La capa application/ depende de la INTERFAZ de repositorio (domain/), no de su implementación."
    category: constraint
    applies_to: "Servicios de aplicación"
    trigger: "Un servicio de aplicación necesita datos."
    logic: "IF un servicio de aplicación accede a datos THEN lo hace a través de la abstracción de repositorio inyectada, no instanciando la implementación concreta (DIP)."
    violation: "Acoplamiento a infraestructura — rechazo en revisión."
    source: [FR2.3, NFR3]
  - id: BR2.4
    statement: "Cada repositorio encapsula exactamente un agregado (SRP)."
    category: constraint
    applies_to: "Repositorios"
    trigger: "Definición de un repositorio."
    logic: "IF se define un repositorio THEN cubre un único agregado de entities.md; no hay repositorio 'god' ni SqlGateway monolítico."
    violation: "Responsabilidad difusa — rechazo en revisión."
    source: [FR2.2]
  - id: BR2.5
    statement: "La fachada pública no contiene lógica de negocio ni SQL: solo delega."
    category: constraint
    applies_to: "Clases fachada (application service delgado)"
    trigger: "Invocación de un método de la fachada."
    logic: "IF un método de la fachada se ejecuta THEN delega en un servicio de aplicación/repositorio; no ejecuta SQL ni cálculo de negocio propio."
    violation: "Fachada gorda — rechazo en revisión."
    source: [FR2, FR2.1]
  - id: BR2.6
    statement: "Las dependencias se inyectan por constructor con defaults que preservan el comportamiento actual (OCP)."
    category: policy
    applies_to: "Fachadas y servicios de aplicación"
    trigger: "Construcción de una fachada/servicio."
    logic: "IF se construye una fachada/servicio sin argumentos THEN usa las implementaciones reales por defecto (comportamiento actual); un test puede inyectar dobles sin monkeypatch."
    violation: "No testeable por inyección — se revisa el diseño del seam."
    source: [FR2.3, NFR3]

  # --- Grupo BR3: DRY y transaccionalidad ---
  - id: BR3.1
    statement: "El mapeo fila→entidad se centraliza y no se duplica entre repositorios (DRY)."
    category: policy
    applies_to: "Repositorios de infrastructure/"
    trigger: "Conversión de filas de BD a entidades."
    logic: "IF varios repositorios mapean la misma forma de fila THEN comparten el helper de mapeo en vez de duplicarlo."
    violation: "Duplicación — se refactoriza el mapeo."
    source: [FR2.2]
  - id: BR3.2
    statement: "Las operaciones de reemplazo de conjuntos usan escritura transaccional atómica, replicando team_prizes_writer."
    category: constraint
    applies_to: "Repositorios con operaciones DELETE+INSERT de reemplazo"
    trigger: "Reemplazo de un conjunto de filas (p. ej. caches, rankings)."
    logic: "IF una operación reemplaza un conjunto THEN es atómica (todo-o-nada); nunca deja estado a medias ante fallo (patrón de referencia prizes/)."
    violation: "Riesgo de corrupción — bloquea el Bolt."
    source: [FR2, NFR2]

  # --- Grupo BR4: Alcance / secuenciación ---
  - id: BR4.1
    statement: "Las oleadas siguen el orden de riesgo creciente: analytics → assistant → sync → data_manager."
    category: policy
    applies_to: "Plan de descomposición (Bolts)"
    trigger: "Secuenciación de los Bolts."
    logic: "IF se planifican los Bolts THEN el primero es analytics y el último data_manager."
    violation: "Orden inseguro — se corrige en delivery-planning."
    source: [FR1.1]
  - id: BR4.2
    statement: "Cada Bolt cierra con comportamiento preservado (suites verdes) + al menos un seam extraído."
    category: policy
    applies_to: "Cada Bolt"
    trigger: "Cierre de un Bolt."
    logic: "IF se cierra un Bolt THEN la suite de caracterización + la suite existente están verdes Y ≥1 dominio/seam quedó extraído tras la fachada."
    violation: "Bolt incompleto — no se aprueba."
    source: [FR4, FR4.1, FR4.2]
```

## Resumen de reglas

| ID | Categoría | Resumen | Fuente |
|----|-----------|---------|--------|
| BR1.1 | constraint | Firma/efecto observable de la superficie pública preservados | FR2.1, NFR2 |
| BR1.2 | constraint | Repositorio ≡ mismo resultado que el SQL inline previo | FR2.2, NFR2 |
| BR1.3 | policy | Caracterización antes de mover el seam (amplia para data_manager) | FR3 |
| BR1.4 | constraint | except: pass preservados se mueven verbatim, sin cambiar semántica | FR2.1, NFR2 |
| BR2.1 | constraint | domain/ sin dependencia de infra/framework | NFR1 |
| BR2.2 | constraint | SQL solo en repositorios de infrastructure/ | FR2.2 |
| BR2.3 | constraint | application/ depende de la interfaz, no de la implementación (DIP) | FR2.3 |
| BR2.4 | constraint | Un repositorio = un agregado (SRP) | FR2.2 |
| BR2.5 | constraint | Fachada solo delega (sin lógica ni SQL) | FR2, FR2.1 |
| BR2.6 | policy | Inyección por constructor con defaults (OCP), testeable sin monkeypatch | FR2.3, NFR3 |
| BR3.1 | policy | Mapeo fila→entidad centralizado (DRY) | FR2.2 |
| BR3.2 | constraint | Reemplazo transaccional atómico (patrón prizes/) | FR2, NFR2 |
| BR4.1 | policy | Orden de oleadas por riesgo creciente | FR1.1 |
| BR4.2 | policy | Cierre de Bolt: suites verdes + ≥1 seam extraído | FR4 |
| BR5.1 | constraint | Sin dependencias de pago; coste 0 € | NFR4 |
| BR5.2 | policy | Sin reformateo masivo brownfield (quirúrgico/módulos nuevos) | FR2, NFR1 |
