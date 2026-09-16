# Unit of Work — Durabilidad del estado y credenciales (FR1/FR5)

> Etapa Units Generation (Inception). Agrupa los componentes del diseño de dominio
> en unidades de trabajo. Describe topología, no orden de entrega (eso es Delivery
> Planning 2.9). Ambas unidades son código nuevo embebido en el servicio
> `futmondo-api` existente (monolito modular; sin despliegue independiente).

## Sources

- domain-design/components.md (5 componentes nuevos + 5 re-cableados) [scope]
- domain-design/decisions.md (ADR-001..005) [scope]
- requirements-analysis/requirements.md (FR1.1–FR1.6, FR5.1–FR5.2, C1–C5, NFR5) [scope]
- team-practices.md (monolito modular; capa `stores/`; despliegue on-merge a Fly.io) [scope]
- units-generation-questions.md (Q1–Q5 confirmadas) [Q1] [Q2] [Q3] [Q4] [Q5]

## Units

### Tabla de unidades

| Unit ID | Directory | kind | Deployment | Complejidad |
|---------|-----------|------|------------|-------------|
| U1 | u1-durable-session | service | embebido en `futmondo-api` | M |
| U2 | u2-durable-sync-tasks | service | embebido en `futmondo-api` | M |

### U1 — Durabilidad de sesión y credenciales

- **Descripción**: hace durable la sesión Futmondo por usuario y aísla el tratamiento
  de la credencial, eliminando el 403 opaco tras reinicio (FR1.1/FR1.2/FR1.3) y la
  contraseña en claro (FR5.1/FR5.2).
- **Componentes que incluye**: `SessionService`, `SessionRepository`,
  `CredentialProtection` (nuevos); `SessionStore` (existente, degradado a caché
  best-effort); re-cableo de `AuthRoutes` (`/auth/refresh` dispara rehidratación) y
  `FutmondoClientAccessor` (`_helpers.get_user_futmondo_client` deja de devolver 403 opaco).
- **Responsabilidades**: persistir la sesión en Neon vía `db_connection` (capa
  estrecha `stores/`); rehidratación idempotente (`ensureSession`); TTL 12h y locks
  por usuario; aislar la credencial protegida (elección fina FR5.2 diferida a diseño).
- **Deployment**: embebido en `futmondo-api` (no hay servicio nuevo).
- **kind**: `service`.
- **Notas/constraints**: capa de persistencia estrecha, sin ampliar SQL-en-router ni
  god-files (C3); la contraseña nunca en claro (FR5.1); autoridad de estado en BD
  (no asumir instancia única, NFR5); caracterizar `SessionStore` antes de refactorizar
  (C5). La interfaz de `CredentialProtection` es un límite intra-unidad, formalizado en
  Contract Design (2.8).

### U2 — Durabilidad de tareas de sync

- **Descripción**: hace durable el estado de las tareas de sync, de modo que sean
  consultables tras un reinicio, se marquen como interrumpidas por reinicio, y la
  unicidad "una activa" se resuelva contra estado persistido (FR1.4/FR1.5/FR1.6).
- **Componentes que incluye**: `TaskService`, `TaskRepository` (nuevos); `TaskManager`
  (existente, degradado a caché best-effort); re-cableo de `SyncEndpoints`
  (`/api/v1/sync` delega en `TaskService`).
- **Responsabilidades**: persistir el estado/progreso de tareas en Neon vía
  `db_connection`; unicidad 409 contra BD (FR1.6); marcado interrumpida-por-reinicio
  al arrancar (FR1.5); estado consultable tras reinicio (FR1.4).
- **Deployment**: embebido en `futmondo-api` (no hay servicio nuevo).
- **kind**: `service`.
- **Notas/constraints**: capa de persistencia estrecha (C3); autoridad de concurrencia
  en BD (NFR5); caracterizar `TaskManager` antes de refactorizar (C5); no se reanudan
  tareas automáticamente (out of scope).

## Rationale de la decomposición

| Decisión | Justificación |
|----------|---------------|
| Dos unidades por dominio de estado (Q1-A) | Sesión y tareas no comparten lógica de dominio ni entidades; solo el abstractor `db_connection` preexistente. Fronteras alineadas con el diseño de dominio. |
| Grano grueso (Q2-A) | Servicio y repositorio de un mismo dominio siempre se construyen/despliegan juntos; separarlos sería el smell de "dos cosas que cambian juntas". Coherente con equipo pequeño e intervención acotada. |
| Credencial dentro de U1 (Q2-A/Q3-B) | `CredentialProtection` se consume dentro de la sesión y no se despliega por separado; su interfaz es un límite intra-unidad, no una arista del DAG. |
| Sin despliegue independiente (Q5-A) | C1 (sin reescrituras/cambios de stack) y coste 0 €: ambas unidades son código nuevo dentro de `futmondo-api`. |

**Alternatives Rejected**: unidad de persistencia compartida fundacional (Q1-B) — rechazada:
`db_connection` ya existe, no hay pieza fundacional real que escribir. Unidad monolítica
única (Q1-C) — rechazada: pierde independencia de test y de secuenciación. Grano fino
(Q2-B) — rechazado: crea unidades que siempre cambian juntas. Despliegue independiente
(Q5-B) — rechazado por coste 0 € y C1.
