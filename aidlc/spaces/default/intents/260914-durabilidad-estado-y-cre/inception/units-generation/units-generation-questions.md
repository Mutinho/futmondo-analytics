# Units Generation — Preguntas de decomposición

> Etapa de Inception (arquitecto + delivery). Agrupamos los componentes del diseño
> de dominio en **unidades de trabajo** con un DAG de dependencias (solo topología;
> el orden de entrega/Bolts es de Delivery Planning 2.9). Responde en el tag
> `[Answer]:`. `X. Other (please specify)` siempre disponible.

## Sources

- domain-design/components.md — 5 nuevos (SessionService, SessionRepository, TaskService, TaskRepository, CredentialProtection) + 5 re-cableados (SessionStore, TaskManager, AuthRoutes, FutmondoClientAccessor, SyncEndpoints) [scope]
- domain-design/decisions.md — ADR-001..005 (fronteras, dirección única de caché, autoridad BD) [scope]
- requirements-analysis/requirements.md — FR1.1–FR1.6, FR5.1–FR5.2, C1–C5, NFR5 [scope]
- team-practices.md — capa de persistencia estrecha; monolito modular; despliegue on-merge a Fly.io [scope]

---

## Q1 — Estrategia de frontera de las unidades

¿Cómo agrupamos los componentes en unidades de trabajo?

- A. **Por dominio de estado**: Unidad "sesión y credenciales" (SessionService, SessionRepository, CredentialProtection, SessionStore + re-cableo de AuthRoutes/FutmondoClientAccessor) y Unidad "tareas de sync" (TaskService, TaskRepository, TaskManager + re-cableo de SyncEndpoints). Dos unidades alineadas con los dos estados durables (FR1 sesión vs FR1 tareas).
- B. **Una unidad de infraestructura de persistencia compartida** (SessionRepository + TaskRepository + capa `stores/`) más dos unidades de dominio encima (sesión, tareas). Tres unidades: la de persistencia es fundacional.
- C. **Una sola unidad monolítica** con todo el trabajo de durabilidad (todos los componentes), dado que es una intervención acotada sobre un monolito modular ya desplegado.

[Answer]: A

---

## Q2 — Granularidad

¿Grano fino (más unidades, más límites de test/deploy) o grano grueso (menos unidades, menos coordinación)?

- A. **Grano grueso**: pocas unidades (1–3), coherente con una intervención acotada sobre un backend existente y un equipo pequeño; menos overhead de coordinación.
- B. **Grano fino**: separar cada servicio/repositorio en su propia unidad para máxima independencia de test/deploy.

[Answer]: A

---

## Q3 — Contratos e integración entre unidades

Si hay más de una unidad, ¿qué las conecta y cómo?

- A. **Contrato de credenciales como frontera explícita**: la unidad de credenciales (CredentialProtection) expone una interfaz estrecha que consume la unidad de sesión; el resto de interacción es intra-unidad. La sesión y las tareas comparten solo la capa de persistencia (`db_connection`), no un contrato de dominio entre sí.
- B. **Sin contratos formales entre unidades**: si quedan varias, comparten solo el abstractor de BD existente y no exponen APIs nuevas entre ellas.

[Answer]: B

---

## Q4 — Dependencias y paralelismo

¿Qué estructura de dependencias modelamos en el DAG?

- A. **Sesión y tareas independientes** (sin dependencia entre ellas; pueden construirse en paralelo); credenciales como dependencia previa de la unidad de sesión (la sesión necesita el contrato de credencial para reconstruir). Refleja el diseño: SessionService depende de CredentialProtection.
- B. **Cadena estricta**: una unidad fundacional (persistencia/credenciales) primero, y el resto en secuencia.

[Answer]: A

---

## Q5 — Modelo de despliegue por unidad

Coherente con el monolito modular ya desplegado (C1, sin reescrituras grandes).

- A. **Despliegue embebido en el backend existente**: todas las unidades se despliegan como parte del único servicio `futmondo-api` (no hay despliegue independiente por unidad). El DAG describe orden de construcción/integración, no artefactos desplegables separados.
- B. **Despliegue independiente por unidad** (nuevos servicios Fly.io) — descartable por coste 0 € y restricción de no multiplicar despliegues, pero se plantea por completitud.

[Answer]: A

---

## Consolidated Summary Confirmation

Plan de decomposición que se materializará en los artefactos (`unit-of-work.md`,
`unit-of-work-dependency.md`, `unit-of-work-story-map.md`, `traceability.json`):

**Estrategia de frontera:** por dominio de estado (Q1-A), grano grueso (Q2-A).

**Unidades (2):**

| Unit ID | Directory | kind | Componentes | Complejidad |
|---------|-----------|------|-------------|-------------|
| U1 | u1-durable-session | service | SessionService, SessionRepository, CredentialProtection, SessionStore (caché) + re-cableo de AuthRoutes y FutmondoClientAccessor | M |
| U2 | u2-durable-sync-tasks | service | TaskService, TaskRepository, TaskManager (caché) + re-cableo de SyncEndpoints | M |

**DAG de dependencias:** sin aristas — U1 y U2 son **independientes** (`depends_on: []` ambas) (Q4-A). Comparten solo el abstractor `db_connection` preexistente; ningún contrato de dominio entre ellas (Q3-B). Construibles en paralelo; el orden económico lo decide Delivery Planning (2.9).

**Modelo de despliegue:** ambas embebidas en el servicio `futmondo-api` existente; sin despliegue independiente (Q5-A). El DAG describe orden de construcción/integración, no artefactos desplegables.

**Notas de frontera:** la interfaz de `CredentialProtection` (`protect`/`resolve`/`canReauthenticate`) es un límite explícito **intra-U1**, cuya formalización fina llega en Contract Design (2.8); no es una arista del DAG.

**Cobertura de FR (sin stories.md, se enumeran FR):** FR1.1/FR1.2/FR1.3/FR5.1/FR5.2 → U1; FR1.4/FR1.5/FR1.6 → U2. NFR5 (multi-instancia) atraviesa ambas vía autoridad en BD.

[Answer]: Looks correct
