# Unit of Work — Story Map

> No existe `stories.md` (la etapa User Stories no se ejecutó en este scope). Se mapean
> los requisitos funcionales (`FR`) —los identificadores de trazabilidad disponibles—
> a su unidad implementadora `U{n}` y su directorio de construcción.

## Sources

- requirements-analysis/requirements.md (FR1.1–FR1.6, FR5.1–FR5.2) [scope]
- unit-of-work.md (U1, U2) [scope]

## Mapa FR → Unidad

| FR ID | Descripción breve | Unit ID | Directory |
|-------|-------------------|---------|-----------|
| FR1.1 | Persistir sesión Futmondo (TTL 12h, locks) | U1 | u1-durable-session |
| FR1.2 | Reconstrucción transparente de sesión tras reinicio | U1 | u1-durable-session |
| FR1.3 | Error accionable (401) cuando no se puede reconstruir | U1 | u1-durable-session |
| FR5.1 | No almacenar contraseña en claro | U1 | u1-durable-session |
| FR5.2 | Mecanismo de credencial (re-auth vs cifrado, diferido) | U1 | u1-durable-session |
| FR1.4 | Persistir estado de tareas de sync (consultable tras reinicio) | U2 | u2-durable-sync-tasks |
| FR1.5 | Marcar tareas en curso como interrumpidas por reinicio | U2 | u2-durable-sync-tasks |
| FR1.6 | Rechazar (409) segunda tarea activa; permitir relanzar si interrumpida | U2 | u2-durable-sync-tasks |

## Requisitos transversales (cross-cutting)

- **NFR5 (robustez multi-instancia)**: atraviesa U1 y U2 — ambas resuelven autoridad de
  estado/concurrencia contra la BD, no en memoria de proceso.
- **NFR3 (coste 0 €), NFR4 (no regresión)**: aplican a ambas unidades.

## Orden de implementación dentro de cada unidad

- **U1**: capa de persistencia (`SessionRepository`) y frontera de credencial
  (`CredentialProtection`) → lógica (`SessionService`, `ensureSession`) → re-cableo de
  disparadores (`AuthRoutes`, `FutmondoClientAccessor`) y degradación de `SessionStore` a caché.
- **U2**: capa de persistencia (`TaskRepository`) → lógica (`TaskService`: unicidad,
  interrupción) → re-cableo de `SyncEndpoints` y degradación de `TaskManager` a caché.

(El orden entre unidades y su secuenciación económica se decide en Delivery Planning 2.9.)

## Verificación de cobertura

- Todos los FR asignados: FR1.1–FR1.3, FR5.1–FR5.2 → U1; FR1.4–FR1.6 → U2. Sin FR huérfano.
- Ambas unidades tienen FR asignados (U1: 5; U2: 3). Sin unidad vacía.
