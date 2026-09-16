# Domain Design — Preguntas de diseño

> Etapa de Inception (arquitecto). El objetivo es fijar las fronteras de los
> **bloques lógicos de software** (componentes que escribimos) para la durabilidad
> de sesión/tareas (FR1) y el tratamiento de credenciales (FR5). No se decide aquí
> topología de despliegue, stack ni patrones NFR. Responde en el tag `[Answer]:`
> de cada pregunta. `X. Other (please specify)` siempre disponible.

## Sources

- requirements.md (FR1.1–FR1.6, FR5.1–FR5.2, NFR1–NFR5, C1–C5) [scope]
- codekb: architecture.md, component-inventory.md (SessionStore, TaskManager, token_store, db_connection) [desc]
- team-practices.md (capa de persistencia estrecha `stores/`; sin ampliar SQL-en-router) [scope]
- project.md (NEVER contraseña en claro ni en memoria ni en BD; coste 0 €) [scope]

---

## Q1 — Frontera de la persistencia de estado

¿Cómo modelamos el nuevo bloque(s) de persistencia durable, respetando C3 (capa
estrecha tipo `stores/`, sin ampliar SQL-en-router ni tocar los god-files)?

- A. **Un componente de persistencia por dominio de estado**: un `SessionRepository`
  (sesión Futmondo) y un `TaskRepository` (tareas de sync), cada uno dueño de su
  tabla y su SQL, ambos sobre el abstractor `db_connection` existente. Los almacenes
  en memoria (`SessionStore`/`TaskManager`) pasan a delegar en su repositorio.
- B. **Un único componente `StateStore` genérico** que persiste ambos tipos de estado
  (sesión y tareas) con una interfaz común.
- C. **Repositorios + fachada de dominio**: repositorios por estado (como A) más un
  componente de servicio de sesión/tareas que encapsula la lógica (TTL, locks,
  reconstrucción, idempotencia) por encima del repositorio.

[Answer]: C

---

## Q2 — Reconstrucción de la sesión Futmondo (FR1.2/FR1.3)

¿Qué componente es dueño de la lógica de reconstruir (o no) la sesión Futmondo tras
un reinicio, y dónde se dispara?

- A. **Extender el flujo de acceso al cliente Futmondo** (`get_user_futmondo_client`):
  al no hallar sesión en memoria, un `SessionService` intenta reconstruirla desde el
  estado persistido (según lo que FR5.2 conserve); si no puede, devuelve el error claro
  (FR1.3, 401 accionable).
- B. **Reconstrucción en `/auth/refresh`**: el refresh de JWT también rehidrata la
  sesión Futmondo cuando sea posible.
- C. **Ambos puntos** (refresh y primer uso del cliente) delegando en el mismo
  `SessionService`, para que la rehidratación sea idempotente venga de donde venga.

[Answer]: C

---

## Q3 — Tratamiento de credenciales (FR5.1/FR5.2) a nivel de diseño de dominio

FR5.2 deja la elección concreta (no persistir vía re-auth vs. cifrar en reposo) para
diseño. A nivel de **frontera de componentes** (no de implementación fina), ¿qué
enfoque de propiedad modelamos ahora?

- A. **Componente de credenciales explícito** (`CredentialProtection` / `SecretVault`):
  un bloque dueño de proteger la credencial (cifrar/descifrar en reposo o gestionar el
  medio de re-auth), del que dependen `SessionService`/`SessionRepository`. La decisión
  fina (cifrado vs. no-persistir) se concreta en Functional/NFR design, pero la frontera
  queda aislada aquí.
- B. **Sin componente propio**: el tratamiento de la credencial vive dentro de
  `SessionRepository`/`SessionService` como responsabilidad interna, sin bloque separado.
- C. **Componente de credenciales + no persistir la contraseña** (re-auth): modelamos el
  bloque de credenciales pero orientado a NO guardar `password` (derivar/re-autenticar),
  dejando el cifrado en reposo como alternativa registrada en ADR.

[Answer]: A

---

## Q4 — Propiedad de la entidad de sesión y de tarea

Cada entidad debe tener exactamente un componente dueño. ¿Confirmas esta asignación?

- A. **`UserSession`** (email, user_id, token, TTL, referencia protegida a credencial)
  → dueño `SessionRepository`; **`SyncTask`** (id, estado, progreso, timestamps, flag
  "interrumpida-por-reinicio") → dueño `TaskRepository`. Ninguna entidad nueva de dominio
  más allá de estas dos.
- B. Igual que A, pero añadiendo una entidad separada para el material de credencial
  protegido (p. ej. `ProtectedCredential`) con su propio dueño (el componente de Q3).

[Answer]: B

---

## Q5 — Interacción y no-regresión con los componentes existentes

¿Cómo se integran los nuevos bloques con `SessionStore`/`TaskManager` actuales, dado
C5 (caracterizar antes de refactorizar) y NFR4 (suite en verde)?

- A. **Los almacenes en memoria se conservan como caché de proceso** delante del
  repositorio (lectura: memoria→BD; escritura: BD + memoria), minimizando cambios en
  los llamadores (`auth/routes`, `_helpers`, `sync.py`) y latencia en el camino de sesión.
- B. **Los almacenes en memoria se sustituyen** por acceso directo al repositorio
  (la BD pasa a ser la fuente de verdad; sin caché en memoria).
- C. **Híbrido explícito**: sesión con caché en memoria (camino caliente, A) y tareas
  directamente sobre el repositorio (B), porque el polling de tareas tolera la lectura a BD.

[Answer]: A

---

## Q6 — Robustez multi-instancia (NFR5)

El diseño no debe asumir instancia única. ¿Qué nivel de coordinación modelamos ahora?

- A. **La BD es la fuente de verdad y árbitro de concurrencia**: el control de "una sola
  tarea activa" (FR1.6, 409) y los locks por usuario se resuelven contra el estado
  persistido (p. ej. condición/constraint en BD), no contra un lock en memoria de proceso.
  El caché en memoria es best-effort, nunca la autoridad.
- B. **Mantener locks en memoria por proceso** como hoy y aceptar que multi-instancia
  queda fuera del alcance real (documentado como limitación).

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de diseño de dominio que se materializarán en los
artefactos (`components.md`, `decisions.md`, `traceability.json`):

**Componentes lógicos (bloques que escribimos):**

1. **`SessionService`** — lógica de dominio de la sesión Futmondo: TTL (12h),
   locks por usuario, y reconstrucción/rehidratación idempotente (`ensureSession`),
   invocada desde `/auth/refresh` y desde el primer uso del cliente Futmondo
   (`_helpers.get_user_futmondo_client`). Cubre FR1.2/FR1.3. [Q1-C, Q2-C]
2. **`SessionRepository`** — persistencia durable de la sesión en Neon vía
   `db_connection`; dueño de la entidad `UserSession`. BD = fuente de verdad. [Q1-C, Q5-A, Q6-A]
3. **`TaskService`** — lógica de dominio de tareas de sync: idempotencia, unicidad
   "una activa" (FR1.6/409) resuelta contra estado persistido, marcado de tarea
   "interrumpida-por-reinicio" (FR1.5). [Q1-C, Q6-A]
4. **`TaskRepository`** — persistencia durable de tareas en Neon; dueño de la
   entidad `SyncTask`. BD = fuente de verdad. [Q1-C, Q4-A, Q6-A]
5. **`CredentialProtection`** — bloque de seguridad dueño de proteger la credencial
   Futmondo (cifrar/descifrar en reposo o gestionar el medio de re-auth); dueño de
   la entidad `ProtectedCredential`. La elección fina de FR5.2 (no-persistir vs.
   cifrar) se difiere a Functional/NFR design; frontera aislada aquí. [Q3-A, Q4-B]

**Componentes existentes que cambian de rol (caché best-effort, no autoridad):**

- **`SessionStore`** (en memoria) → caché de proceso delante de `SessionService`;
  ya no guarda `password` en claro (solo referencia a `ProtectedCredential`). [Q5-A]
- **`TaskManager`** (en memoria) → caché de proceso delante de `TaskService`;
  autoridad de concurrencia en BD. [Q5-A, Q6-A]

**Entidades y propiedad (una sola dueña cada una):**

- `UserSession` → `SessionRepository` (email, user_id, token, TTL; referencia a `ProtectedCredential`, sin `password` en claro).
- `SyncTask` → `TaskRepository` (id, estado, progreso, timestamps, flag interrumpida-por-reinicio).
- `ProtectedCredential` → `CredentialProtection` (referenciada por `user_id`).

**Dependencias clave:** `SessionService` → `SessionRepository`, `CredentialProtection`;
`TaskService` → `TaskRepository`; almacenes en memoria delante de sus servicios.
Dependencias de infraestructura (no componentes): Neon PostgreSQL, API Futmondo.

**Decisiones diferidas (registradas como ADR/Alternatives Rejected):** elección fina
FR5.2 (cifrado en reposo vs. re-auth), umbral numérico NFR2.

[Answer]: Looks correct
