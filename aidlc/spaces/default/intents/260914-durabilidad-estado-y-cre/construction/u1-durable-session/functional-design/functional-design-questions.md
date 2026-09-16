# Functional Design — u1-durable-session

> Construction (arquitecto + desarrollador). Diseño funcional de la unidad de sesión
> durable: modelo de entidades, reglas de negocio y especificación de comportamiento
> (workflows y máquina de estados). Técnicamente agnóstico; sin código. Responde en el
> tag `[Answer]:`. `X. Other (please specify)` siempre disponible.

## Sources

- unit-of-work.md (U1: SessionService, SessionRepository, CredentialProtection, SessionStore) [scope]
- requirements.md (FR1.1/1.2/1.3, FR5.1/5.2, NFR1/2/5, C4) [scope]
- domain-design/components.md (entidades UserSession, ProtectedCredential; dirección única de caché) [scope]
- contract-design/contract-summary.md (C1: protect/resolve/can_reauthenticate; resolve→None→401; nunca plaintext) [scope]
- team.md (caracterización primero; fakes de persistencia en tests) [scope]

---

## Q1 — Persistencia del TTL de sesión (FR1.1, C4)

El TTL de 12h se preserva. Tras un reinicio, ¿cómo se trata una sesión persistida cuya
marca de tiempo indica que ya expiró?

- A. **TTL absoluto por `expires_at`**: la sesión persiste `created_at` + `expires_at` (12h).
  Al leerla tras reinicio, si `now > expires_at` se trata como ausente (no se reconstruye por
  TTL; se intenta re-auth vía FR1.2 o se cae a FR1.3). Una purga perezosa la elimina al leerla.
- B. **TTL deslizante**: cada uso renueva el `expires_at` (+12h). 
- C. Otra (indícala en Other).

[Answer]: A

---

## Q2 — Clave de la sesión persistida y unicidad

- A. **Una fila por `user_id`** (la sesión Futmondo es por usuario; `user_id` es el identificador):
  upsert al hacer login/reconstruir; una sola sesión activa por usuario, coherente con el
  `dict[str, UserSession]` actual y con los locks por usuario.
- B. Múltiples filas por usuario (histórico de sesiones).

[Answer]: A

---

## Q3 — Máquina de estados de la sesión (para functional-spec)

¿Qué estados observables modelamos para la sesión?

- A. **Estados: `active` → `expired` (por TTL) / `absent` (no persistida o purgada) → `rehydrating`
  → `active` | `unrecoverable`**. Transición clave: en el primer uso tras reinicio con sesión
  ausente, `SessionService.ensureSession` pasa a `rehydrating`; si `CredentialProtection.resolve`
  da material → re-auth contra Futmondo → `active`; si da `None` o falla el re-auth → `unrecoverable`
  (⇒ 401 accionable, FR1.3).
- B. Modelo más simple (solo present/absent) sin estado de rehidratación explícito.

[Answer]: A

---

## Q4 — Reglas de negocio a fijar (rules.md)

¿Confirmas el conjunto de reglas de negocio de la unidad?

- A. **Sí**, estas reglas (se numerarán BRx.y):
  - Preservar TTL 12h y locks por usuario (FR1.1/C4).
  - Rehidratación idempotente: `ensureSession` es segura de llamar múltiples veces; no crea
    sesiones duplicadas (FR1.2).
  - Reconstrucción condicional: solo si `can_reauthenticate` es cierto; si no, 401 accionable (FR1.2/FR1.3).
  - No persistir ni loggear la contraseña en claro; la credencial vive tras `CredentialProtection` (FR5.1/NFR1).
  - Autoridad en BD: la sesión persistida es la fuente de verdad; el caché en memoria es best-effort (NFR5).
  - Disparadores de rehidratación: `/auth/refresh` y primer uso del cliente Futmondo (idempotente).
- B. Faltan/sobran reglas (indícalo en Other).

[Answer]: A

---

## Q5 — Manejo de errores y casos límite (functional-spec)

- A. **Explícito y tipado**: fallo de descifrado/almacén de credencial → excepción tipada del
  dominio (no `except: pass`), que `SessionService` traduce a un error accionable sin filtrar el
  secreto; fallo de re-auth contra Futmondo (credenciales ya inválidas) → `unrecoverable` → 401
  accionable; concurrencia (dos peticiones rehidratando el mismo usuario) → lock por usuario
  serializa, la segunda reutiliza la sesión reconstruida (idempotencia). Sin reintentos internos.
- B. Otra semántica (indícala en Other).

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen del diseño funcional de u1-durable-session que se materializará en
`entities.md`, `rules.md`, `functional-spec.md` y `traceability.json`:

**Entidades:**
- `UserSession` (dueño SessionRepository): `user_id` (id, único), `email`, `token`,
  `created_at`, `expires_at` (TTL absoluto 12h), referencia a `ProtectedCredential` por
  `user_id`. Una fila por usuario (upsert). Sin `password` en claro. [Q1-A, Q2-A]
- `ProtectedCredential` (dueño CredentialProtection): `user_id` (id), `protected_material`
  (opaco), `scheme`, `updated_at`. Mecanismo fino (cifrado vs re-auth, FR5.2) diferido.

**Máquina de estados de sesión (functional-spec):** `active` → `expired` (TTL) / `absent`
→ `rehydrating` → `active` | `unrecoverable`. `ensureSession` dispara `rehydrating`;
material de re-auth presente → re-auth Futmondo → `active`; `None`/fallo → `unrecoverable`
(401 accionable, FR1.3). [Q3-A]

**Reglas de negocio (rules.md, BRx.y):** TTL 12h + locks por usuario; rehidratación
idempotente; reconstrucción condicional a `can_reauthenticate`; no persistir/loggear
contraseña en claro; autoridad en BD (caché best-effort); disparadores refresh + primer
uso del cliente. [Q4-A]

**Errores/concurrencia:** excepción tipada del dominio en fallo de descifrado/almacén (no
`except: pass`, sin filtrar secreto); re-auth fallido → `unrecoverable` → 401; concurrencia
serializada por lock por usuario + idempotencia de `ensureSession`; sin reintentos internos. [Q5-A]

**Workflows en functional-spec:** (1) login (persiste sesión + credencial protegida);
(2) `/auth/refresh` dispara `ensureSession`; (3) primer uso del cliente Futmondo dispara
`ensureSession`; (4) purga perezosa de sesión expirada al leer.

**Traceability:** los FR de U1 (FR1.1, FR1.2, FR1.3, FR5.1) se mapearán a las BRx.y de rules.md.

[Answer]: Looks correct
