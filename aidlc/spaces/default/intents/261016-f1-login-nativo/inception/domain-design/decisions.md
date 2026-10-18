# Domain Design — Decisiones (ADRs) (F1: Login nativo end-to-end)

> Fase: inception (domain-design). Cada ADR incluye Context, Decision, Consequences, Alternatives
> Rejected (guardrail de inception). Idioma: castellano; tokens técnicos verbatim en inglés.

## ADR-1 — Transporte del refresh token: aditivo cookie + body/header

- **Context**: `/auth/refresh` y `/auth/logout` leen hoy el refresh token **solo** de la cookie
  `HttpOnly`; `/auth/login` no lo devuelve en el body. Un cliente nativo iOS no maneja cookies de
  navegador. La PWA en producción no debe sufrir regresión (FR-9, R-01).
- **Decision**: ajuste **aditivo**: el login devuelve el refresh token también en el body; refresh
  y logout aceptan el refresh token por **cookie O body/header**. Se reutiliza la cripto existente
  (`verify_token`, `hash_token`, revocación por `sha256`).
- **Consequences**: el cliente nativo funciona sin cookies; la PWA sigue igual; se añaden tests
  `pytest` de ambos canales. Pequeño aumento de superficie en `auth/routes.py` (acotado, tras
  función estrecha, sin ampliar god-files).
- **Alternatives rejected**: (a) **endpoints nuevos `/auth/native/*`** — duplica lógica y
  mantenimiento; (b) **mover el refresh token a header obligatorio** — rompería la PWA (regresión);
  (c) **ampliar CORS para origen nativo con cookies** — más frágil y acopla el cliente nativo al
  modelo de cookies del navegador.

## ADR-2 — Refresh token en iOS Keychain; access token en memoria

- **Context**: regla durable de seguridad: credenciales/tokens nunca en claro ([memory:M2],
  NFR-1). El cliente nativo necesita persistir la sesión entre arranques (FR-5).
- **Decision**: refresh token en **iOS Keychain** (framework `Security`), vía `KeychainStore`
  (C2); access token **solo en memoria** del proceso, espejando la PWA.
- **Consequences**: la sesión sobrevive a reinicios de la app de forma segura; al cerrar sesión se
  borra el Keychain. El acceso al almacén seguro queda encapsulado en un único componente testeable.
- **Alternatives rejected**: (a) **`UserDefaults`/plist** — almacenamiento en claro, viola la
  regla durable; (b) **access token también en Keychain** — innecesario (es efímero, 1h) y añade
  I/O; (c) **librería de terceros (KeychainAccess)** — viola "solo SDK de Apple" (NFR-2/P-3).

## ADR-3 — Capas separadas: NetworkClient / KeychainStore / AuthService / ViewModel / View

- **Context**: F1 debe quedar testeable pese a no tener aún arnés XCTest (P-1); la lógica de red y
  de credenciales no debe vivir en la UI.
- **Decision**: separación en C1–C5: `NetworkClient` (HTTP puro), `KeychainStore` (almacén),
  `AuthService` (orquestación de sesión **y dueño único del reintento**, un `actor`),
  `AuthViewModel` (estado de UI; **refleja**, no reintenta), `View` (SwiftUI sin lógica).
  Dependencias inyectables para poder doblarlas en el arnés `swift test`.
- **Consequences**: cuando llegue XCTest (deuda registrada), las capas son unit-testables con
  dobles; en F1 la verificación es manual pero el diseño ya es testable.
- **Alternatives rejected**: (a) **todo en la View** — no testeable, acopla UI y red/credenciales;
  (b) **un único "god object" de auth** — contradice el espíritu de no-god-files del proyecto.

## ADR-4 — Reintento único ante 401, sin bucle

- **Context**: el access token caduca (1h); el refresh debe ser transparente (FR-5, US-4) sin
  entrar en bucles de reintento.
- **Decision**: ante 401 en una llamada protegida, **`AuthService` (dueño único)** refresca y
  reintenta la petición **exactamente una vez**; `AuthViewModel` solo refleja el estado y **no
  reintenta** (evita doble reintento). Si el reintento vuelve a 401 o el refresh falla por
  401/revocación → re-login. Fallo de red/5xx en el refresh → preserva Keychain y reintenta más
  tarde. (Precisado en construcción Bolt 3: `AuthService` es un `actor` y el refresh es
  **coalescido** —una sola operación en vuelo compartida— para no disparar N refresh en paralelo.)
- **Consequences**: comportamiento predecible y testable; sin tormentas de reintentos.
- **Alternatives rejected**: (a) **reintentos múltiples con backoff** — innecesario para F1 y
  arriesga bucles; (b) **sin reintento** — peor UX (re-login ante cada expiración).

## Sources

- [consumes] requirements.md, stories.md, architecture.md, team-practices.md.
- [code] `auth/routes.py`, `jwt_utils.py`, `auth.service.ts`, `auth.interceptor.ts`.

## Assumptions & Open Questions

None.
