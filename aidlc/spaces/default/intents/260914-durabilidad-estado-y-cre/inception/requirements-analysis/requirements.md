# Requirements — Durabilidad del estado y credenciales Futmondo

> Fase de Inception. Deriva del intent, el alcance aprobado y el codekb del
> backend. Los IDs FR/NFR son claves de trazabilidad permanentes.

## Sources

- intent-statement.md, scope-document.md, intent-backlog.md [scope]
- codekb: architecture.md, code-quality-assessment.md (estado FR1/FR5) [desc]
- requirements-analysis-questions.md (Q1–Q5 confirmadas) [Q1] [Q2] [Q3] [Q4] [Q5]
- team.md / project.md (prácticas y reglas duras afirmadas) [scope]

## Análisis de intención

El objetivo es que dos piezas de estado crítico del backend dejen de depender de
la vida del proceso, atacando los dos hallazgos "Crítico" del plan de mejoras:

- **FR1 — Durabilidad**: el estado de las sesiones Futmondo (`SessionStore`) y de
  las tareas de sync (`TaskManager`) sobrevive a un reinicio/redeploy de la
  máquina Fly, persistiéndose en Neon PostgreSQL. El usuario deja de sufrir 403
  opacos y tareas huérfanas.
- **FR5 — Credenciales**: la contraseña Futmondo deja de persistirse en claro al
  hacer durable el estado.

Meta de negocio: continuidad de la experiencia (el reinicio no rompe el sync ni
la sesión) y eliminación del riesgo de exponer credenciales, a coste 0 € y sin
reescrituras grandes.

## Requisitos funcionales

### FR1 — Durabilidad del estado

- **FR1.1** El sistema debe persistir en Neon PostgreSQL el estado de las
  sesiones Futmondo por usuario, preservando el TTL (12h) y la semántica de
  concurrencia con locks por usuario ya existente. [Q1] [scope]
- **FR1.2** Cuando el mecanismo de credenciales elegido en diseño (FR5.2)
  conserve un medio de re-autenticación (contraseña cifrada o token), tras un
  reinicio del proceso el sistema debe reconstruir la sesión Futmondo de forma
  transparente, de modo que la primera petición autenticada tras el reinicio no
  requiera re-login. Este requisito es condicional: si el diseño opta por no
  conservar credencial alguna, no aplica y prevalece FR1.3. [Q1] [Q4]
- **FR1.3** Cuando la sesión no pueda reconstruirse, el sistema debe responder
  con una acción clara para el usuario (p. ej. 401 con instrucción de volver a
  iniciar sesión) en lugar de un 403 opaco. [Q1]
- **FR1.4** El sistema debe persistir en Neon PostgreSQL el estado de las tareas
  de sync, de modo que una tarea sea consultable tras un reinicio y refleje su
  último estado conocido. [Q2] [scope]
- **FR1.5** Tras un reinicio, cualquier tarea de sync que estuviera en curso debe
  marcarse explícitamente como interrumpida por reinicio (no permanecer "en
  curso" indefinidamente); no se reanuda automáticamente. [Q2]
- **FR1.6** El sistema debe rechazar (409) el lanzamiento de una tarea de sync
  cuando ya haya una activa según el estado persistido, salvo que la tarea
  previa esté marcada como interrumpida por reinicio, en cuyo caso debe permitir
  relanzarla. [Q3]

### FR5 — Tratamiento de credenciales

- **FR5.1** El sistema no debe almacenar la contraseña Futmondo en claro en
  ningún estado persistente (base de datos), y al construir la durabilidad no
  debe reintroducir ni perpetuar el patrón de texto plano. La presencia
  transitoria de la contraseña en memoria del proceso durante la vida de la
  sesión es la deuda preexistente (`UserSession`) que el mecanismo elegido en
  diseño (FR5.2) buscará reducir; esta redacción es coherente con la regla dura
  afirmada en `project.md` (NEVER contraseña en claro, ni en memoria ni en BD)
  entendida como no reintroducir el patrón al diseñar la durabilidad. [Q4] [scope]
- **FR5.2** El mecanismo concreto (no persistir la contraseña vía re-auth, o
  cifrarla en reposo con clave gestionada como secret de Fly.io) se decide en la
  etapa de diseño; ambos son viables a coste 0 €. [Q4]

## Requisitos no funcionales

- **NFR1 — Seguridad**: la contraseña Futmondo nunca se almacena en claro en
  reposo (BD) y el diseño de durabilidad no reintroduce el patrón de texto
  plano; el objetivo, alineado con la regla dura afirmada, es reducir la deuda
  de credenciales en memoria (no ampliarla). El arranque del servicio sigue
  exigiendo un `JWT_SECRET` no-default (guard ya endurecido). [Q4] [Q5]
- **NFR2 — Rendimiento**: la persistencia de sesión y de estado de tareas no
  debe degradar de forma perceptible el camino de sesión. No se fija un umbral
  numérico en esta etapa; se validará por medición en diseño/build. [Q5]
- **NFR3 — Coste**: la solución se mantiene a coste 0 € (Neon free, Fly.io free
  allowance, GitHub Actions free); no se introducen servicios de pago. [Q5] [scope]
- **NFR4 — Compatibilidad / no regresión**: la suite de tests existente debe
  permanecer en verde tras los cambios. [Q5] [scope]
- **NFR5 — Robustez multi-instancia**: el diseño de persistencia no debe asumir
  instancia única, aunque `fly.toml` fije min=max=1 (debe tolerar reinicio y un
  eventual escalado). [desc]

## Restricciones

- **C1** Mantener el stack actual (Angular + FastAPI + Neon + Fly.io); sin
  reescrituras grandes. [scope]
- **C2** La persistencia se apoya en Neon PostgreSQL vía el abstractor
  `db_connection.py`; sin dependencias nuevas de pago. [desc] [scope]
- **C3** El nuevo estado durable debe implementarse tras una capa de persistencia
  estrecha (módulo tipo `stores/` o funciones repositorio en `services/`), sin
  ampliar el patrón de SQL-en-router ni los god-files existentes. [scope]
- **C4** Preservar el TTL (12h) y los locks de concurrencia por usuario. [desc]
- **C5** Caracterizar (congelar con tests) el comportamiento actual de
  `SessionStore`/`TaskManager` antes de refactorizarlos. [scope]

## Assumptions

- [assumption] Neon (tier free) admite las tablas nuevas de estado sin acercarse
  a los límites del tier, dado el volumen actual. [Q5] [memory:M1]
- [assumption] La reconstrucción transparente de la sesión (FR1.2) será posible
  al menos cuando el diseño de FR5 conserve un medio de re-autenticación
  (contraseña cifrada o token); si el diseño opta por no conservar credencial,
  FR1.2 puede no aplicar y prevalece FR1.3. [Q1] [Q4]

## Out of scope

- Reanudación automática de tareas de sync interrumpidas (solo se persiste y se
  marca el estado). [Q2] [scope]
- Reescrituras grandes, cambios de stack o cualquier solución con coste
  recurrente. [scope]
- Cobertura profunda o cambios del frontend Angular (intent centrado en backend). [scope]

## Open questions

- La elección concreta de FR5 (re-auth vs. cifrado en reposo) se decide en
  diseño (domain/functional design). [Q4]
- El umbral numérico de latencia de NFR2 se fijará por medición en diseño/build. [Q5]
