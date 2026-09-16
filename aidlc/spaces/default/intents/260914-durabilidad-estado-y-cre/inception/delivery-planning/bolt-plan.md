# Bolt Plan — Durabilidad del estado y credenciales

> Última etapa de Inception (delivery lead). Secuencia ordenada de **Bolts** — cada
> Bolt es una pasada de construcción sobre una o más unidades de trabajo, con su
> Definición de Hecho y una hipótesis de confianza, que termina en algo que funciona.
> El DAG de Units Generation no tiene aristas (U1 y U2 independientes); el orden 1→2
> es una elección económica (risk/value-first), no una restricción de dependencia.

## Sources

- units-generation/unit-of-work.md, unit-of-work-dependency.md (U1, U2; DAG sin aristas) [scope]
- requirements-analysis/requirements.md (FR1/FR5, C5, NFR2) [scope]
- contract-design/contract-summary.md (C1 CredentialProtection intra-U1) [scope]
- team.md (Testing: caracterización primero; Way of Working: squash-merge; Walking Skeleton OFF) [scope]
- delivery-planning-questions.md (Q1–Q6) [Q1] [Q2] [Q3] [Q4] [Q5] [Q6]

## Way of Working (resuelto de prácticas afirmadas)

- **Rama base/destino:** `main` / `main`; **estrategia de merge:** squash-merge (cada Bolt
  aterriza como un commit por su slug).
- **Walking skeleton:** OFF — el sistema ya está en producción; no hay nada que arrancar de
  cero. El primer Bolt corre como cualquier otro.
- **Despliegue:** on-merge a Fly.io (`futmondo-api`), smoke test contra `/health`.

## Secuencia de Bolts

Ejecución **en serie** (un Bolt tras otro): equipo AI, un solo proceso; el Bolt 1 valida el
patrón de persistencia que el Bolt 2 reutiliza.

### Bolt 1 — Sesión durable (walking skeleton: no)

- **Unidad incluida:** U1 (`u1-durable-session`).
- **Componentes:** SessionService, SessionRepository, CredentialProtection, SessionStore (caché)
  + re-cableo de AuthRoutes y FutmondoClientAccessor.
- **Definición de Hecho:**
  - Caracterización previa: tests que congelan el comportamiento actual de `SessionStore`
    (incluido el fallo 403 tras reinicio) antes de refactorizar (C5).
  - Sesión Futmondo persistida en Neon (FR1.1, TTL 12h, locks por usuario).
  - Rehidratación idempotente (`ensureSession`) desde `/auth/refresh` y primer uso del cliente
    (FR1.2); si no hay medio de re-auth, 401 accionable (FR1.3), no 403 opaco.
  - Contraseña nunca en claro en BD ni logs (FR5.1); interfaz `CredentialProtection` aislada (C1).
  - Tests del nuevo contrato (sesión reconstruida, no texto plano); suite existente en verde (NFR4).
- **Hipótesis de confianza:** tras un redeploy de `futmondo-api`, la primera petición autenticada
  NO devuelve 403 (se reconstruye la sesión o se pide re-login con 401 claro), y el `password`
  no aparece en claro en la BD ni en los logs.
- **Demo esperado:** reiniciar el backend y mostrar que la sesión sobrevive (o degrada a 401
  accionable) en lugar del 403 opaco actual.

### Bolt 2 — Tareas de sync durables (walking skeleton: no)

- **Unidad incluida:** U2 (`u2-durable-sync-tasks`).
- **Componentes:** TaskService, TaskRepository, TaskManager (caché) + re-cableo de SyncEndpoints.
- **Definición de Hecho:**
  - Caracterización previa: tests que congelan el comportamiento actual de `TaskManager`
    (incluida la tarea huérfana tras redeploy) antes de refactorizar (C5).
  - Estado de tareas persistido en Neon y consultable tras reinicio (FR1.4).
  - Tarea en curso marcada como interrumpida-por-reinicio al arrancar (FR1.5; no se reanuda).
  - Unicidad "una tarea activa" resuelta contra BD (FR1.6, 409; relanzable si interrumpida).
  - Tests del nuevo contrato (idempotencia, interrupción); suite existente en verde (NFR4).
- **Hipótesis de confianza:** tras un redeploy con una tarea en curso, la tarea queda marcada
  como interrumpida (no "en curso" indefinidamente), y un segundo `trigger` con tarea activa
  devuelve 409.
- **Demo esperado:** lanzar un sync, reiniciar el backend a mitad, y mostrar el estado
  interrumpido consultable + el 409 al relanzar sobre una activa.

## Notas

- Ambos Bolts reutilizan el patrón de aislamiento de tests afirmado (fakes de la capa de
  persistencia en memoria, no BD Neon real).
- El mecanismo fino de credenciales (cifrado vs. re-auth, FR5.2) se concreta en Functional/NFR
  design dentro del Bolt 1.
