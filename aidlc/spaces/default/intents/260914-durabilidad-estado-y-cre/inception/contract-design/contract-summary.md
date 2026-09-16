# Contract Summary — Durabilidad del estado y credenciales

> Etapa Contract Design (Inception). Mapea todas las fronteras de contrato del intent.
> El DAG de Units Generation no tiene aristas (U1 y U2 independientes) y el intent no
> crea API externa nueva; el único contrato formal a fijar es la **interfaz interna de
> `CredentialProtection`** (frontera de seguridad intra-U1), que el diseño de dominio
> (ADR-003) difirió a esta etapa. El mecanismo fino de protección (cifrado vs. re-auth,
> FR5.2) sigue diferido a Functional/NFR design; aquí se fija la frontera, no la
> implementación.

## Sources

- units-generation/unit-of-work.md, unit-of-work-dependency.md (U1, U2; DAG sin aristas) [scope]
- domain-design/components.md (CredentialProtection, ProtectedCredential) [scope]
- domain-design/decisions.md (ADR-003 credencial; ADR-005 BD autoridad) [scope]
- requirements-analysis/requirements.md (FR5.1/FR5.2, FR1.2/FR1.3, NFR1) [scope]
- contract-design-questions.md (Q1–Q4) [Q1] [Q2] [Q3] [Q4]

## Fronteras del sistema (alcance)

- **Inter-unidad:** ninguna. U1 (`u1-durable-session`) y U2 (`u2-durable-sync-tasks`) son
  independientes (DAG sin aristas) y no exponen contrato de dominio entre sí; solo comparten
  el abstractor `db_connection` preexistente. [Q1-A]
- **API pública/externa nueva:** ninguna. Los endpoints existentes (`/auth/refresh`,
  `/api/v1/sync/trigger`, `/api/v1/sync/task/{id}`, y el resto de `/api/v1/*`) conservan su
  contrato observable. El cambio de `403` a `401` accionable (FR1.3) es una mejora de
  comportamiento dentro de un endpoint existente, no una API nueva a formalizar aquí. [Q1-A]
- **Contrato formal a fijar:** 1 — la interfaz interna de `CredentialProtection` (intra-U1).

## Contracts table

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---------------|----------|-----------|-------|
| C1 | u1-durable-session (`CredentialProtection`) | u1-durable-session (`SessionService`) — in-proc | Interfaz de código Python (`Protocol`) | `CredentialProtection` |

## Contrato C1 — `CredentialProtection` (interfaz interna in-proc)

Contrato de comportamiento/tipos dentro de un único proceso (`futmondo-api`); no cruza la red,
por lo que no aplica OpenAPI/AsyncAPI. Se especifica como interfaz de código (Q2-A).

```yaml
# in-proc interface contract (Python Protocol) — CredentialProtection
kind: code-interface
language: python
protocol: CredentialProtection
methods:
  - name: protect
    signature: "protect(user_id: str, plaintext_credential: str) -> None"
    purpose: >
      Store the reauthentication material for a user WITHOUT persisting the Futmondo
      password in clear text (FR5.1). The concrete scheme (encrypt-at-rest with a
      Fly.io-managed secret, or store no password and rely on re-auth) is decided in
      Functional/NFR design (FR5.2); this signature does not commit to either.
    errors:
      - "raises CredentialProtectionError on storage/encryption failure (typed domain exception; never `except: pass`)"
    security:
      - "MUST NOT persist or log the plaintext credential (FR5.1 / NFR1)"
  - name: resolve
    signature: "resolve(user_id: str) -> ReauthMaterial | None"
    purpose: >
      Return the material SessionService needs to transparently rebuild the Futmondo
      session after a restart (FR1.2). Returns None when no reauthentication means is
      available, which drives SessionService to the actionable-401 path (FR1.3).
    returns:
      - "ReauthMaterial: opaque handle sufficient to re-authenticate (never the raw password exposed to the caller)"
      - "None: no reauth means available -> caller falls back to FR1.3 (401 accionable)"
    errors:
      - "raises CredentialProtectionError on decryption/store failure (typed; not silent)"
    security:
      - "MUST NOT return or log the plaintext password (FR5.1 / NFR1)"
  - name: can_reauthenticate
    signature: "can_reauthenticate(user_id: str) -> bool"
    purpose: "Cheap predicate for whether resolve() would yield a usable means, so SessionService can branch FR1.2 vs FR1.3 without materializing secrets."
    errors: []
retry_policy: "none internal — the DB is the authority (ADR-005); any retry is the caller's decision"
```

> **Nota de armonización de nombre (R-01):** `can_reauthenticate` es la forma **canónica**
> del contrato (snake_case, idiomática en Python). El diseño de dominio (`components.md`) y la
> pregunta Q2 se refieren a la misma operación con `canReauthenticate` (camelCase). Es **una
> sola operación**; Functional/NFR design y Code Generation deben usar la forma del contrato
> (`can_reauthenticate`) y no crear un segundo método.

## Contract ownership rules

- **Dueño de C1:** el componente `CredentialProtection` (dentro de U1). [Q3-A]
- **Cambios que rompen la firma:** se resuelven actualizando su único consumidor
  (`SessionService`) en el mismo Bolt, porque proveedor y consumidor viven en la misma
  unidad y el mismo proceso. No hay coordinación entre equipos ni compatibilidad de red.
- **Cambios aditivos** (nuevos métodos o parámetros opcionales): seguros; los consumidores
  ignoran lo que no usan.
- **Versionado:** por firma de tipos (verificado por el type-checker/tests), sin versionado
  semántico de API de red ni ventanas de deprecación (sería sobre-ingeniería para un contrato
  in-proc intra-unidad).
- **Seguridad como parte del contrato:** ningún método devuelve, persiste ni registra el
  `password` en claro (FR5.1/NFR1); los fallos son excepciones tipadas del dominio, nunca
  `except: pass`.

## Open questions

| Contract | Question | Blocks |
|----------|----------|--------|
| C1 | Mecanismo fino de protección: cifrado en reposo (clave gestionada como secret de Fly.io) vs. no persistir la contraseña (re-auth). Se decide en Functional/NFR design (FR5.2). | No bloquea Contract Design (la frontera es estable); condiciona la implementación de `protect`/`resolve` en Construction. |
