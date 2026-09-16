# Contract Design — Preguntas de contrato

> Etapa de Inception (arquitecto + plataforma). Fija los contratos formales que el
> sistema debe honrar. En este intent, el DAG de Units Generation no tiene aristas
> (U1 y U2 independientes, sin contrato de dominio entre ellas) y no se crea API
> externa nueva; el contrato formal a fijar es la **interfaz de `CredentialProtection`**
> (frontera de seguridad intra-U1) que el diseño de dominio difirió aquí. Responde en
> el tag `[Answer]:`. `X. Other (please specify)` siempre disponible.

## Sources

- units-generation/unit-of-work.md (U1, U2; kind service; embebidas en futmondo-api) [scope]
- units-generation/unit-of-work-dependency.md (DAG sin aristas; sin contrato inter-unidad) [scope]
- domain-design/components.md (CredentialProtection: protect/resolve/canReauthenticate; ProtectedCredential) [scope]
- domain-design/decisions.md (ADR-003: elección fina FR5.2 diferida) [scope]
- requirements-analysis/requirements.md (FR5.1/FR5.2, FR1.2/FR1.3, NFR1) [scope]

---

## Q1 — Confirmación del conjunto de fronteras a formalizar

¿Confirmas que las únicas fronteras de contrato de este intent son las de abajo?

- A. **Sí**: (1) ninguna frontera inter-unidad (U1 y U2 independientes, sin API entre ellas);
  (2) ninguna API pública/externa nueva (los endpoints `/auth/*` y `/api/v1/*` existentes
  no cambian su contrato observable; el cambio 403→401 de FR1.3 es mejora de comportamiento
  dentro de un endpoint existente, no una API nueva); (3) el único contrato formal a fijar es
  la **interfaz interna de `CredentialProtection`** dentro de U1.
- B. **No**: hay alguna frontera adicional (indícala en Other).

[Answer]: A

---

## Q2 — Mecanismo de la interfaz `CredentialProtection`

¿Cómo se modela el contrato de la frontera de credenciales (consumida por `SessionService` dentro de U1)?

- A. **Interfaz interna de código (contrato de módulo Python)**: una clase/Protocol con métodos
  `protect(user_id, plaintext) -> None`, `resolve(user_id) -> ReauthMaterial | None`,
  `can_reauthenticate(user_id) -> bool`, más el manejo de errores. No es API de red (no OpenAPI/AsyncAPI);
  es un contrato de tipos/comportamiento in-proc, coherente con el monolito modular.
- B. **Contrato de esquema compartido** (tabla/estructura de `ProtectedCredential`) como shared-schema,
  sin interfaz de métodos.

[Answer]: A

---

## Q3 — Propiedad y política de cambios de la interfaz

- A. **Dueño: el componente `CredentialProtection`** (dentro de U1). Cambios que rompan la firma
  requieren actualizar `SessionService` en el mismo Bolt (misma unidad); cambios aditivos
  (nuevos métodos/params opcionales) son seguros. Versionado in-proc por firma de tipos, sin
  versionado de API de red.
- B. Otra política (indícala en Other).

[Answer]: A

---

## Q4 — Comportamiento de error/timeout de la interfaz

¿Qué contrato de fallo expone `CredentialProtection` hacia `SessionService`?

- A. **Fallo explícito y sin exponer secretos**: `resolve` devuelve `None` cuando no hay medio de
  re-auth disponible (⇒ `SessionService` cae a FR1.3, 401 accionable); errores de descifrado/almacén
  se propagan como excepción tipada del dominio (no un `except: pass`), nunca devolviendo el
  `password` en claro ni registrándolo. Sin reintentos internos (la BD es la autoridad; el reintento,
  si aplica, es del llamador).
- B. Otra semántica (indícala en Other).

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen del contrato que se materializará en `contract-summary.md`:

**Conjunto de fronteras (Q1-A):**
- Fronteras inter-unidad: **ninguna** (U1 y U2 independientes; DAG sin aristas).
- API pública/externa nueva: **ninguna** (endpoints existentes sin cambio de contrato; 403→401 de FR1.3 es mejora de comportamiento intra-endpoint).
- Contrato formal a fijar: **1** — la interfaz interna de `CredentialProtection` (intra-U1).

**Contrato C1 — `CredentialProtection` (interfaz interna, in-proc):**
- **Mecanismo (Q2-A):** `Protocol`/clase Python (no API de red); métodos `protect(user_id, plaintext) -> None`, `resolve(user_id) -> ReauthMaterial | None`, `can_reauthenticate(user_id) -> bool`.
- **Proveedor:** `CredentialProtection` (U1). **Consumidor:** `SessionService` (U1).
- **Propiedad/cambios (Q3-A):** dueño `CredentialProtection`; cambios que rompan la firma se resuelven con su único llamador en el mismo Bolt; aditivos seguros; versionado por firma de tipos, sin versionado de red.
- **Error/timeout (Q4-A):** `resolve` devuelve `None` si no hay medio de re-auth (⇒ FR1.3, 401 accionable); errores de descifrado/almacén como excepción tipada del dominio (no `except: pass`); nunca devolver ni registrar el `password` en claro (FR5.1/NFR1); sin reintentos internos (BD autoridad, ADR-005).

**Nota:** el mecanismo concreto de protección (cifrado en reposo vs. re-auth, FR5.2) sigue diferido a Functional/NFR design; este contrato fija la *frontera*, no la implementación.

[Answer]: Looks correct
