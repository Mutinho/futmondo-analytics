# Architecture Decision Records — Domain Design (FR1/FR5)

> Registro durable de las decisiones significativas de diseño de dominio de este
> intent. Cada ADR sigue la estructura exigida por las guardarraíles de Inception:
> Context, Decision, Consequences, Alternatives Rejected. Trazan a las preguntas
> Q1–Q6 confirmadas y a los requisitos FR/NFR/C.

## Sources

- domain-design-questions.md (Q1–Q6) [Q1] [Q2] [Q3] [Q4] [Q5] [Q6]
- requirements.md (FR1.1–FR1.6, FR5.1–FR5.2, NFR1–NFR5, C1–C5) [scope]
- team-practices.md, project.md, architecture.md, component-inventory.md [scope] [desc]

---

## ADR-001: Descomposición en repositorios + fachadas de servicio por dominio de estado

### Context
El intent debe hacer durable dos estados de proceso (sesión Futmondo, tareas de
sync) sin ampliar el patrón de SQL-en-router ni tocar los god-files existentes
(C3), y con un patrón de test basado en fakes de la capa de persistencia
(team-practices). Hay lógica de dominio no trivial (TTL 12h, locks por usuario,
reconstrucción idempotente, unicidad de tarea, interrupción por reinicio) que
convive con acceso a datos.

### Decision
Adoptar una descomposición por dominio de estado con dos capas separadas:
`SessionService`/`TaskService` (lógica de dominio) por encima de
`SessionRepository`/`TaskRepository` (persistencia estrecha sobre `db_connection`).
[Q1-C]

### Consequences
- (+) Alta cohesión: la lógica de negocio (change rate por reglas) y el acceso a
  datos (change rate por esquema) evolucionan por separado.
- (+) Testable con fakes del repositorio en memoria, sin Neon real (team-practices).
- (+) Respeta C3: la lógica no se filtra a los routers.
- (−) Más piezas que una solución monolítica; algo más de indirección.

### Alternatives Rejected
- **`StateStore` genérico único (Q1-B):** acopla sesión y tareas —dos dominios que
  cambian por razones distintas— en una interfaz común; baja cohesión.
- **Repositorios sin fachada de servicio (Q1-A):** deja sin hogar la lógica de
  reconstrucción/idempotencia, que tendería a filtrarse a los routers (contra C3).

---

## ADR-002: Rehidratación de sesión idempotente disparada desde refresh y primer uso

### Context
Tras un reinicio, una petición puede llegar por dos caminos: la recarga de página
(`/auth/refresh` con cookie) o la primera llamada a `/api/v1/*` con un access token
aún válido. Hoy el segundo camino produce un 403 opaco en
`_helpers.get_user_futmondo_client` (architecture.md). FR1.2 pide reconstrucción
transparente cuando exista medio de re-auth; FR1.3 pide un error accionable cuando
no.

### Decision
Ubicar la lógica de reconstrucción en `SessionService.ensureSession` (operación
idempotente) e invocarla desde **ambos** disparadores: `/auth/refresh` (AuthRoutes)
y el primer uso del cliente (FutmondoClientAccessor). [Q2-C]

### Consequences
- (+) Cubre los dos caminos reales de entrada tras un reinicio; elimina el 403 opaco.
- (+) Idempotencia: la misma operación desde dos disparadores no duplica lógica ni
  produce estados inconsistentes.
- (−) Dos puntos de invocación a mantener; se mitiga porque ambos delegan en una
  única operación.

### Alternatives Rejected
- **Solo en `/auth/refresh` (Q2-B):** una petición con Bearer válido no pasa por
  refresh y seguiría fallando.
- **Solo en el primer uso del cliente (Q2-A):** pierde la oportunidad de rehidratar
  temprano en la recarga.

---

## ADR-003: Componente de seguridad `CredentialProtection` como frontera de FR5

### Context
El tratamiento de la credencial Futmondo es la decisión de seguridad crítica del
intent, sujeta a una regla dura (project.md: NUNCA contraseña en claro, ni en
memoria ni en BD; FR5.1). FR5.2 deja explícitamente la elección fina (no persistir
vía re-auth vs. cifrar en reposo) para la etapa de diseño posterior.

### Decision
Modelar un componente `CredentialProtection` con interfaz estrecha, dueño de la
entidad `ProtectedCredential`, del que depende `SessionService` (por llamada, para
consultar el medio de re-auth). La `UserSession` (dueña `SessionRepository`)
referencia la `ProtectedCredential` como **referencia de entidad**
(`references.entity`), no como arista de llamada de componente. La `UserSession`
deja de portar el `password`. La elección fina FR5.2 se difiere a Functional/NFR
design sin mover la frontera. [Q3-A] [Q4-B]

### Consequences
- (+) Hace explícito y auditable el límite de seguridad (make the implicit explicit).
- (+) Design for change: cifrado-en-reposo vs. re-auth se decide luego sin rediseñar
  fronteras.
- (+) Refuerza FR5.1: el `password` en claro deja de ser atributo de la sesión.
- (−) Introduce una entidad y un componente adicionales; se justifica por la criticidad
  de seguridad.

### Alternatives Rejected
- **Sin componente propio (Q3-B):** el tratamiento de credencial dentro del repositorio
  de sesión diluye la responsabilidad de seguridad y la hace difícil de auditar.
- **Fijar ya "no persistir la contraseña" (Q3-C):** comprometería la implementación fina
  que FR5.2 reserva para diseño; se conserva como alternativa en la decisión fina.

---

## ADR-004: Almacenes en memoria conservados como caché best-effort (BD fuente de verdad)

### Context
`SessionStore` y `TaskManager` son hoy singletons de proceso y la fuente de verdad.
El intent exige caracterizar (congelar con tests) su comportamiento observable antes
de refactorizar (C5), mantener la suite en verde (NFR4) y no degradar de forma
perceptible el camino de sesión (NFR2).

### Decision
Conservar `SessionStore`/`TaskManager` como **caché de proceso best-effort** delante
de los servicios (lectura: memoria → BD; escritura: BD + memoria), degradando su rol:
la fuente de verdad pasa a ser el repositorio/BD; el caché nunca es autoritativo.
[Q5-A]

### Consequences
- (+) Cambios mínimos en los llamadores existentes (auth/routes, _helpers, sync.py);
  facilita preservar el comportamiento observable (C5) y la suite verde (NFR4).
- (+) Protege la latencia del camino caliente de sesión (NFR2).
- (−) Coherencia caché↔BD a gestionar (invalidez/escritura ordenada); se acota con la
  regla "BD autoritativa, caché best-effort".

### Alternatives Rejected
- **Sustituir los almacenes por acceso directo a BD (Q5-B):** fuerza una lectura a Neon
  en cada petición del camino caliente (NFR2) y complica preservar el comportamiento
  observable exigido por C5.

---

## ADR-005: La base de datos como autoridad de concurrencia (robustez multi-instancia)

### Context
NFR5 pide no asumir instancia única aunque `fly.toml` fije min=max=1. Un lock en
memoria de proceso no coordina dos instancias ni sobrevive a un reinicio —justo el
fallo que ataca el intent—. FR1.6 exige rechazar (409) una segunda tarea activa, y
FR1.5 marcar como interrumpidas las tareas en curso tras un reinicio.

### Decision
Resolver la unicidad "una tarea activa por usuario" (FR1.6) y los locks de
concurrencia contra el estado **persistido** (condición/constraint en BD), no contra
un lock en memoria. El caché en memoria es best-effort y nunca la autoridad. [Q6-A]

### Consequences
- (+) Control de concurrencia correcto aun con reinicio o escalado futuro (NFR5).
- (+) Consistente con ADR-004 (BD fuente de verdad).
- (−) La comprobación de unicidad implica un acceso a BD; aceptable porque no está en
  el camino caliente de lectura de sesión.

### Alternatives Rejected
- **Locks en memoria de proceso (Q6-B):** no coordina multi-instancia ni sobrevive a
  reinicio; contradice NFR5 y el propio objetivo del intent.
