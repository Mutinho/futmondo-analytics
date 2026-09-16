# Entities — u1-durable-session

> Diseño funcional (Construction). Modelo de entidades de la sesión durable y su credencial
> protegida. Técnicamente agnóstico; sin SQL ni código. El bloque `yaml` es la fuente de
> verdad; el resumen humano lo deriva.

## Sources

- requirements.md (FR1.1, FR5.1) [scope]
- domain-design/components.md (UserSession→SessionRepository; ProtectedCredential→CredentialProtection) [scope]
- contract-design/contract-summary.md (C1) [scope]
- functional-design-questions.md (Q1-A TTL absoluto, Q2-A una fila por user_id) [Q1] [Q2]

## Entity model (source of truth)

```yaml
entities:
  - name: UserSession
    owned_by: SessionRepository
    description: >
      Sesión Futmondo durable por usuario. Persiste el token de sesión y su vigencia
      (TTL absoluto de 12h) para poder reconstruir la sesión tras un reinicio del proceso.
      NO almacena la contraseña en claro; referencia la credencial protegida por user_id.
    attributes:
      - name: user_id
        type: string
        required: true
        unique: true
        constraints: identificador de la sesión; una fila por usuario (upsert)
      - name: email
        type: string
        required: true
        constraints: email Futmondo del usuario (identidad de login)
      - name: token
        type: string
        required: true
        constraints: token de sesión Futmondo obtenido del login/re-auth
      - name: created_at
        type: timestamp
        required: true
        constraints: instante de creación de la sesión
      - name: expires_at
        type: timestamp
        required: true
        constraints: created_at + 12h (TTL absoluto; no deslizante)
    entity_constraints:
      - una sola UserSession activa por user_id (upsert por user_id)
      - nunca contiene el password en claro (regla dura FR5.1)
      - una sesión con now > expires_at se trata como ausente (purga perezosa al leer)
    relationships:
      - references: ProtectedCredential
        owned_by: CredentialProtection
        cardinality: "cada UserSession referencia como máximo una ProtectedCredential del mismo user_id (1:0..1)"
        direction: UserSession → ProtectedCredential

  - name: ProtectedCredential
    owned_by: CredentialProtection
    description: >
      Material de credencial protegido para poder re-autenticar al usuario contra Futmondo
      al reconstruir su sesión. El mecanismo concreto (cifrado en reposo con clave gestionada
      como secret de Fly.io, o no-persistencia con re-auth) se decide en NFR Design (FR5.2);
      esta entidad modela la frontera, no la implementación.
    attributes:
      - name: user_id
        type: string
        required: true
        unique: true
        constraints: identificador; una fila por usuario
      - name: protected_material
        type: opaque
        required: false
        constraints: >
          representación protegida del medio de re-autenticación; NUNCA el password en claro.
          Su forma concreta depende del scheme (definido en NFR Design). Puede ser vacío si el
          scheme elegido no persiste credencial (re-auth puro), en cuyo caso can_reauthenticate=false.
      - name: scheme
        type: string
        required: true
        constraints: identificador del mecanismo de protección (p. ej. "encrypted-at-rest" | "none")
      - name: updated_at
        type: timestamp
        required: true
        constraints: última actualización del material protegido
    entity_constraints:
      - nunca almacena ni expone el password en claro (FR5.1/NFR1)
      - el material solo es descifrable/usable dentro de CredentialProtection
    relationships: []
```

## Resumen del modelo de entidades

- **`UserSession`** es la sesión Futmondo durable por usuario: identidad (`user_id`, `email`),
  el `token` de sesión y su vigencia absoluta (`created_at`/`expires_at`, 12h). Una fila por
  usuario (upsert). No porta el `password`; referencia a `ProtectedCredential` por `user_id`.
- **`ProtectedCredential`** encapsula el medio de re-autenticación protegido, tras la frontera
  de `CredentialProtection`. El `scheme` indica el mecanismo (cifrado en reposo vs. sin
  persistencia); la forma concreta de `protected_material` se fija en NFR Design (FR5.2).
- La relación es `UserSession → ProtectedCredential` (1:0..1 por `user_id`): la sesión sabe
  que existe una credencial protegida para su usuario, pero no accede a su contenido — eso es
  competencia exclusiva de `CredentialProtection` vía la interfaz C1.

> **Nota (esquema físico):** el mapeo a tablas Neon (nombres de columna, tipos SQL, migración
> `CREATE TABLE IF NOT EXISTS`) es un detalle de implementación de Code Generation sobre
> `db_connection`; aquí solo se fija la forma lógica.
