# Business Rules — u1-durable-session

> Diseño funcional (Construction). Reglas de negocio de la sesión durable. El bloque `yaml`
> es la fuente de verdad; la tabla humana lo resume. IDs `BRx.y` para trazabilidad.

## Sources

- requirements.md (FR1.1, FR1.2, FR1.3, FR5.1, NFR1, NFR5, C4) [scope]
- contract-design/contract-summary.md (C1: resolve→None→401; can_reauthenticate; nunca plaintext) [scope]
- domain-design/decisions.md (ADR-005 BD autoridad, sin reintentos internos) [scope]
- functional-design-questions.md (Q4-A conjunto de reglas, Q5-A errores) [Q4] [Q5]

## Rules (source of truth)

```yaml
rules:
  - id: BR1.1
    statement: La sesión Futmondo persiste con un TTL absoluto de 12h y locks de concurrencia por usuario.
    category: constraint
    applies_to: UserSession
    trigger: creación o lectura de la sesión
    logic: >
      IF se crea una sesión THEN expires_at = created_at + 12h (absoluto, no deslizante).
      IF se lee una sesión con now > expires_at THEN se trata como ausente (purga perezosa).
      El acceso concurrente por usuario se serializa con un lock por user_id.
    violation_behaviour: una sesión expirada nunca se sirve como activa; se intenta reconstruir o se cae a 401.
    source: FR1.1, C4

  - id: BR1.2
    statement: La reconstrucción de sesión (ensureSession) es idempotente.
    category: policy
    applies_to: SessionService
    trigger: llamada a ensureSession(user_id) desde cualquier disparador
    logic: >
      IF ya existe una sesión activa (caché o BD) THEN se devuelve sin reconstruir.
      IF dos llamadas concurrentes reconstruyen el mismo user_id THEN el lock por usuario
      serializa; la segunda reutiliza la sesión ya reconstruida (no crea duplicados).
    violation_behaviour: nunca se crean dos sesiones para el mismo usuario ni se re-autentica dos veces innecesariamente.
    source: FR1.2

  - id: BR1.3
    statement: La sesión solo se reconstruye si existe un medio de re-autenticación; si no, error accionable 401.
    category: policy
    applies_to: SessionService
    trigger: ensureSession con sesión ausente/expirada tras reinicio
    logic: >
      IF CredentialProtection.can_reauthenticate(user_id) es cierto AND resolve devuelve material
      THEN re-autenticar contra Futmondo y activar la sesión (FR1.2).
      IF can_reauthenticate es falso OR resolve devuelve None OR el re-auth falla
      THEN estado unrecoverable ⇒ responder 401 accionable ("vuelve a iniciar sesión"), no 403 opaco.
    violation_behaviour: nunca se devuelve un 403 opaco por sesión perdida; siempre 401 accionable cuando no se puede reconstruir.
    source: FR1.2, FR1.3

  - id: BR1.4
    statement: La contraseña Futmondo nunca se almacena ni se registra en claro.
    category: authorization
    applies_to: UserSession, ProtectedCredential, CredentialProtection
    trigger: cualquier persistencia, log o retorno de datos de credencial
    logic: >
      IF se persiste, loggea o retorna material de credencial THEN debe estar protegido
      (nunca el password en claro), y solo CredentialProtection accede a su contenido.
    violation_behaviour: cualquier aparición del password en claro en BD, logs o valores de retorno es un fallo bloqueante (regla dura project.md).
    source: FR5.1, NFR1

  - id: BR1.5
    statement: La base de datos es la autoridad de estado; el caché en memoria es best-effort.
    category: constraint
    applies_to: SessionService, SessionStore, SessionRepository
    trigger: lectura/escritura de sesión
    logic: >
      IF hay discrepancia entre caché en memoria y BD THEN gana la BD.
      El caché (SessionStore) acelera el camino caliente pero nunca es autoritativo;
      no se asume instancia única (NFR5).
    violation_behaviour: nunca se sirve estado de caché como autoritativo frente a la BD.
    source: NFR5

  - id: BR1.6
    statement: La rehidratación se dispara desde /auth/refresh y desde el primer uso del cliente Futmondo, sin reintentos internos.
    category: policy
    applies_to: AuthRoutes, FutmondoClientAccessor, SessionService
    trigger: POST /auth/refresh; primer uso del cliente Futmondo tras reinicio
    logic: >
      IF llega /auth/refresh OR el primer uso del cliente encuentra la sesión ausente
      THEN invocar ensureSession (idempotente, BR1.2).
      Los fallos de descifrado/almacén se propagan como excepción tipada del dominio
      (no except: pass); no hay reintentos internos (el reintento, si aplica, es del llamador).
    violation_behaviour: un fallo silencioso (except: pass) o un reintento interno no controlado es una violación.
    source: FR1.2, ADR-005
```

## Resumen de reglas

| ID | Regla | Categoría | Fuente |
|----|-------|-----------|--------|
| BR1.1 | TTL absoluto 12h + locks por usuario (purga perezosa) | constraint | FR1.1, C4 |
| BR1.2 | `ensureSession` idempotente (sin sesiones duplicadas) | policy | FR1.2 |
| BR1.3 | Reconstrucción condicional a medio de re-auth; si no, 401 accionable | policy | FR1.2, FR1.3 |
| BR1.4 | Nunca contraseña en claro (BD/logs/retornos) | authorization | FR5.1, NFR1 |
| BR1.5 | BD autoridad; caché best-effort (no asume instancia única) | constraint | NFR5 |
| BR1.6 | Disparadores refresh + primer uso; excepción tipada; sin reintentos internos | policy | FR1.2, ADR-005 |
