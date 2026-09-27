# Preguntas de Diseño Funcional — FR13 Descomposición de god files

> Intent `260927-god-files-refactor`, scope `refactor`, depth Minimal. Full mode (unidad única). Conversation language: Spanish.
>
> units-generation y domain-design se omiten por diseño en refactor; se trabaja desde `requirements.md` (FR1–FR4, NFR1–NFR4) y el codekb (`code-structure.md`, `code-quality-assessment.md`), tratando la estructura de código existente como el domain design de facto. Estas preguntas fijan la **forma de la descomposición** antes de escribir los artefactos de diseño. Lo ya afirmado (characterization-first, preservar superficie pública, patrón `prizes/`, no ampliar god files, no reformatear en masa) no se re-pregunta.

## Q1 — Ubicación y convención de los módulos extraídos

El precedente `prizes/` es un subpaquete bajo `backend/app/services/`. ¿Replicamos esa convención para cada dominio extraído?

- A. **Subpaquete por god file**: `backend/app/services/<servicio>/` (p. ej. `analytics/`, `assistant/`, `sync/`, `data_manager/`) con un módulo por dominio dentro y la fachada re-exportada desde el nombre original. Aísla cada descomposición y espeja `prizes/`.
- B. **Subpaquetes por dominio transversal**: agrupar por agregado de datos (p. ej. `repositories/players.py`, `repositories/transactions.py`) compartidos entre servicios, no por god file.
- C. **Módulos planos hermanos**: ficheros nuevos hermanos en `services/` sin subpaquete (p. ej. `analytics_trends.py`), la fachada importa de ellos.
- X. Other (please specify)

[Answer]: A (con estructura DDD interna). Subpaquete por god file como **bounded context** bajo `backend/app/services/<contexto>/` (`analytics/`, `assistant/`, `sync/`, `data_manager/`), y dentro de cada uno separación por capas DDD: `domain/` (entidades/agregados/value objects + interfaces de repositorio, sin dependencia de infraestructura), `application/` (servicios de aplicación que orquestan casos de uso), `infrastructure/` (implementaciones de repositorio con el SQL). La fachada con el nombre original se re-exporta desde el módulo/paquete para no romper import paths. Espeja y generaliza el precedente `prizes/`. (Recomendación A refinada con la petición del usuario: "lo más DDD posible, separación de responsabilidades, SOLID, DRY".)

## Q2 — Modelo de acceso a datos extraído

Los god files tienen SQL crudo inline (94 + 42 + 2 `cursor.execute`). ¿Qué forma toma la capa de datos al extraerla?

- A. **Repositorios por agregado**: una clase/módulo repositorio por agregado (players, transactions, clauses, standings, …) que encapsula su SQL y recibe la conexión/cursor; la lógica de negocio consume el repositorio, no `cursor.execute`. Espeja `team_prizes_writer`.
- B. **Un `SqlGateway`/query-helpers único**: envolver todos los `cursor.execute` en helpers de bajo nivel sin trocear por agregado todavía (más conservador, menos módulos).
- C. **Mixto por god file**: repositorios por agregado donde el dominio es claro (data_manager); gateway/helpers donde el SQL es incidental (assistant `_ctx_*`).
- X. Other (please specify)

[Answer]: A (patrón repositorio DDD con inversión de dependencias). Un **repositorio por agregado** (players, teams/users, transactions, clauses, standings, rosters, sync-metadata, assistant-usage, …): la **interfaz abstracta** (Protocol/ABC) vive en `domain/` y la **implementación** con SQL crudo en `infrastructure/`; la capa de aplicación depende de la abstracción, no del detalle (DIP de SOLID). Un helper de mapeo fila→entidad compartido evita duplicación (DRY). Espeja `team_prizes_writer` (writer transaccional atómico) elevándolo a interfaz de repositorio. Sin `SqlGateway` monolítico: cada repositorio tiene una única responsabilidad (SRP). (Recomendación A con orientación DDD/SOLID.)

## Q3 — Preservación de la fachada pública

¿Cómo se preserva exactamente la superficie pública (`DataManagerV2.*`, `AnalyticsService.get_*`, etc.) para que los routers no cambien?

- A. **Fachada delega (thin wrapper)**: la clase original conserva sus métodos públicos con la misma firma; cada método delega en el módulo/repositorio extraído. Import paths de los routers intactos.
- B. **Re-export de símbolos**: mover la clase al subpaquete y re-exportar el nombre desde el módulo original (`from .analytics.service import AnalyticsService`).
- C. **Ambas según el caso**: delegación para clases con estado/DI (analytics `self.dm`, assistant), re-export para funciones puras.
- X. Other (please specify)

[Answer]: A (fachada = application service delgado que delega, con inyección de dependencias). La clase original (`DataManagerV2`, `AnalyticsService`, `DataSyncService`, assistant vía `get_assistant_service()`) conserva EXACTAMENTE sus métodos públicos y firmas; cada método delega en el servicio de aplicación / repositorio del bounded context. Las dependencias (repositorios, config) se **inyectan** por constructor con defaults que preservan el comportamiento actual (Open/Closed + DIP), de modo que los tests puedan sustituir dobles sin monkeypatch — generalizando el seam `self.dm` ya probado en `test_analytics_service.py`. Import paths de los routers intactos vía re-export. (Recomendación A con orientación SOLID.)

## Q4 — Qué documentar como "entidades" y "reglas" en este refactor

En un refactor no hay entidades de negocio nuevas. ¿Cómo interpretamos los artefactos `entities.md` y `rules.md`?

- A. **entities = agregados de datos existentes** (los grupos de tablas que cada repositorio encapsulará: players, teams/users, transactions, clauses, standings, rosters, sync-metadata, assistant-usage) y **rules = invariantes de preservación de comportamiento** (BR: "la fachada X preserva la firma/efecto observable de método Y"; "el repositorio Z produce el mismo resultado que el SQL inline previo"). Documenta el contrato que la caracterización congela.
- B. **Minimalista**: `entities.md` y `rules.md` como stubs que remiten al codekb; concentrar el diseño en `functional-spec.md` (seams, orden de extracción, mapa fachada→módulo).
- X. Other (please specify)

[Answer]: A (modelado explícito DDD). `entities.md` documenta los **agregados** y sus raíces por bounded context (Player, Team/User, Transaction, Clause, Standing, Roster, SyncMetadata, AssistantUsage…), con value objects donde aporten (p. ej. identificadores, importes), atributos y relaciones — el modelo de datos existente reexpresado en lenguaje DDD (lenguaje ubicuo). `rules.md` documenta como `BRx.y`: (1) **invariantes de preservación de comportamiento** ("la fachada preserva firma/efecto observable"; "el repositorio produce el mismo resultado que el SQL inline previo") que la caracterización congela, y (2) los **límites de responsabilidad** entre capas (domain no depende de infraestructura; el SQL solo vive en repositorios; la fachada no contiene lógica de negocio). `functional-spec.md` lleva el mapa de seams, el orden de oleadas y los flujos de delegación. (Recomendación A con orientación DDD.)

## Q5 — Alcance del diseño en este Bolt (unidad única)

El intent es multi-oleada pero este workflow corre como unidad única (no hubo units-generation). ¿El diseño funcional cubre el plan de descomposición de los cuatro god files, o solo la primera oleada (`analytics_service`)?

- A. **Diseño del plan completo de los cuatro**, con el mapa de seams por god file y el orden (analytics → assistant → sync → data_manager), dejando el detalle fino de cada oleada para code-generation. Coherente con FR1 (gated por dominio).
- B. **Solo la primera oleada (`analytics_service`)** en profundidad; el resto se diseña en intents/Bolts posteriores.
- X. Other (please specify)

[Answer]: A. Diseño del plan completo de los cuatro bounded contexts, con el mapa de seams por god file y el orden de oleadas (analytics → assistant → sync → data_manager), dejando el detalle de implementación de cada oleada para code-generation. Coherente con FR1 (gated por dominio). (Recomendación A.) La primera oleada (`analytics`) se especifica con más detalle por ser la que valida el patrón DDD end-to-end.

## Consolidated Summary Confirmation

- **Estructura (Q1)**: bounded context por god file bajo `services/<contexto>/` con capas DDD `domain/` (agregados + interfaces de repositorio), `application/` (servicios de caso de uso), `infrastructure/` (repositorios con SQL); fachada re-exportada.
- **Acceso a datos (Q2)**: repositorio por agregado — interfaz en `domain/`, implementación SQL en `infrastructure/` (DIP); sin `SqlGateway` monolítico (SRP); mapeo fila→entidad compartido (DRY); writer transaccional atómico como el de `prizes/`.
- **Fachada (Q3)**: application service delgado que delega, firmas públicas y import paths intactos, dependencias inyectadas por constructor con defaults que preservan comportamiento (OCP/DIP; sustituibles por dobles sin monkeypatch).
- **Artefactos (Q4)**: entities = agregados/value objects DDD (lenguaje ubicuo); rules = invariantes de preservación de comportamiento + límites de responsabilidad entre capas; functional-spec = seams + orden + flujos de delegación.
- **Alcance (Q5)**: plan completo de los cuatro bounded contexts, orden analytics → assistant → sync → data_manager; detalle de implementación a code-generation.
- **Restricción dura transversal**: todo el diseño DDD/SOLID/DRY se subordina a **preservar el comportamiento observable** (characterization-first); no se cambia ningún contrato de la superficie pública ni de los endpoints.

Does this all look correct before I generate the functional design artifacts?

[Answer]: Looks correct
