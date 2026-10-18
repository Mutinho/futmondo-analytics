# Requirements — F1: Login nativo end-to-end (app iOS Swift)

> Fase: inception (requirements-analysis). Requisitos funcionales (FR) y no funcionales (NFR),
> testables y trazables. Idioma: castellano; tokens técnicos verbatim en inglés. IDs estables.

## Requisitos funcionales

### FR-1 — Login nativo
El usuario introduce email y password de Futmondo en la pantalla de login nativa; la app llama a
`POST /auth/login` y, si es 200, obtiene el access token y queda autenticado.
- **Criterio**: con credenciales válidas → sesión activa; con credenciales inválidas (401) → se
  muestra un mensaje de error accionable y se permanece en login.
- **Traza**: intent-statement §1-2; scope F1-U3; `auth/routes.py` login.

### FR-2 — Almacenamiento del access token en memoria
El access token se mantiene **solo en memoria** del proceso; nunca se persiste en claro.
- **Criterio**: el access token no aparece en `UserDefaults`, plist ni disco.
- **Traza**: C-02; `auth.service.ts` (access en memoria).

### FR-3 — Almacenamiento del refresh token en iOS Keychain
El refresh token se guarda en **iOS Keychain** (Keychain Services), nunca en claro.
- **Criterio**: tras login, el refresh token está en Keychain; no aparece en `UserDefaults`/plist.
- **Traza**: C-02; [memory:M2]; FR del scope F1-U3.

### FR-4 — Transporte del refresh token (ajuste aditivo del backend, D-01)
`POST /auth/login` devuelve el refresh token **también en el body**; `POST /auth/refresh` y
`POST /auth/logout` **aceptan** el refresh token por body/header, además del canal cookie actual.
- **Criterio**: existe al menos un camino no-cookie para refresh/logout; la cookie `HttpOnly`
  sigue funcionando para la PWA sin cambios (FR-9).
- **Traza**: D-01; P-2; `auth/routes.py`.

### FR-5 — Refresh automático de sesión
Al arrancar la app, si hay refresh token en Keychain, se intenta `POST /auth/refresh` (auto-login
silencioso). Ante un 401 en una llamada protegida, la app refresca y **reintenta la petición
exactamente una vez**; si el refresh falla, borra el Keychain y fuerza re-login.
- **Criterio**: expiración del access token → refresh transparente + un reintento; refresh
  inválido/revocado (401) → borra Keychain y re-login.
- **Criterio (fallo transitorio)**: ante **fallo de red o 5xx** en el refresh, el Keychain **se
  preserva** (no se borra); se reintenta en el siguiente arranque/llamada. Solo un **401 /
  revocación** borra el Keychain.
- **Traza**: intent-statement criterio 3 (Q3=A); `auth.interceptor.ts`.

### FR-6 — Logout
El logout llama a `POST /auth/logout` (revoca en backend), borra el refresh token del Keychain y
limpia el access token en memoria.
- **Criterio (red OK)**: tras logout, el refresh token queda **revocado en backend** y no hay
  tokens en memoria ni Keychain.
- **Criterio (red caída)**: el estado local (memoria + Keychain) se limpia igualmente; la
  revocación en backend queda **pendiente** y se documenta como tal (no bloquea el logout local).
- **Traza**: intent-statement criterio 4; `auth/routes.py` logout.

### FR-7 — Cliente de red con Bearer
El cliente de red adjunta `Authorization: Bearer <access>` a las llamadas `/api/v1/*` y expone una
base URL configurable; mapea errores (401/403/5xx/red) a tipos Swift accionables.
- **Criterio**: una llamada de humo a `GET /api/v1/user/me` con token válido responde 200 y con
  token ausente/ inválido responde 401 mapeado a un error tipado.
- **Traza**: scope F1-U2 (Q2=A); `dependencies.py`/`AuthMiddleware`.

### FR-8 — Polish nativo del login (SwiftUI, sin dependencias externas)
La pantalla de login usa UX nativa (animaciones, autorrelleno de contraseña, haptics, materiales)
con **solo SDK de Apple**, respetando Reduce Motion / Dynamic Type / VoiceOver.
- **Criterio**: con Reduce Motion activo, las animaciones se degradan a transiciones instantáneas;
  autorrelleno de contraseña disponible vía `.textContentType`.
- **Traza**: decisión del propietario (rough-mockups opción A); P-3.

### FR-9 — Sin regresión de la PWA
El ajuste del backend no altera el comportamiento del login/refresh/logout por cookie `HttpOnly`
que usa la PWA Angular.
- **Criterio**: los tests `pytest` del canal cookie siguen verdes tras el ajuste.
- **Criterio (nuevo transporte)**: existe un test `pytest` nuevo que cubre el camino aditivo
  **no-cookie** (body/header) de login/refresh/logout, aseverando su efecto (NFR-3, P-2).
- **Traza**: C-03; R-01; P-2.

## Fuera de alcance (reafirmado del scope-document)

- Face ID / Touch ID (diferido, fast-follow; amplía B-03).
- Pantallas de datos y navegación/tab bar (F2/F3).
- Cambios de backend más allá del transporte del refresh token (D-01).
- App Store pública, Android, refirmado ~7 días, widgets, push.

## Requisitos no funcionales

### NFR-1 — Seguridad de credenciales
Ninguna credencial ni token se registra en claro (logs, excepciones) ni se persiste fuera del
Keychain. El `JWT_SECRET` no-default fail-fast del backend se mantiene.
- **Traza**: [memory] credenciales nunca en claro; `jwt_startup`.

### NFR-2 — Coste 0 €
Sin dependencias de pago ni librerías de terceros en el cliente nativo (solo SDK de Apple). Firma
gratuita de Apple ID.
- **Traza**: C-01; P-3; [memory:M1].

### NFR-3 — Compatibilidad de verificación
Backend: build + `pytest` verdes + gate de CI bloqueante. Cliente nativo: validación manual
documentada en el iPhone 13 Pro (login → refresh → logout); arnés de test nativo como deuda
registrada.
- **Traza**: scope Definición de hecho (Q5=A); P-1.

### NFR-4 — Idioma
Identificadores/código/comentarios Swift en inglés; textos de UI y mensajes de commit en
castellano.
- **Traza**: C-04; P-4.

## Sources

- [consumes] intent-statement, scope-document, team-practices de F1; codekb
  (business-overview, architecture, code-structure).
- [code] `auth/routes.py`, `dependencies.py`, `auth.service.ts`, `auth.interceptor.ts`.

## Assumptions & Open Questions

- [assumption] El **cómo exacto** del transporte del refresh token (body vs. header, nombre del
  campo) se fija en diseño (functional-design/contract-design); FR-4 fija el principio, no la
  firma concreta.
