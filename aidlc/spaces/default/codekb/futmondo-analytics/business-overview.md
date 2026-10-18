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

## Relevancia para F1 (login nativo iOS)

El objetivo de F1 es un cliente nativo iOS (Swift/SwiftUI) que **reutiliza el
backend FastAPI**. El contrato de auth existente es la pieza central: hoy el
refresh token viaja **solo** por cookie `HttpOnly` (pensado para navegador),
mientras que un cliente nativo sin almacén de cookies de navegador necesita un
**transporte alternativo del refresh token** (decisión D-01, ajuste **aditivo**
del backend) y guardarlo en **iOS Keychain**, nunca en claro. El flujo de
negocio (login → access en memoria + refresh de larga duración → refresh →
logout) se mantiene; F1 solo cambia el canal de transporte del refresh token
para el cliente nativo.

## Sources

- `README.md`
- `backend/app/main.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/session_store.py`
- `backend/app/core/config.py`
- `backend/app/api/v1/endpoints/user.py`
- Listado de `backend/app/api/v1/endpoints/` y `angular-app/src/app/features/`

## Assumptions & Open Questions

- El detalle exacto del transporte alternativo del refresh token para iOS (D-01)
  y el formato del almacén en Keychain son decisiones de diseño de F1; aquí solo
  se documenta el contrato brownfield actual (refresh solo por cookie `HttpOnly`).
