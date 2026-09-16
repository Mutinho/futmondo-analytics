# NFR Design — Preguntas de diseño (u1-durable-session)

> Etapa NFR Design (Construction). Traigo al arquitecto (lead) con la perspectiva de plataforma
> (AWS/infra, aquí Fly.io + Neon) como apoyo. La mayoría del espacio de diseño ya está acotado por
> las etapas previas (coste 0€, sin servicios nuevos, BD como autoridad, caché en memoria
> best-effort, logging estructurado sobre los logs de Fly.io). Estas preguntas resuelven lo que
> las etapas anteriores dejaron **explícitamente abierto** o donde caben variantes de patrón.
>
> Responde con `[Answer]: <letra>` (o `X` con tu texto). Puedes dejar en blanco las que quieras
> que resuelva con el valor recomendado; si dejas alguna en blanco te lo marco antes de generar.

---

## Q1 — Mecanismo de protección de la credencial (FR5.2) — LA decisión abierta de la unidad

Es la única decisión tecnológica que todas las etapas previas difirieron aquí. Regla dura de
`project.md`: NUNCA contraseña en claro (ni memoria ni BD). Ambas opciones son coste 0€.

- **A. No persistir la contraseña — re-auth con refresh token (recomendada).** `protect` NO guarda
  la contraseña; `ProtectedCredential` almacena únicamente un *handle* de re-autenticación que ya
  existe (el refresh token de Futmondo / la vía de re-login), no el secreto. `resolve` devuelve ese
  handle o `None`. Ventaja: no hay secreto en reposo que gestionar ni clave que rotar; superficie
  de fuga mínima (NFR1.1 trivialmente cierto). Coste 0€. Si no hay handle → `None` → 401 accionable
  (FR1.3), que es exactamente la degradación ya diseñada.
- **B. Cifrado en reposo de la contraseña** con `cryptography` (Fernet/AES-GCM) y clave gestionada
  como secret de Fly.io (`FUTMONDO_CRED_KEY`). `protect` cifra y guarda; `resolve` descifra en
  memoria efímera. Ventaja: re-auth totalmente transparente aunque el refresh token caduque. Coste:
  gestión y rotación de una clave nueva, y la contraseña (aunque cifrada) vive en reposo.
- **X. Otra (especifica).**

[Answer]: A

---

## Q2 — Cómo se materializa el `resolve` sin exponer el secreto al llamador

`SessionService` necesita reconstruir la sesión Futmondo, pero el contrato C1 dice que `resolve`
devuelve `ReauthMaterial` opaco, "nunca el password crudo expuesto al llamador".

- **A. `CredentialProtection` ejecuta el re-auth internamente y devuelve la sesión/token ya
  reconstruido (recomendada).** El material sensible nunca sale del componente de seguridad; el
  llamador recibe una sesión válida o `None`. Frontera de confianza mínima. Encaja con A y con B de Q1.
- **B. `resolve` devuelve un objeto opaco (handle) que `SessionService` pasa al cliente Futmondo,
  sin poder leer su contenido.** Requiere disciplina para que el opaco no se loggee ni serialice.
- **X. Otra (especifica).**

[Answer]: A

---

## Q3 — Concurrencia: reconstrucción simultánea del mismo usuario (BR1.1 lock, BR1.2 idempotencia)

Dos peticiones pueden disparar `ensureSession(user_id)` a la vez tras un reinicio. El spec exige
serializar por `user_id` y que la segunda reutilice la sesión ya reconstruida.

- **A. Lock a nivel de BD con `SELECT ... FOR UPDATE` sobre la fila de `UserSession` (recomendada).**
  La autoridad de concurrencia es la BD (NFR5.2, tolera multi-instancia sin rediseño). Neon lo
  soporta; coste 0€. La segunda transacción espera y encuentra la sesión ya `active`.
- **B. Lock en memoria de proceso (`asyncio.Lock` por `user_id`).** Más simple y rápido, pero NO
  tolera multi-instancia (viola NFR5.2 si algún día `min>1`). Aceptable solo como optimización
  *encima* de la autoridad de BD, no como única barrera.
- **C. A + B (lock en memoria como fast-path por instancia, BD como autoridad).**
- **X. Otra (especifica).**

[Answer]: A

---

## Q4 — Fiabilidad del re-auth ante fallo transitorio de Futmondo (NFR5.1/NFR5.3, BR1.6)

BR1.6 dice "sin reintentos internos". Pero conviene distinguir un fallo *transitorio* de Futmondo
(5xx/timeout de red) de una credencial *definitivamente inválida*.

- **A. Sin reintentos; distinguir el resultado (recomendada).** Credencial inválida / `None` →
  `unrecoverable` → 401 accionable (FR1.3). Error transitorio de red/5xx → error tipado hacia
  arriba (no se marca `unrecoverable` de forma permanente, no se destruye el handle), el usuario
  reintenta. Respeta BR1.6 (nada de bucles de reintento internos) sin convertir un blip en un
  logout injustificado.
- **B. Sin reintentos y tratar cualquier fallo como `unrecoverable` → 401.** Más simple, pero un
  hipo de red desloguea al usuario.
- **X. Otra (especifica).**

[Answer]: A

---

## Q5 — Purga perezosa de sesiones expiradas (WF4, BR1.1) — política de escritura

Al leer una `UserSession` con `now > expires_at` se trata como ausente y se elimina de forma
perezosa (sin job de limpieza, coste 0€).

- **A. `DELETE` de la fila expirada dentro de la misma transacción de lectura (recomendada).**
  Autolimpieza incremental; la tabla se mantiene en ~1 fila por usuario activo. Idempotente y barato.
- **B. Ignorar en lectura y sobrescribir por `upsert` en el siguiente login.** No borra filas de
  usuarios que no vuelven; acumula filas muertas (poco, dado 1 fila/usuario, pero sin límite duro).
- **X. Otra (especifica).**

[Answer]: A

---

## Q6 — Observabilidad: correlación de eventos de sesión en los logs de Fly.io (NFR-OBS.1/2)

Sin infra de métricas/tracing de pago. Quiero poder contar por logs cuántas sesiones acaban en
`unrecoverable` → 401.

- **A. Log estructurado (JSON) con `event`, `user_id`, `outcome` y un `request_id`/correlation-id
  propagado desde el middleware existente (recomendada).** Permite `grep`/conteo en Fly.io sin
  dashboard. NUNCA se loggea la credencial (refuerza NFR1.1).
- **B. Log estructurado con `event`/`outcome`/`user_id` pero sin correlation-id** (si el backend no
  tiene ya un id de petición reutilizable). Igual de auditable por conteo, sin trazar la petición.
- **X. Otra (especifica).**

[Answer]: A

---

## Consolidated Summary Confirmation

Análisis de ambigüedad: sin respuestas vagas ni contradicciones. Todas las decisiones son
concretas. Q6 lleva una degradación condicional explícita (si no hay id de petición reutilizable,
se usa la variante sin correlation-id), que no bloquea el diseño.

Resumen de lo que voy a diseñar con tus respuestas:

- **Q1 (A) — Protección de credencial:** NO se guarda la contraseña. `CredentialProtection` guarda
  solo un *handle* de re-autenticación (refresh token / vía de re-login que ya existe). Cumple
  "nunca contraseña en claro" de forma casi automática; sin clave que gestionar ni rotar; coste 0€.
- **Q2 (A) — Frontera de seguridad:** el componente de seguridad hace el re-auth por dentro y
  devuelve una sesión ya reconstruida (o `None`). El material sensible nunca cruza la frontera hacia
  `SessionService`.
- **Q3 (A) — Concurrencia:** bloqueo en BD (`SELECT ... FOR UPDATE` sobre la fila del usuario). La
  BD es la autoridad; tolera multi-instancia sin rediseño. La 2ª petición reutiliza la sesión ya
  reconstruida (idempotencia BR1.2).
- **Q4 (A) — Fiabilidad del re-auth:** sin reintentos internos (BR1.6), pero distinguiendo fallo
  transitorio de Futmondo (error tipado hacia arriba, no destruye el handle) de credencial inválida
  / `None` (→ `unrecoverable` → 401 accionable, FR1.3).
- **Q5 (A) — Purga:** `DELETE` perezoso de la fila caducada en la misma transacción de lectura. Sin
  job de limpieza. Tabla en ~1 fila por usuario activo.
- **Q6 (A) — Observabilidad:** log estructurado JSON (evento, user_id, outcome, correlation-id
  propagado desde el middleware existente) sobre los logs de Fly.io; conteo por `grep`, sin
  dashboard. NUNCA se loggea la credencial (refuerza NFR1.1).

Voy a generar 7 artefactos: performance-design, security-design, scalability-design,
reliability-design, observability-design, logical-components y traceability.json.

[Answer]: Looks correct
