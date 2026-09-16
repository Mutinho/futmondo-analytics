# Security Design — u1-durable-session

> Etapa NFR Design (Construction). Traduce los requisitos de seguridad (NFR1.1–NFR1.4) y las reglas
> duras de `project.md` en un diseño concreto de protección de credencial, autenticación y manejo de
> secretos. Es diseño, no implementación: los snippets son ilustrativos (≤15 líneas).

## Sources

- nfr-requirements/security-requirements.md (NFR1.1, NFR1.2, NFR1.3, NFR1.4; STRIDE) [scope]
- project.md (NEVER contraseña en claro en memoria/BD; NEVER JWT_SECRET default) [scope]
- inception/contract-design/contract-summary.md (C1: `protect`/`resolve`/`can_reauthenticate`) [scope]
- functional-design/functional-spec.md (WF1–WF4; estados; BR1.4) [scope]
- nfr-design-questions.md (Q1-A no persistir contraseña, Q2-A re-auth interno, Q4-A distinguir fallo) [Q1] [Q2] [Q4]

## Decisión central — protección de la credencial (FR5.2, Q1-A)

**No se persiste la contraseña de Futmondo.** `CredentialProtection` almacena únicamente un
*handle* de re-autenticación derivado del propio login (el token/refresh de Futmondo que el flujo
de login ya obtiene), nunca la contraseña. Esto elimina por diseño la persistencia de la contraseña.

> **Alcance preciso de "por construcción" (corrige R-03):** la propiedad "por construcción" se
> refiere a la **NO persistencia** de la contraseña, no a su ausencia total del proceso. La
> contraseña en claro SÍ entra al proceso en el login (WF1 paso 3: `protect(user_id,
> plaintext_credential)`). El ciclo de vida del plaintext dentro de `protect` se especifica abajo.

### El handle de re-auth es un secreto en reposo (corrige R-01)

El handle (token/refresh de Futmondo) es **material portador reutilizable**: quien lo lea puede
re-autenticar como el usuario. Por tanto se trata como **secreto en reposo**, no como dato opaco
inocuo:

- **Cifrado en reposo del handle** con `cryptography` (AES-GCM / Fernet), clave gestionada como
  **secret de Fly.io** (`FUTMONDO_CRED_KEY`) — exactamente la vía que NFR1.2 contempla. Es coste 0€
  (una variable de entorno de Fly.io, sin servicio nuevo). `protected_material` guarda el
  ciphertext; nunca el token en claro.
- Esto NO contradice Q1-A: Q1-A decide **no guardar la contraseña**; el handle es un token con TTL
  (12h, BR1.1), revocable y de menor alcance que la contraseña. La contraseña sigue sin persistirse.
- Diferencia frente a la alternativa rechazada (cifrar la contraseña): aquí ciframos un **token de
  sesión de vida corta**, no la contraseña maestra. Menos valor si se filtra y caduca solo.
- Clasificación de compliance: `protected_material` es **restricted** (security-requirements.md >
  Notas de cumplimiento); el cifrado en reposo lo satisface, y su retención sigue el TTL de sesión.

### Ciclo de vida del `plaintext_credential` en `protect` (corrige R-03)

```text
protect(user_id, plaintext_credential):
  1. usa el plaintext SOLO para completar/confirmar el login a Futmondo ya en curso (WF1)
  2. obtiene el handle de re-auth (token/refresh) de la RESPUESTA de Futmondo
  3. cifra el handle con la clave de Fly.io -> guarda el ciphertext en ProtectedCredential
  4. NO retiene el plaintext: no lo asigna a atributos de instancia, no lo loggea, no lo serializa
  5. el plaintext queda fuera de alcance al terminar la función (variable local efímera)
```

La ventana de plaintext se limita a la pila de `protect` durante el login; no se persiste ni se
loggea (refuerza NFR1.1). El desarrollador implementa `protect` con esta regla explícita.

### Modelo de datos de la credencial

`ProtectedCredential` (una fila por `user_id`) guarda:
- `protected_material` (opaco): el handle de re-auth **cifrado** (ciphertext). No es la contraseña
  y no es legible sin la clave de Fly.io.
- `scheme`: identifica la vía y el esquema de cifrado (p. ej. `refresh-token+aesgcm-v1`), para
  poder rotar la clave o evolucionar sin migración dura.
- `updated_at`.

## Arquitectura de autenticación / autorización

No cambia el modelo existente (JWT access token en memoria + refresh token en cookie HttpOnly). Lo
que añade esta unidad es la **reconstrucción transparente** de la sesión Futmondo tras un reinicio:

- **Frontera de confianza (Q2-A) — firma reconciliada (corrige R-02):** `CredentialProtection`
  ejecuta el re-auth **internamente** y devuelve una sesión Futmondo ya reconstruida (o `None`). El
  material sensible (handle descifrado) NUNCA cruza hacia `SessionService`. Para que la firma sea
  coherente con Q2-A (y no con la Q2-B rechazada), la operación pública que usa `SessionService` es
  `reauthenticate`, que devuelve la **sesión reconstruida**, no material. `resolve` (que devolvía
  `ReauthMaterial`) pasa a ser **interno-privado** del componente, no expuesto al llamador.

```python
# Interfaz reconciliada con Q2-A — ilustrativa, no implementación
class CredentialProtection(Protocol):
    def protect(self, user_id: str, plaintext_credential: str) -> None: ...
    #   deriva el handle de la respuesta de Futmondo, lo CIFRA (clave Fly.io) y lo guarda;
    #   NUNCA persiste/loggea el plaintext ni el handle en claro (NFR1.1/NFR1.2)
    def can_reauthenticate(self, user_id: str) -> bool: ...
    #   predicado barato: ¿hay handle guardado? Ramifica FR1.2 vs FR1.3 sin materializar secretos
    def reauthenticate(self, user_id: str) -> "FutmondoSession | None": ...
    #   Q2-A: descifra el handle EN MEMORIA, re-autentica contra Futmondo y devuelve la SESIÓN
    #   reconstruida (o None). El handle descifrado nunca sale de este método.
    # resolve(user_id) -> ReauthMaterial | None  # INTERNO-PRIVADO; no forma parte de la API que usa SessionService (evita Q2-B)
```

> **Nota de contrato (C1):** el contrato C1 (contract-summary.md) fijó la *frontera*, no la
> implementación fina, y advirtió que el mecanismo se decidía en NFR Design (FR5.2). Esta etapa
> resuelve FR5.2 (Q1-A/Q2-A) y por tanto **precisa** la interfaz: la operación de cara a
> `SessionService` devuelve la sesión reconstruida (`reauthenticate`), y `resolve` queda como
> detalle interno. Es un cambio aditivo/de refinamiento dentro de la misma unidad y proceso;
> Code Generation implementa esta forma, coherente con Q2-A.

- **Defensa en profundidad:**
  1. La contraseña no se persiste (elimina la clase de fuga de la contraseña en reposo).
  2. El handle se guarda **cifrado** en reposo (clave de Fly.io); un volcado de la fila no expone
     material reutilizable en claro (cierra R-01).
  3. El handle descifrado solo vive dentro de `reauthenticate` (Q2-A); no cruza la frontera.
  4. Fallos = excepciones tipadas del dominio, nunca `except: pass` (BR1.4) — no se filtra el
     secreto en trazas ni mensajes.
  5. gitleaks bloqueante en el gate de MR (NFR1.4).

## Cifrado en tránsito y en reposo

- **En tránsito:** todo el tráfico va por HTTPS (nginx en Fly.io) — sin cambios. La conexión a Neon
  usa TLS.
- **En reposo:** la contraseña no se persiste (no hay contraseña que cifrar). El handle de re-auth,
  que SÍ es material portador reutilizable, se guarda **cifrado a nivel de aplicación** (AES-GCM /
  Fernet) con la clave `FUTMONDO_CRED_KEY` gestionada como secret de Fly.io. El cifrado de aplicación
  se suma al TLS de Neon (defensa en profundidad): un volcado de la tabla no expone el handle en
  claro. Es la vía que NFR1.2 contempla, a coste 0€ (una variable de entorno, sin servicio nuevo).

## Validación de entrada

La superficie de entrada nueva es mínima: `ensureSession(user_id)` recibe un `user_id` que ya viene
de un JWT válido (Bearer verificado aguas arriba). No hay entrada de usuario libre nueva. El `user_id`
se usa como clave en consultas parametrizadas (nunca concatenación de SQL) a través de la capa
`stores/` (evita inyección; corrige el patrón brownfield de SQL-en-router).

## Manejo de secretos

- `JWT_SECRET`: sigue exigiéndose no-default en el arranque (NFR1.3, guard `test_jwt_startup.py`
  existente). Esta unidad no lo relaja; verificación anclada a ese test (R-04).
- **`FUTMONDO_CRED_KEY` (clave de cifrado del handle):** único secreto nuevo, gestionado como
  `secret` de Fly.io — **nunca literal en el repo** (team.md). No entra en el código ni en el
  workflow; gitleaks bloqueante en MR (NFR1.4) actúa como red. Rotación: al rotar la clave, el
  `scheme` versionado (`aesgcm-v1` → `v2`) permite re-cifrar en el siguiente login sin migración
  dura; los handles antiguos caducan por TTL (12h).
- No se introduce ningún otro secreto en el repo (NFR1.4).

## Logging seguro (refuerzo de NFR1.1) — con control determinista (corrige R-05)

Ver observability-design. Regla dura: los eventos de sesión loggean `user_id`, `outcome`, `event`,
correlation-id — **NUNCA** la contraseña, el handle (cifrado o descifrado) ni `protected_material`.

Para no depender solo de disciplina humana, se añade un **control determinista**: el tipo que
transporta material sensible (`ReauthMaterial` / `FutmondoSession` en la medida en que lleve el
handle) define `__repr__`/`__str__` **redactados** (p. ej. `<ReauthMaterial redacted>`) y no es
serializable a JSON por defecto. Así, un log o traza accidental no imprime el secreto por
construcción, no por convención.

```python
# Ilustrativo (≤15 líneas)
class ReauthMaterial:
    __slots__ = ("_secret",)
    def __repr__(self) -> str: return "<ReauthMaterial redacted>"
    __str__ = __repr__
    # sin __dict__ (slots) y sin serializador JSON -> no se filtra en logs/repr
```

Fallos de descifrado/almacén se loggean como error tipado **sin** el valor sensible (Q4-A).

## Cabeceras de seguridad

Sin cambios respecto al comportamiento existente; esta unidad no añade endpoints nuevos ni superficie
HTTP nueva (contract-summary: ninguna API pública nueva). El cambio 403→401 accionable (FR1.3) es de
comportamiento dentro de un endpoint existente.

## ADR — No persistir la contraseña; handle de re-auth cifrado en reposo

- **Contexto:** FR5.2 dejó abierto cifrar-en-reposo vs. no-persistir. Regla dura: nunca contraseña en
  claro. Restricción: coste 0€, sin servicios nuevos.
- **Decisión:** (1) NO persistir la contraseña; guardar solo un handle de re-auth derivado del login.
  (2) Tratar ese handle como secreto en reposo: **cifrarlo** con clave `FUTMONDO_CRED_KEY` gestionada
  como secret de Fly.io. (3) El re-auth ocurre dentro de `CredentialProtection` (`reauthenticate`),
  que devuelve la sesión reconstruida; el handle descifrado nunca cruza la frontera (Q2-A).
- **Consecuencias (+):** la contraseña nunca se persiste; el handle no es legible en reposo aunque se
  vuelque la tabla; superficie de fuga mínima; coste 0€. **(−):** hay que gestionar y rotar una clave
  de Fly.io (mitigado: `scheme` versionado + TTL 12h); si el handle caduca, la re-auth no es
  transparente y el usuario ve un 401 accionable (FR1.3) — aceptado, es la degradación ya diseñada.
- **Alternativa rechazada:** cifrar la **contraseña** en reposo — más valor si se filtra (llave
  maestra, no caduca) que cifrar un token de sesión de vida corta.
- **Alternativa rechazada:** guardar el handle en claro apoyándose solo en TLS/Neon — deja material
  portador reutilizable legible en reposo (era el defecto R-01).

## Trazabilidad

| NFR | Solución de diseño |
|-----|--------------------|
| NFR1.1 | La contraseña no se persiste ni se loggea; ventana de plaintext en `protect` acotada (efímera, no retenida, no logueada); tipo redactado como control determinista |
| NFR1.2 | Handle solo accesible tras `CredentialProtection`; **cifrado en reposo** con clave de Fly.io; re-auth interno (`reauthenticate`, Q2-A); `resolve` interno-privado |
| NFR1.3 | Guard de arranque `JWT_SECRET` no-default intacto; verificación anclada a `test_jwt_startup.py` |
| NFR1.4 | Único secreto nuevo (`FUTMONDO_CRED_KEY`) como secret de Fly.io, nunca en repo; gitleaks bloqueante en MR |
