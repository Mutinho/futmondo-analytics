# Contexto del Proyecto — Futmondo Analytics

## Estado Actual (28 agosto 2026) — v2.1.0

### Resumen
Aplicación multi-usuario de gestión de ligas Futmondo (fantasy football). Frontend Angular 22 (PWA) + backend FastAPI. Autenticación JWT con HttpOnly cookies. Base de datos Neon PostgreSQL. Deploy en Fly.io. Incluye asistente IA conversacional (Groq/Gemini).

### Repo
- **GitHub**: https://github.com/Mutinho/futmondo-analytics
- **Branch**: main
- **Deploy**: Fly.io (futmondo-app.fly.dev / futmondo-api.fly.dev)
- **Versión actual**: v2.1.0

---

## Arquitectura Técnica

### Frontend (angular-app/)
- **Angular 22.1.0** con standalone components, signals, OnPush
- **Angular Material 22** — tema custom verde + dark mode
- **ng2-charts** (Chart.js) para gráficos
- **marked** (18.0.11) para renderizado markdown en chat del asistente
- **PWA** — service worker, manifest, instalable en iPhone/Android
- **Auth** — access token en memoria, refresh via HttpOnly cookie, interceptor con queuing
- **Build**: multi-stage Docker (Node 24 → nginx)
- **Routing**: lazy loading + PreloadAllModules + provideAnimationsAsync
- **Detección responsive**: `injectIsMobile()` shared (BreakpointObserver)

### Backend (backend/)
- **FastAPI** (Python 3.12)
- **Neon PostgreSQL** (serverless, eu-central-1 Frankfurt)
- **PyJWT** para autenticación
- **curl_cffi** para Sofascore (bypass TLS fingerprinting)
- **psycopg2** con ThreadedConnectionPool (5-20 conexiones, thread-safe)
- **google-genai** + **groq** para asistente IA
- **Puerto**: 8000

### Base de datos
- **Neon PostgreSQL** (free tier: 0.5GB)
- Latencia: ~95ms desde Docker local, ~30ms desde Fly.io (París→Frankfurt)
- ThreadedConnectionPool con validación automática (handles idle timeout de Neon)
- db_type normalizado a "postgresql" siempre

### Deploy
- **Fly.io** — 3 máquinas (frontend + backend + cron), región París (cdg)
- **GitHub Actions** — deploy automático en push a main
- **Cron diario** — GitHub Actions schedule a las 6:30 CET (sync datos) + 7:00 CET (Sofascore local)
- **HTTPS** automático via Fly.io
- **Secrets en Fly**: DATABASE_URL, JWT_SECRET, FUTMONDO_EMAIL, FUTMONDO_PASSWORD, GEMINI_API_KEY, GROQ_API_KEY
- **Deploy manual**: `cd backend && ~/.fly/bin/flyctl deploy && cd ../angular-app && ~/.fly/bin/flyctl deploy`

### Seguridad (v2.0)
- **CORS**: whitelist de orígenes (futmondo-app.fly.dev, futmondo.localhost, localhost:4200) + EXTRA_CORS_ORIGIN env var
- **JWT_SECRET**: RuntimeError si no está seteado en producción (detecta FLY_APP_NAME)
- **SSL**: verificación activa (no se deshabilita globalmente)
- **Auth interceptor**: encola requests durante refresh con BehaviorSubject
- **Auth guard**: espera tryRecoverSession() antes de verificar (fix F5 deep link)

---

## Arquitectura Frontend Detallada

### Estructura de archivos
```
angular-app/src/app/
├── app.ts / app.html / app.scss       # Shell: sidebar + router-outlet + assistant FAB
├── app.config.ts                       # Providers (router, animations, http)
├── app.routes.ts                       # Rutas lazy-loaded + authGuard + wildcard 404
├── version.ts                          # APP_VERSION constant
│
├── core/                               # Singleton services, interceptors, guards
│   ├── services/
│   │   ├── auth.service.ts             # Login, refresh, logout, initialized signal
│   │   ├── championship.service.ts     # Active championship signal + load
│   │   ├── analytics.service.ts        # 12 métodos tipados (18 interfaces exportadas)
│   │   ├── assistant.service.ts        # Chat IA (ask + conversations + usage)
│   │   ├── budget.service.ts           # Balances
│   │   ├── evolution.service.ts        # Evolution charts (cache con TTL 5min)
│   │   ├── favorites.service.ts        # Get/unfollow favorites
│   │   ├── roster.service.ts           # My roster, sell, cancel-sale, on-sale
│   │   ├── stats.service.ts            # User stats (cache con TTL 5min)
│   │   └── sync.service.ts             # Trigger sync + polling
│   ├── guards/
│   │   └── auth.guard.ts              # Async guard con tryRecoverSession()
│   └── interceptors/
│       └── auth.interceptor.ts        # Bearer token + refresh queue (BehaviorSubject)
│
├── shared/                             # Componentes y utils reutilizables
│   ├── components/
│   │   ├── loading-state/             # Loading/error/empty wrapper (content projection)
│   │   ├── view-toggle/              # Cards/table toggle + sort dropdown
│   │   ├── player-card/              # Tarjeta genérica de jugador con slots
│   │   ├── position-chip/            # Badge de posición (DL/MC/DF/PT) coloreado
│   │   ├── info-banner/              # Banner key-value stats
│   │   ├── page-header.component.ts  # Icono + título + descripción de página
│   │   ├── scroll-top.component.ts   # FAB scroll to top
│   │   ├── sofascore-badge.component.ts      # Píldora rating (tabla)
│   │   ├── sofascore-card-badge.component.ts # Badge rating (tarjeta)
│   │   ├── starter-badge.component.ts        # Píldora titularidad (tabla)
│   │   ├── starter-card-badge.component.ts   # Badge titularidad (tarjeta)
│   │   ├── info-card.component.ts            # Tarjeta genérica
│   │   ├── assistant-fab.component.ts        # FAB flotante (@defer on idle)
│   │   └── assistant-chat.component.ts/.html/.scss  # Panel chat IA
│   ├── utils/
│   │   ├── player.utils.ts           # getPlayerPhoto, getTeamLogo, getPositionKey/Label, onImgError
│   │   ├── responsive.ts             # injectIsMobile() — shared signal
│   │   ├── spanish-date-adapter.ts   # NativeDateAdapter español + ES_DATE_FORMATS
│   │   └── team-logos.ts             # TEAM_LOGO_MAP + getTeamLogoById()
│   ├── styles/
│   │   ├── _loading-states.scss      # .loading, .error-message, .empty
│   │   ├── _table-common.scss        # .table-container, .player-photo, .pos-chip, .trend-*
│   │   ├── _player-card.scss         # .player-card, .card-header, .card-avatar, etc.
│   │   ├── _responsive-grid.scss     # .cards-container breakpoints
│   │   └── _index.scss               # Barrel @forward
│   └── pipes/
│       └── money.pipe.ts             # Formato €
│
├── features/                           # Páginas (lazy-loaded, OnPush)
│   ├── splash/                        # Splash → tryRecoverSession → redirect
│   ├── login/                         # Login con credenciales Futmondo
│   ├── budget/                        # Presupuestos (overview + detail + sync-dialog + prizes-dialog)
│   ├── market/                        # Mercado (bid-dialog, sofascore-detail-dialog, confirm-dialog)
│   ├── favorites/                     # Jugadores favoritos
│   ├── my-roster/                     # Mi plantilla
│   ├── calculator/                    # Calculadora de ventas
│   ├── transactions/                  # Historial compras/ventas
│   ├── evolution/                     # Gráficos de evolución
│   ├── classification/                # Clasificación dinámica
│   ├── clausulable/                   # Jugadores clausulables
│   ├── stats/                         # Estadísticas
│   ├── finances/                      # Finanzas
│   ├── analytics/                     # Sub-rutas: overview, classification, players, users, market, opportunities, projections
│   └── settings/                      # Configuración de campeonatos
```

### Patrones del frontend
- **Todos los componentes**: `standalone: true` + `ChangeDetectionStrategy.OnPush`
- **Signal inputs**: `input()` / `input.required()` en shared components
- **Templates externos**: `.html` + `.scss` separados (12 componentes migrados)
- **State management**: Angular signals (0 BehaviorSubjects en componentes)
- **Lazy loading**: Todas las rutas con `loadComponent` / `loadChildren`
- **Shared components**: LoadingState, ViewToggle, PositionChip reemplazan código duplicado en market, favorites, my-roster
- **Caching**: signal-based con TTL 5min en evolution/stats services
- **isMobile**: `injectIsMobile()` en shared/utils (inyectable, no duplicado)
- **PWA**: NGSW cachea Google Fonts + imágenes estáticas de Futmondo CDN

---

## Arquitectura Backend Detallada

### Estructura de archivos
```
backend/app/
├── main.py                            # FastAPI app, CORS, routers, middleware
├── core/
│   ├── config.py                      # Env vars (DATABASE_URL, JWT_SECRET, GEMINI/GROQ keys)
│   └── constants.py                   # LALIGA_TEAMS map + LALIGA_TEAM_NAMES (shared)
├── auth/
│   ├── routes.py                      # /auth/login, /auth/refresh, /auth/logout + auto-detect championships
│   ├── jwt_utils.py                   # create/verify access token
│   ├── token_store.py                 # Refresh tokens table + migrations
│   ├── session_store.py               # Futmondo sessions por usuario (12h TTL)
│   ├── dependencies.py                # get_current_user dependency
│   └── models.py                      # Pydantic models
├── api/v1/endpoints/
│   ├── _helpers.py                    # get_user_futmondo_client, get_championship_config, clean_float
│   ├── _sofascore_helpers.py          # calculate_starter_pct, get_current_matchday, lookup_sofascore
│   ├── analytics.py                   # /championship/trends, /classification-full, watchlist, etc.
│   ├── assistant.py                   # /ask, /conversations CRUD, /usage
│   ├── balances.py                    # /balances (presupuestos por equipo)
│   ├── championships.py              # /championships (CRUD)
│   ├── clausulable_players.py        # /clausulable-players
│   ├── favorites.py                   # /favorites/my, /mark, /unfollow
│   ├── market.py                      # /market/today, /market/bid (cache market_today)
│   ├── matchdays.py                   # /matchdays/evolution
│   ├── phantoms.py                    # Verificar fantasmas
│   ├── player_finances.py            # /player-finances
│   ├── roster.py                      # /roster/my, /sell, /cancel-sale, /on-sale
│   ├── sofascore_detail.py           # /sofascore/player/:id
│   ├── sofascore_sync.py             # /sync/sofascore
│   ├── statistics.py                  # /user-stats
│   ├── sync.py                        # /sync/trigger + background thread (10 pasos)
│   ├── transactions.py               # /transactions/history
│   ├── user.py                        # /user/me, /user/championships
│   └── user_stats.py                  # /user-stats
├── services/
│   ├── assistant_service.py           # IA: context builder, guardrails, factual answers, LLM (Groq→Gemini)
│   ├── analytics_service.py           # Lógica analytics (usa LALIGA_TEAM_NAMES desde constants)
│   ├── data_manager_v2.py            # Queries complejas a BD
│   ├── data_sync_service.py          # Sync completo (10 pasos)
│   ├── db_connection.py              # ThreadedConnectionPool + adapt_params + reconnect
│   ├── futmondo_client.py            # HTTP client para API Futmondo
│   ├── futmondo_service.py           # Legacy (solo usado por initialize.py)
│   ├── photo_service.py              # Descarga y cachea fotos de jugadores
│   ├── sofascore_client.py           # HTTP client para Sofascore (curl_cffi)
│   └── task_manager.py               # Background task tracking
```

### Patrones del backend
- **Helpers compartidos**: `_helpers.py` (get_championship_config, clean_float, get_user_futmondo_client)
- **Constantes centralizadas**: `core/constants.py` (LALIGA_TEAMS en un solo lugar, antes duplicado en 6 archivos)
- **Seguridad**: CORS whitelist, JWT prod-only check, ThreadedConnectionPool
- **Asistente IA**: guardrails → factual DB → LLM (ahorra tokens en 3 capas)
- **Provider fallback**: Groq (gpt-oss-120b, rápido) → Gemini (gemini-3.6-flash → gemini-3.5-flash)
- **Market cache**: tabla `market_today` evita llamadas live a API Futmondo
- **Usage tracking**: tabla `assistant_usage` con límites mensuales/diarios
- **Premios (team_prizes)**: ranking + mvp + points + dream_team, calculados localmente con fórmula de Futmondo
  - Ranking: fórmula inversa `pos / (N*(N+1)/2) * pool` (modo flop) — excluye equipos con 0 puntos (N dinámico)
  - Dream team: 1M€ por jugador en equipo ideal de la jornada (cruce lineup vs dreamTeam API)
  - Balances, assistant y market suman `ranking_prize + mvp_prize + points_prize + dream_team_prize`

---

## Asistente IA

### Arquitectura
```
Frontend (FAB → chat panel) → POST /api/v1/assistant/ask → Backend
                                                              │
                                                              ├─ 1. Guardrails (off-topic? → rechaza sin tokens)
                                                              ├─ 2. Factual answer (saldo, plantilla, clasificación → responde de BD)
                                                              └─ 3. LLM call (Groq → Gemini fallback)
                                                                    ├─ Context builder (roster, budget, market, matches, etc.)
                                                                    └─ System prompt con identidad usuario + reglas
```

### Optimizaciones de tokens
- Formato compacto CSV en contexto (no tablas con `|`)
- Follow-ups solo inyectan presupuesto (si no cambian de tema)
- Historial limitado a 4 mensajes
- max_output_tokens: 2048 (Groq y Gemini)
- Chips de sugerencia cortos ("¿Qué vendo?" no párrafos largos)
- System prompt prohíbe tablas markdown (usa listas)
- Sin llamada live a API Futmondo (solo BD)

### Conversaciones
- Persistidas en tabla `assistant_conversations` (user_id, messages JSON, title)
- Frontend: sidebar overlay con backdrop oscuro
- Auto-selecciona última conversación al abrir

### Control de uso
- Monthly limit: 25M tokens
- Daily limit: 50 requests
- Tabla `assistant_usage` con upsert mensual/diario

---

## Páginas de la Aplicación

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/` | Splash | Recovery de sesión → redirect |
| `/login` | Login | Credenciales Futmondo |
| `/budget` | Presupuesto | Vista general de equipos con balance, valor, premios (modal con desglose: ranking, puntos, MVP, equipo ideal) |
| `/my-roster` | Mi Plantilla | Jugadores con valor, plusvalía, ventas recomendadas |
| `/market` | Mercado | Jugadores del computer, puja sugerida, favoritos dorados |
| `/favorites` | Favoritos | Jugadores libres marcados como favoritos |
| `/transactions` | Transacciones | Historial compras/ventas por fecha |
| `/evolution` | Evolución | Gráficos de progresión |
| `/classification` | Clasificación | Clasificación dinámica con filtros |
| `/clausulable` | Clausulables | Jugadores susceptibles de cláusula |
| `/calculator` | Calculadora | Simular ventas con proyección por tendencia |
| `/stats` | Estadísticas | Datos por jugador y equipo |
| `/finances` | Finanzas | Desglose económico |
| `/free-agents` | Agentes Libres | Vista completa del watchlist |
| `/settings` | Ajustes | Configuración de campeonatos |
| `**` | 404 | Redirige a /budget |

### Vistas responsive
- **Tabla** (desktop) y **Tarjetas** (móvil) en: Presupuesto, Mi Plantilla, Mercado, Favoritos, Clausulables, Calculator
- Toggle via `ViewToggleComponent` shared
- Grid responsive: 1→2→3→4 columnas
- `injectIsMobile()` para lógica condicional
- F5 preserva la ruta actual (auth guard + tryRecoverSession)

---

## Autenticación

### Flujo
1. Usuario navega a cualquier ruta protegida → auth guard se activa
2. Guard: si no `initialized()` → llama `tryRecoverSession()` (refresh via cookie)
3. Si cookie válida → token en memoria → guard deja pasar
4. Si no → redirige a `/login`
5. Login: credenciales Futmondo → backend valida → JWT + HttpOnly cookie
6. Interceptor: Bearer token automático, refresh queue con BehaviorSubject

### Seguridad
- Refresh token: HttpOnly, Secure (prod), SameSite=Lax, path=/auth
- Access token: 1h, solo en memoria JS (nunca localStorage)
- CORS: whitelist estricta (no wildcard)
- Rate limiting pendiente en /auth/login

---

## Tablas de la Base de Datos

| Tabla | Descripción |
|-------|-------------|
| `app_users` | Usuarios de la app (id, email, futmondo_user_id, display_name) |
| `refresh_tokens` | Tokens de refresh (hash, user_id, expires, revoked) |
| `user_championships` | Campeonatos por usuario + config + is_pro + futmondo_team_id |
| `players` | Jugadores (player_id, name, role, role2, real_team_id, slug, photo_url, value) |
| `teams` | Equipos de los campeonatos |
| `users` | Managers de Futmondo |
| `transactions` | Historial compras/ventas (+ market_value_at_purchase, bids_json) |
| `team_standings` | Clasificación por jornada |
| `player_performance` | Rendimiento por jornada |
| `player_championship_stats` | Stats de cláusulas, medias, owner_team |
| `dream_teams_mvps` | Dream team y MVPs |
| `punishments_bonuses` | Castigos y bonificaciones |
| `clauses` | Cláusulas ejecutadas |
| `team_prizes` | Premios por jornada (ranking + mvp + points + dream_team) |
| `team_rosters` | Plantillas de equipos |
| `match_odds` | Cuotas de partidos |
| `player_favorites` | Jugadores favoritos por usuario/campeonato |
| `sofascore_cache` | Caché global Sofascore (una entrada por jugador) |
| `sync_metadata` | Metadatos de sincronización |
| `market_today` | Cache del mercado del día (usado por assistant + market page) |
| `assistant_conversations` | Conversaciones del chat IA |
| `assistant_usage` | Tracking de tokens/requests del asistente |

---

## Sincronización

### Flujo
1. Frontend: POST /sync/trigger → task_id
2. Backend: thread daemon con 10 pasos
3. Frontend: polling cada 2s
4. Al completar: actualiza sync_metadata

### Pasos del sync "all"
1. Jugadores (batch ~520, incluye role2 y favoritos)
2. Transacciones (incremental pressroom + enrichment market_value + bids)
3. Cláusulas
4. Castigos/bonificaciones
5. Dream teams/MVPs
6. Rendimiento por jornada
7. Plantillas
8. Clasificación
9. Cuotas de partidos
10. Verificar fantasmas

### Sync automático (Cron)
- GitHub Actions: `daily-sync.yml` cron `'30 4 * * *'` (6:30 CET)
- Máquina `futmondo-cron` en Fly.io (256MB, se para sola al terminar)
- Multi-campeonato: itera sobre todos los campeonatos del usuario

### Sync Sofascore — Local (IP residencial)
- Script: `backend/scripts/sync_sofascore_local.py`
- Self-hosted runner en WSL (`futmondo-local`)
- Schedule: `'0 5 * * *'` (7:00 CET)
- ~306 jugadores, ~25-30 min, rate limit conservador

---

## Desarrollo Local (Docker)

### Comandos
- **Build + deploy local**: `echo "javi" | sudo -S docker compose up -d --build`
- **Solo frontend**: `echo "javi" | sudo -S docker compose up -d --build frontend`
- **Solo backend**: `echo "javi" | sudo -S docker compose up -d --build backend`
- **Ver logs**: `echo "javi" | sudo -S docker compose logs -f backend`
- **Parar todo**: `echo "javi" | sudo -S docker compose down`

### URLs locales
- Frontend: `futmondo.localhost`
- Backend: `futmondo-api.localhost`
- Proxy nginx rutea por `server_name`

### Notas
- Docker requiere `sudo` (password: `javi`)
- La BD Neon es compartida entre local y producción
- `proxy.conf.json` proxea `/api` y `/auth` a localhost:8000 (para dev sin Docker)
- Nginx del proxy tiene `proxy_buffering off` para SSE

### Versionado
- Versión en `angular-app/src/app/version.ts` + `package.json`
- Tags git: `git tag -a vX.Y.Z -m "msg" && git push origin vX.Y.Z`
- Releases GitHub: `gh release create vX.Y.Z --title "..." --notes "..."`
- **Siempre**: tag + release juntos

---

## PWA

### Configuración
- `site.webmanifest`: name="Futmondo Analytics", short_name="Futmondo Analytics"
- `apple-mobile-web-app-title`: "Futmondo Analytics"
- `background_color`: #2e7d32 (verde)
- Iconos: set completo Android (mipmap) + iOS (AppIcon.appiconset) en `public/icon/`
- `apple-touch-icon.png`: 180x180 RGB (sin transparencia)
- `android-chrome-*.png`: 192x192 + 512x512 RGB
- Favicon: `.ico` + PNG 16/32

### NGSW Cache
- Google Fonts: strategy performance, 365d TTL
- Futmondo static CDN (fotos/logos): strategy performance, 7d TTL, max 500

---

## APIs Externas

### Futmondo
- Login: POST `/5/login/with_mail`
- Campeonatos activos: POST `/2/user/activechampionships`
- Config campeonato: POST `/2/championship/teams`
- Jugadores: POST `/5/league/championshipplayers`
- Mercado: POST `/1/market/players`
- Sala de prensa: POST `/1/locker/pressroom`
- Roster: POST `/1/userteam/roster`
- Perfil jugador: POST `/1/player/fullprofile`
- Standings: POST `/1/classic/championship/matchday/standings`
- Vender: POST `/1/market/putonmarket`
- Cancelar venta: POST `/1/market/cancelsell`
- Ranking ronda: POST `/1/ranking/round`
- Dream team: POST `/1/userteam/dreamteam`

### Sofascore (no oficial)
- Base: `https://api.sofascore.com/api/v1`
- Requiere `curl_cffi` (impersonate Chrome)
- Búsqueda: GET `/search/players?q={name}`
- Stats: GET `/player/{id}/unique-tournament/{ut}/season/{s}/statistics/overall`
- LaLiga ID: 8, Season 26/27: 97268, 25/26: 77559

### LLM Providers
- **Groq** (primario): model `openai/gpt-oss-120b`, max_tokens 2048
- **Gemini** (fallback): models `gemini-3.6-flash` → `gemini-3.5-flash`, max_output_tokens 2048
- Free tier Gemini: 15 RPM, 1M tokens/día
- API keys en Fly secrets + .env local

---

## URLs de Imágenes
- Jugadores: `https://static01.mondocore.com/futmondo/img/faces/64/{slug}.png`
- Equipos: `https://static02.mondocore.com/futmondo/img/teams/64/{logo}`
- Default player avatar: SVG data URI inline (silueta close-up)
