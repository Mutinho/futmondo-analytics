# User Flow — F1: Autenticación nativa (iOS)

> Fase: ideación (rough-mockups). Flujos de usuario de la auth nativa. Idioma: castellano;
> tokens técnicos verbatim en inglés. Diagrama mermaid validado + fallback de texto.

## Flujo 1 — Arranque de la app (auto-login)

```mermaid
flowchart TD
    A[Arranca la app] --> B{Hay refresh token en Keychain?}
    B -- No --> C[Pantalla Login]
    B -- Si --> D[Splash: POST /auth/refresh con el refresh token]
    D --> E{Refresh OK?}
    E -- Si --> F[Access token en memoria -> pantalla autenticada]
    E -- No --> G[Borra Keychain -> Pantalla Login]
```

Fallback de texto: al arrancar, si no hay refresh token en Keychain → Login. Si lo hay → splash
que llama a `POST /auth/refresh`; si responde OK, guarda el access token en memoria y entra a la
app; si falla, borra el Keychain y va a Login.

## Flujo 2 — Login manual

```mermaid
flowchart TD
    A[Pantalla Login] --> B[Usuario introduce email y password]
    B --> C[POST /auth/login]
    C --> D{200 OK?}
    D -- No --> E[Muestra mensaje de error accionable]
    E --> A
    D -- Si --> F[Guarda access token en memoria]
    F --> G[Guarda refresh token en iOS Keychain]
    G --> H[Pantalla autenticada]
```

Fallback de texto: el usuario introduce email/password → `POST /auth/login`. Si no es 200,
muestra error y permanece en Login. Si es 200, guarda el access token en memoria y el refresh
token en Keychain, y entra a la app.

## Flujo 3 — Refresh ante expiración (401)

```mermaid
flowchart TD
    A[Peticion a /api/v1/* con Bearer] --> B{401?}
    B -- No --> C[Respuesta usada normalmente]
    B -- Si --> D[POST /auth/refresh con refresh token del Keychain]
    D --> E{Refresh OK?}
    E -- Si --> F[Reintenta la peticion UNA vez con el nuevo access token]
    E -- No --> G[Borra Keychain -> fuerza re-login en Login]
```

Fallback de texto: ante un 401 en una llamada protegida, la app refresca con el refresh token
del Keychain; si el refresh va bien, reintenta la petición **una** vez; si falla, borra el
Keychain y fuerza re-login (Q3=A).

## Flujo 4 — Logout

```mermaid
flowchart TD
    A[Usuario pide logout] --> B[POST /auth/logout]
    B --> C[Borra refresh token del Keychain]
    C --> D[Limpia access token en memoria]
    D --> E[Pantalla Login]
```

Fallback de texto: el logout llama a `POST /auth/logout` (revoca en backend), borra el refresh
token del Keychain, limpia el access token en memoria y vuelve a Login. Si la llamada de red
falla, igualmente limpia el estado local.

## Sources

- [consumes] intent-statement, scope-document de F1.
- [code] `angular-app/src/app/core/services/auth.service.ts` (flujos de login/refresh/recover/
  logout de referencia).

## Assumptions & Open Questions

None.
