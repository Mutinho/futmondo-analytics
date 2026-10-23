# Business Overview — Futmondo Analytics

## Qué es el producto

Futmondo Analytics es una aplicación web multi-usuario (PWA) para gestionar y
analizar campeonatos de **Futmondo** (fantasy football). Reutiliza las
credenciales del usuario en Futmondo para autenticarse contra la API oficial de
Futmondo, auto-detecta sus campeonatos y expone análisis financiero y de mercado
sobre los datos sincronizados. El sistema está **en producción** (Fly.io, región
`cdg`/París según `fly.toml`; `README.md` menciona París) con backend FastAPI,
frontend Angular y base de datos Neon PostgreSQL.

El `README.md` y `app/main.py` describen el servicio como *"API for analyzing
Futmondo player transactions and team evolution"*.

## Funcionalidades principales

- **Login (auth)**: el usuario entra con su email/password de Futmondo
  (`POST /auth/login`). El backend valida esas credenciales contra la API de
  Futmondo (`FutmondoClient.login()`), crea/actualiza un usuario interno
  (`app_users`) y emite un **JWT access token** (en memoria del navegador) más un
  **refresh token** entregado hoy **solo** por cookie `HttpOnly`. En el primer
  login se auto-detectan los campeonatos del usuario
  (`_auto_detect_championships`). **Relevante para F1 (login nativo iOS).**
- **Presupuesto (budget)**: saldos por equipo, altas/bajas, puja máxima y
  rendimiento (feature `budget/`, endpoints `/api/v1/analytics/balances`).
- **Mercado (market)**: jugadores del *computer* con puja sugerida, rating
  Sofascore y tendencia; modal de puja con min/max validados
  (`/api/v1/market/today`, `/api/v1/market/bid`; feature `market/`).
- **Sincronización (sync)**: sync asíncrono en background con progreso paso a
  paso (jugadores, transacciones, cláusulas, castigos, dream teams, rendimiento,
  plantillas, clasificación, odds, phantoms, Sofascore). Endpoints
  `/api/v1/sync/trigger` y `/api/v1/sync/task/{id}`; tareas durables
  (`task_service.py`, `task_repository.py`).
- **Finanzas (finances / player-finances)**: cálculo de dinero por usuario
  (presupuesto + puntos×€ + profit de transacciones + dream team + MVP +
  clasificación + castigos/bonificaciones). Endpoints `/api/v1/player-finances/`.
- **Clasificación, Evolución, Estadísticas, Clausulables, Analytics**: gráficos
  (Chart.js / ng2-charts) y tablas interactivas sobre los datos del campeonato.
- **Asistente AI**: chat con contexto del campeonato (`/api/v1/assistant`,
  `assistant_service.py`; proveedores Gemini/Groq vía claves de entorno).
- **PWA**: service worker (`ngsw-config.json`), manifest y meta tags Apple;
  instalable en iPhone Safari.

## Modelo multi-usuario

- Cada usuario tiene sus propios campeonatos, auto-detectados en el primer login
  contra Futmondo (`activechampionships`).
- Los endpoints `/api/v1/*` operan con las credenciales Futmondo del usuario
  logado: no hay credenciales globales obligatorias (`config.py` deja
  `FUTMONDO_EMAIL`/`FUTMONDO_PASSWORD` como opcionales/vacíos).
- Los datos del campeonato (transacciones, jugadores, standings) se comparten
  entre usuarios del mismo campeonato; la configuración por usuario
  (presupuesto, premios, cláusulas, equipo propio `futmondo_team_id`) vive en
  `user_championships`.

## Relevancia para F1 (login nativo iOS) — YA IMPLEMENTADO en `ios/`

El objetivo de F1 era un cliente nativo iOS (Swift/SwiftUI) que **reutiliza el
backend FastAPI**; esa capa **ya existe** en el repo bajo `ios/` (paquete
SwiftPM `FutmondoKit` + app `FutmondoApp`). El contrato de auth es la pieza
central: el refresh token viaja por cookie `HttpOnly` para el navegador, mientras
que el cliente nativo lo recibe en el body de `/auth/login` y lo reenvía en el
header `X-Refresh-Token` (ajuste **aditivo** D-01 del backend, ya consumido por
`AuthService`), guardándolo en **iOS Keychain**, nunca en claro. El flujo de
negocio (login → access en memoria + refresh de larga duración → refresh →
logout) se mantiene idéntico; F1 solo cambió el canal de transporte del refresh
token para el cliente nativo.

## Relevancia para F2 (Presupuesto nativo + selector de campeonato)

F2 construye la pantalla nativa de **Presupuesto** y el **selector de
campeonato** sobre la capa iOS de F1, reproduciendo la feature web `budget/` y
el `ChampionshipService` de Angular. No cambia el backend: consume los endpoints
ya existentes `/api/v1/analytics/balances` (saldos por equipo: balance, gastado,
ingresado, valor de plantilla, rendimiento, premios) y la lista de campeonatos
del usuario (`/api/v1/user/championships`, con fallback a `/api/v1/championships`).
El selector reproduce el patrón del `ChampionshipService` (campeonato activo
persistido localmente) con un almacén nativo en vez de `localStorage`.

## Relevancia para el sistema de diseño nativo iOS (intent 261018-design-system-nativo)

Este intent diseña el **sistema de diseño / theming de la app nativa iOS**
reproduciendo, como **fuente de verdad**, el tema visual del frontend Angular
existente. El objetivo de negocio es que la app nativa iOS se sienta como el
mismo producto que la PWA actual: misma identidad de marca (**verde** como color
primario, acentos **violeta**, tipografía **Roboto**), misma semántica de color
(dinero positivo verde / negativo rojo), mismo contraste y modo claro/oscuro, y
las mismas pantallas de referencia (login y shell de navegación). No introduce
cambios de backend ni de datos: es un intent de **diseño visual** cuyo insumo
primario es la capa de estilos del `angular-app`. Google Stitch quedó descartado
como referencia de diseño (decisión del propietario, 2026-10-18); la única
fuente de verdad es el tema de Angular.

## Sources

- `README.md`
- `backend/app/main.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/session_store.py`
- `backend/app/core/config.py`
- `backend/app/api/v1/endpoints/user.py`
- Listado de `backend/app/api/v1/endpoints/` y `angular-app/src/app/features/`
- `ios/Package.swift`, `ios/Sources/FutmondoKit/Auth/AuthService.swift` (capa nativa F1)
- `backend/app/api/v1/endpoints/{balances,user,championships}.py` (endpoints que consume F2)
- `angular-app/src/styles.scss` (tema de diseño — fuente de verdad del sistema de diseño nativo)

## Assumptions & Open Questions

- El detalle exacto del transporte alternativo del refresh token para iOS (D-01)
  y el formato del almacén en Keychain son decisiones de diseño de F1; aquí solo
  se documenta el contrato brownfield actual (refresh solo por cookie `HttpOnly`).
- La correspondencia exacta Material 3 → SwiftUI (tokens `--mat-sys-*`, densidad)
  es decisión del intent de diseño; aquí solo se documenta el tema Angular de
  origen. Donde Material 3 no tenga equivalente 1:1, se cubrirá con Apple HIG.
