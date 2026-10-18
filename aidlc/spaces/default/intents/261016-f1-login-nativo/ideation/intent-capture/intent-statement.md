# Intent Statement — F1: Login nativo end-to-end (app iOS Swift)

> Fase: ideación (intent-capture). Prosa de encuadre, no implementación. Idioma de
> conversación: castellano; tokens técnicos (frameworks, rutas, endpoints, claves) verbatim
> en inglés. Fuentes: backlog y feasibility del intent `261016-ios-native-feasibility`,
> lectura del backend (`backend/app/auth/routes.py`) y del cliente Angular de referencia
> (`features/login`, `core/services/auth.service`).

## Intent

Construir la **primera capa funcional (F1) de la app iOS nativa** de Futmondo: un **login
nativo end-to-end** en Swift/SwiftUI que autentique contra el backend FastAPI existente y deje
la sesión lista para las pantallas de F2. Agrupa dos proto-Units del backlog:

- **B-02 — Cliente de red Swift**: capa HTTP tipada hacia `/auth/*` y `/api/v1/*` (base URL,
  serialización JSON, inyección del `Authorization: Bearer`, manejo de errores/estados HTTP),
  reutilizable por todas las pantallas posteriores.
- **B-03 — Auth nativa**: flujo de login (email/password Futmondo → JWT), persistencia del
  **refresh token en iOS Keychain** (nunca en claro), refresco de access token y logout.

El código Angular existente es la **especificación funcional de referencia** (no se porta); el
**backend FastAPI se reutiliza**, con el ajuste mínimo que exige D-01 (abajo).

## Por qué ahora (secuenciación risk-first)

F0 (spike `xtool`, intent `261016-xtool-spike`) ya validó la cadena build+firma+install en
vivo. F1 es el siguiente eslabón del camino crítico: sin red + auth no hay ninguna pantalla.
B-04/B-05 (Presupuesto, Mercado, F2) dependen de B-02 y B-03.

## Dependencia dura verificada (D-01) — ajuste de backend en alcance

Lectura directa de `backend/app/auth/routes.py`:

- `POST /auth/login` **no devuelve el refresh token en el body**; lo fija como cookie
  `HttpOnly` (`futmondo_refresh_token`, `path=/auth`, `samesite=lax`) vía `_set_refresh_cookie`.
- `POST /auth/refresh` lee el refresh token **sólo de esa cookie**
  (`futmondo_refresh_token: Optional[str] = Cookie(default=None)`); sin cookie responde `401`.
- `POST /auth/logout` revoca leyendo igualmente la cookie.

Un cliente Swift nativo **no gestiona cookies de navegador** de forma transparente. Por tanto,
F1 incluye un **ajuste mínimo y aditivo del backend** para que login/refresh/logout funcionen
por **header/body** además de por cookie, sin romper el cliente Angular/PWA actual (la cookie
`HttpOnly` sigue siendo el canal del navegador). Esto es un hecho, no un supuesto. El **cómo**
exacto del ajuste se decide en diseño (ver preguntas Q1).

## Resultado esperado (criterios de hecho, verificables)

1. Desde la app nativa en el iPhone 13 Pro: introducir email/password Futmondo → recibir
   access token y disponer de sesión activa.
2. El refresh token se guarda en **iOS Keychain**; nunca en `UserDefaults`/plist en claro.
3. Al caducar el access token, la app **refresca** sin re-login y reintenta la petición
   **exactamente una vez** (Q3=A); si el refresh token es inválido/revocado, fuerza re-login.
4. **Logout** revoca la sesión en backend y borra el token del Keychain.
5. El cliente de red adjunta `Authorization: Bearer <access>` a `/api/v1/*` y mapea errores
   (401/403/5xx/red) a tipos Swift accionables, verificado end-to-end con una llamada de humo a
   `/api/v1/user/me` (Q2=A).
6. La **PWA Angular existente sigue funcionando** sin regresión (el ajuste de backend es
   aditivo).
7. **Definición de hecho (Q5=A)**: build + `pytest` verdes para el ajuste de backend, y
   validación manual documentada en el iPhone 13 Pro (login → refresh → logout). El arnés de
   test de UI/dispositivo nativo queda como **deuda registrada**.

## Fuera de alcance (F1)

- Pantallas de datos (Presupuesto, Mercado, Favoritos, Calculadora) → F2/F3.
- Navegación nativa / tab bar (B-08) → F2.
- Reinstalación/refirmado de ~7 días (B-09), widgets (B-10), push (B-11).
- Cualquier cambio de backend más allá del ajuste aditivo de D-01.
- App Store pública, Android.

## Restricciones durables aplicables

- **Coste 0 €** recurrente (firma gratuita; sin dependencias de pago; librerías OSS pin exacto).
- **Nunca** credencial/refresh token en claro; refresh token en **iOS Keychain**.
- Identificadores/código en **inglés**; texto de usuario y commits (Conventional Commits con
  scope) en **castellano**.
- El gate de CI bloqueante del repo sigue aplicando a cualquier cambio de backend.

## Sources

- [desc] Descripción del intent F1 (login nativo end-to-end: B-02 + B-03), creada en este
  arranque.
- [backlog] `261016-ios-native-feasibility/ideation/scope-definition/intent-backlog.md`
  (B-02, B-03, dependencias, D-01).
- [feasibility] `261016-ios-native-feasibility/ideation/feasibility/feasibility-assessment.md`
  §5 (impacto en autenticación, Keychain, D-01).
- [code] `backend/app/auth/routes.py` (login/refresh/logout; cookie `HttpOnly`), verificado en
  esta etapa.
- [code] `angular-app/src/app/features/login/login.component.ts` (flujo de login de referencia).
- [memory:M1] Mandato de coste 0 € con excepción acotada de distribución nativa.
- [memory:M2] Refresh token en almacenamiento seguro nativo (iOS Keychain), nunca en claro.

## Assumptions & Open Questions

- [assumption] El ajuste de D-01 es **aditivo** (acepta token por header/body sin eliminar el
  canal cookie), de modo que la PWA no sufre regresión. A confirmar en diseño (Q1).
- [assumption] El backend ya emite JWT estándar reutilizables por un cliente nativo sin cambios
  en el formato del token (sólo cambia el transporte del refresh token). A confirmar leyendo
  `jwt_utils.py` en inception. **Impacto si resultara falso**: el alcance crecería más allá del
  "sólo transporte del refresh token" (tocaría el formato/emisión del token), lo que obligaría
  a revisar el encuadre de F1.
- Las preguntas abiertas de encuadre están en `intent-capture-questions.md`.
