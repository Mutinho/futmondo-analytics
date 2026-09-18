# Arquitectura — futmondo-analytics

## Visión General del Sistema

futmondo-analytics es un sistema de dos servicios desplegados por separado en Fly.io
(región `cdg`/París), respaldados por una base de datos Neon PostgreSQL (Frankfurt):

- **Backend** `futmondo-api`: aplicación FastAPI (Python 3.12), puerto 8000, healthcheck
  `/health`.
- **Frontend** `futmondo-app`: SPA/PWA Angular 22 servida por nginx (puerto 80), que además
  actúa como reverse proxy hacia el backend para `/api/*` y `/auth/*`.

## Estilo Arquitectónico

**Monolito modular con frontend desacoplado.** El backend es un único despliegue FastAPI
con submódulos internos por responsabilidad (`api`, `auth`, `core`, `services`, `stores`,
`security`, `models`); no hay microservicios. La integración externa (Futmondo, Sofascore)
se hace vía clientes HTTP dentro de `services/`. El frontend es un despliegue independiente
que consume el backend por HTTP. Evidencia: routers montados en un solo `main.py`, un solo
`fly.toml` por servicio, sin buses de eventos ni colas.

El inventario completo de componentes y sus dependencias está en `component-inventory.md`;
aquí se describen relaciones y flujos, no el catálogo.

## Relaciones entre Componentes

```mermaid
graph TD
    Browser["Navegador / PWA (Angular 22)"]
    Nginx["nginx (futmondo-app)"]
    API["FastAPI (futmondo-api)"]
    MW["AuthMiddleware"]
    Auth["auth (JWT, token_store, session_store)"]
    Endpoints["api/v1/endpoints (routers)"]
    Services["services (clientes externos + lógica)"]
    Stores["stores (durabilidad)"]
    DB["Neon PostgreSQL"]
    Futmondo["API Futmondo"]
    Sofascore["API Sofascore"]

    Browser --> Nginx
    Nginx --> API
    API --> MW
    MW --> Endpoints
    MW --> Auth
    Endpoints --> Services
    Endpoints --> Auth
    Auth --> Stores
    Services --> Stores
    Stores --> DB
    Auth --> DB
    Services --> Futmondo
    Services --> Sofascore
```

<!-- Text fallback: el navegador (Angular PWA) habla con nginx, que hace reverse proxy a FastAPI. Toda petición pasa por AuthMiddleware, que enruta a los routers de api/v1/endpoints y consulta el módulo auth. Los routers usan services (clientes de Futmondo/Sofascore) y auth; ambos persisten vía stores hacia Neon PostgreSQL; auth también accede directamente a la BD para tablas de refresh tokens. -->

## Diagramas de Interacción

Cómo se implementan dos transacciones de negocio representativas a través de los componentes.

### Transacción: puja en el mercado (FR6)

```mermaid
sequenceDiagram
    participant U as Navegador
    participant N as nginx
    participant MW as AuthMiddleware
    participant M as market.place_bid
    participant H as _helpers.get_user_futmondo_client
    participant F as API Futmondo

    U->>N: POST /api/v1/market/bid (Bearer, price)
    N->>MW: reenvía petición
    MW->>MW: verify_token(expected_type="access")
    MW->>M: enruta si token válido
    M->>M: (FR6) NO valida price hoy
    M->>H: get_user_futmondo_client()
    H->>F: POST {base_url}/1/market/bid
    F-->>M: resultado de puja
    M-->>U: respuesta
```

<!-- Text fallback: el navegador envía POST /api/v1/market/bid con Bearer token y price. nginx lo reenvía; AuthMiddleware verifica el access token y enruta a place_bid. place_bid hoy NO valida price (hallazgo FR6), obtiene el cliente Futmondo del usuario vía _helpers y proxya la puja a POST /1/market/bid de Futmondo; la respuesta vuelve al navegador. -->

### Transacción: refresco de sesión (FR9)

```mermaid
sequenceDiagram
    participant U as Navegador
    participant R as auth.routes /auth/refresh
    participant T as token_store.is_refresh_token_valid
    participant DB as Neon PostgreSQL

    U->>R: POST /auth/refresh (cookie HttpOnly)
    R->>T: is_refresh_token_valid(token_hash)
    T->>DB: SELECT revoked, expires_at
    DB-->>T: fila (expires_at aware en PostgreSQL)
    T->>T: (FR9) ternario de precedencia ambigua
    T-->>R: False erróneo para tokens activos aware
    R-->>U: 401 pese a token válido
```

<!-- Text fallback: el navegador llama POST /auth/refresh con la cookie HttpOnly. auth.routes invoca is_refresh_token_valid, que consulta revoked y expires_at en PostgreSQL. Con expires_at aware, el ternario de precedencia ambigua (hallazgo FR9) devuelve False para tokens activos futuros, provocando un 401 indebido. -->

## Flujo de Datos

Toda petición autenticada entra por nginx → `AuthMiddleware` (que exige `Authorization:
Bearer <access>` salvo rutas en `AUTH_EXCLUDED_PATHS`) → router → `services`/`auth` →
persistencia (`stores` o SQL crudo) → Neon PostgreSQL o proxy a Futmondo/Sofascore. La
ruta `/static/photos/*` (StaticFiles) queda fuera del prefijo protegido y se sirve sin auth.

## Decisiones de Diseño Clave

- **Access token en memoria + refresh token en cookie `HttpOnly`**: minimiza exposición del
  token a XSS a costa de un flujo de refresco (donde vive el bug FR9).
- **Proxy hacia Futmondo con credenciales por usuario**: el backend no guarda password en
  claro en sesión; usa la sesión Futmondo del usuario (12h TTL) — ver `NEVER almacenar la
  contraseña en claro` en las reglas del proyecto.
- **Persistencia mixta**: coexisten una capa `stores/` (durabilidad reciente) y SQL crudo
  disperso en `auth`/routers (deuda descrita en `code-quality-assessment.md`).

## Oportunidades de Mejora

- Introducir validación de entrada en el backend para pujas (FR6) tras una capa estrecha,
  sin ampliar el patrón SQL-en-router.
- Aislar de forma inequívoca `SSL_VERIFY` al entorno local (FR8).
- Consolidar el acceso a datos de auth en una capa repositorio para eliminar la clase de
  bugs naive/aware (FR9). El detalle de deuda vive en `code-quality-assessment.md`.
