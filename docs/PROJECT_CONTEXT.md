# Contexto del Proyecto — Futmondo Analytics

## Estado Actual (23 agosto 2026) — v1.4.4

### Resumen
Aplicación multi-usuario de gestión de ligas Futmondo (fantasy football). Frontend Angular 22 (PWA) + backend FastAPI. Autenticación JWT con HttpOnly cookies. Base de datos Neon PostgreSQL. Deploy en Fly.io.

### Repo
- **GitHub**: https://github.com/Mutinho/futmondo-analytics
- **Branch**: main
- **Deploy**: Fly.io (futmondo-app.fly.dev / futmondo-api.fly.dev)
- **Versión actual**: v1.4.4

---

## Arquitectura Técnica

### Frontend (angular-app/)
- **Angular 22.1.0** con standalone components y signals
- **Angular Material 22** — tema custom verde + dark mode
- **ng2-charts** (Chart.js) para gráficos
- **PWA** — service worker, manifest, instalable en iPhone
- **Auth** — access token en memoria, refresh via HttpOnly cookie
- **Build**: multi-stage Docker (Node 24 → nginx)
- **Componentes compartidos** (`shared/components/`): ScrollTopComponent, SofascoreBadgeComponent, SofascoreCardBadgeComponent, StarterBadgeComponent, StarterCardBadgeComponent

### Backend (backend/)
- **FastAPI** (Python 3.12)
- **Neon PostgreSQL** (serverless, eu-central-1 Frankfurt)
- **PyJWT** para autenticación
- **curl_cffi** para Sofascore (bypass TLS fingerprinting)
- **psycopg2** con connection pool (5-20 conexiones, reconnect automático)
- **Puerto**: 8000

### Base de datos
- **Neon PostgreSQL** (free tier: 0.5GB)
- Latencia: ~95ms desde Docker local, ~30ms desde Fly.io (París→Frankfurt)
- Connection pool con validación automática (handles idle timeout de Neon)

### Deploy
- **Fly.io** — 3 máquinas (frontend + backend + cron), región París (cdg)
- **GitHub Actions** — deploy automático en push a main (a veces falla, usar `flyctl deploy` directamente)
- **Cron diario** — GitHub Actions schedule a las 6:30 CET → `flyctl deploy` de `futmondo-cron` (sync completo + Sofascore)
- **HTTPS** automático via Fly.io
- **Deploy manual**: `cd backend && ~/.fly/bin/flyctl deploy && cd ../angular-app && ~/.fly/bin/flyctl deploy`

---

## Páginas de la Aplicación

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/budget` | Presupuesto | Vista general de equipos con balance, valor plantilla, rendimiento. Vista tabla y tarjetas |
| `/my-roster` | Mi Plantilla | Jugadores del usuario con valor, plusvalía, puntos, media, ventas recomendadas |
| `/market` | Mercado | Jugadores del computer para pujar, puja sugerida basada en % real de sobrepago. Favoritos destacados con borde/fondo dorado |
| `/favorites` | Favoritos | Jugadores libres marcados como favoritos, con botón de unfollow |
| `/transactions` | Transacciones | Historial compras/ventas por fecha, con pujas competidoras y plusvalías |
| `/evolution` | Evolución | Gráficos de progresión |
| `/stats` | Estadísticas | Datos por jugador y equipo |
| `/finances` | Finanzas | Desglose económico detallado |
| `/clausulable` | Clausulables | Jugadores susceptibles de cláusula |
| `/analytics` | Analytics | Dashboard avanzado |
| `/settings` | Ajustes | Configuración de campeonatos |

### Vistas responsive
- **Tabla** (desktop por defecto) y **Tarjetas** (móvil por defecto) en: Presupuesto, Mi Plantilla, Mercado, Favoritos
- Toggle de vista guardado en localStorage por página
- Selector de ordenación en vista tarjetas (mat-form-field + mat-select de Angular Material)
- Grid responsive: 1→2→3→4 columnas según pantalla
- F5 preserva la ruta actual (localStorage `futmondo_last_route`)

---

## Autenticación

### Flujo
1. Usuario entra → splash screen → intenta refresh via cookie
2. Si cookie válida → recupera sesión → navega a última ruta visitada
3. Si no → navega a /login → login con credenciales Futmondo
4. Backend valida contra API Futmondo → genera JWT + HttpOnly cookie
5. Access token (1h) en memoria, refresh token (30d) en cookie
6. Interceptor auto-refresh transparente al expirar
7. Login resetea `_initialized` para que el effect re-dispare la carga de datos

### Seguridad
- Refresh token: HttpOnly, Secure (en prod), SameSite=Lax, path=/auth
- Access token: nunca en localStorage, solo en memoria JS
- Sesión Futmondo: por usuario, 12h TTL, re-auth automática
- Middleware protege todos los /api/v1/* endpoints

---

## Tablas de la Base de Datos

| Tabla | Descripción |
|-------|-------------|
| `app_users` | Usuarios de la app (id, email, futmondo_user_id, display_name) |
| `refresh_tokens` | Tokens de refresh (hash, user_id, expires, revoked) |
| `user_championships` | Campeonatos por usuario + config completa (premios, cláusulas) |
| `players` | Jugadores (player_id, name, role, role2, real_team_id, slug, photo_url) |
| `teams` | Equipos de los campeonatos |
| `users` | Managers de Futmondo (no de la app) |
| `transactions` | Historial compras/ventas (+ market_value_at_purchase, bids_json) |
| `championships` | Referencia mínima para FKs |
| `team_standings` | Clasificación por jornada |
| `player_performance` | Rendimiento por jornada |
| `dream_teams_mvps` | Dream team y MVPs |
| `punishments_bonuses` | Castigos y bonificaciones |
| `clauses` | Cláusulas ejecutadas |
| `sync_metadata` | Metadatos de sincronización (compartido) |
| `sofascore_cache` | Caché global de Sofascore (sin championship_id, una entrada por jugador) |
| `team_rosters` | Plantillas de equipos |
| `player_championship_stats` | Stats de cláusulas y medias |
| `match_odds` | Cuotas de partidos |
| `player_favorites` | Jugadores favoritos por usuario/campeonato |

---

## Sofascore Cache

### Estructura
- **Global** — un registro por jugador, compartido entre todos los campeonatos
- **Sin championship_id** (eliminado en migración v1.4)
- Columnas clave: `player_name` (UNIQUE), `rating`, `matches_started`, `matches_started_prev`, `season`, `appearances`, `sofascore_url`

### Cálculo de % Titularidad
- Centralizado en `backend/app/api/v1/endpoints/_sofascore_helpers.py`
- **Cap**: resultado siempre ≤ 100% (para ligas con >38 jornadas como 2ª División)
- **Temporada anterior** (season contiene "25/26"): `matches_started / 38`
- **Temporada actual** (season contiene "26/27"):
  - Jornada 1-9: blend ponderado `(current/matchday)*peso + (prev/38)*(1-peso)` donde peso = matchday/10
  - Jornada 10+: `matches_started / current_matchday`
- `get_current_matchday()` lee MAX(matchday) de team_standings

### Prioridad de datos Sofascore (get_player_stats)
- **Prioridad 1**: LaLiga temporada actual (26/27)
- **Prioridad 2**: Cualquier liga temporada actual (26/27) — ej. Bundesliga, Premier
- **Prioridad 3**: LaLiga temporada anterior (25/26)
- **Prioridad 4**: Cualquier liga temporada anterior (25/26)
- Temporada siempre tiene prioridad sobre liga (un jugador con datos recientes de Bundesliga usa esos, no datos viejos de LaLiga)

### Sync de Sofascore
- Procesa TODOS los 507 jugadores del campeonato (no solo mercado/roster)
- Escritura por lotes de 50 con UPSERT (evita timeout de Neon)
- ON CONFLICT preserva `matches_started_prev` cuando cambia la temporada
- Rate limit: 750ms entre requests, 5s pausa cada 20 perfiles
- Duración: ~15-20 minutos para 507 jugadores

---

## Transacciones

### Enriquecimiento de valor de mercado
- Cada transacción se enriquece con `market_value_at_purchase` via `/1/player/fullprofile`
- **Compras**: usa valor del día anterior (resolución de subasta)
- **Ventas**: usa valor del mismo día (venta inmediata)
- Solo se procesan las que tienen `market_value_at_purchase IS NULL`
- Rate limit: 500ms entre requests, 5s pausa cada 20 perfiles

### Pujas competidoras
- Campo `bids_json` almacena las pujas de otros equipos
- Se guarda durante el sync de transacciones (`_store_bids`)
- Frontend muestra las pujas con nombre, monto y % de sobrepago

### Puja sugerida (mercado)
- Basada en % real de sobrepago histórico (`price / market_value_at_purchase`)
- Busca transacciones con `market_value_at_purchase` en rango ±25% del valor del jugador
- Fallback: método anterior por rango de precios pagados
- Confianza: high (≥10 txns), medium (≥3), low (<3)

---

## Sincronización

### Flujo
1. Frontend: modal sin toggle → POST /sync/trigger → task_id
2. Backend: thread daemon con 10 pasos (sin Sofascore)
3. Frontend: polling cada 2s
4. Al completar: actualiza `sync_metadata` tipo "all" con fecha actual

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

### Sync automático (Cron) — Datos
- **GitHub Actions** workflow `daily-sync.yml` con schedule `cron: '30 4 * * *'` (6:30 CET)
- Ejecuta `flyctl deploy --config cron/fly.toml --ha=false` + `flyctl machine start`
- Usa la 3ª máquina gratis de Fly.io (`futmondo-cron`, región cdg, 256MB)
- Reutiliza el Dockerfile del backend, overrides CMD via `[processes]` en fly.toml
- Ejecuta `scripts/sync_data.py` — **multi-campeonato**:
  - Obtiene championship IDs cruzando API Futmondo (`/2/user/activechampionships`) con BD (`user_championships`)
  - Itera sobre cada campeonato y ejecuta sync_all()
  - Si un campeonato falla, continúa con el siguiente
  - Exit 0 si al menos uno tiene éxito
- La máquina arranca, ejecuta el sync (~10-15s por campeonato) y se para sola al terminar
- Requiere `flyctl machine start` explícito después del deploy (sin http_service no auto-arranca)
- También se puede lanzar manualmente desde GitHub Actions (workflow_dispatch)

### Sync Sofascore — Local (IP residencial)
- **Sofascore bloquea IPs de datacenter** (Fly.io) con 403 "challenge"
- El sync de Sofascore se ejecuta desde la máquina local del usuario (IP residencial)
- **Script**: `backend/scripts/sync_sofascore_local.py`
  - Conecta directamente a Neon PostgreSQL (no necesita Futmondo login)
  - Lee jugadores de la BD (tabla `players` JOIN `player_championship_stats` JOIN `user_championships`)
  - ~544 jugadores activos (filtra huérfanos de temporadas anteriores)
  - Muestra cada jugador en tiempo real con rating coloreado
  - Rate limit conservador: 2s entre requests, 15s pausa cada 10 jugadores
  - Retry en 403: hasta 3 reintentos con backoff 60/120/180s
  - Escribe en batches de 50 con UPSERT
  - Duración estimada: ~25-30 min
- **Alias local**: `sofascore_sync` (en `~/.bash_aliases`)
- **GitHub Actions** workflow `sofascore-sync.yml`:
  - Corre en **self-hosted runner** (`futmondo-local`) instalado en WSL
  - Schedule: `cron: '0 5 * * *'` (7:00 CET, después del sync de datos)
  - También workflow_dispatch (lanzable desde móvil)
  - Runner instalado como servicio systemd (auto-start con WSL)
  - Ubicación: `/home/javi/actions-runner`
  - WSL config: `%UserProfile%\.wslconfig` con `vmIdleTimeout=-1` para evitar apagado

### Sofascore — Rate Limiting
- Ban temporal por IP tras ~340 requests seguidas a 0.75s
- Duración del ban: **~1 hora** (confirmado empíricamente)
- Con los nuevos parámetros conservadores no debería activarse el ban

### Anti-rate-limiting
- Headers idénticos a la PWA de Futmondo (Origin, Referer, User-Agent Chrome)
- 300-500ms entre requests a Futmondo API
- 750ms entre requests a Sofascore
- Pausas de 5s cada 20 perfiles

---

## APIs externas

### Futmondo
- Login: POST `/5/login/with_mail`
- Campeonatos activos: POST `/2/user/activechampionships`
- Config campeonato: POST `/2/championship/teams`
- Jugadores campeonato: POST `/5/league/championshipplayers`
- Mercado: POST `/1/market/players`
- Sala de prensa: POST `/1/locker/pressroom`
- Roster usuario: POST `/1/userteam/roster`
- Perfil jugador: POST `/1/player/fullprofile` (historial precios)
- Quitar favorito: POST `/5/championship/unmarkfavorite`
- Standings: POST `/1/classic/championship/matchday/standings`

### Sofascore (no oficial)
- Base: `https://api.sofascore.com/api/v1`
- Requiere `curl_cffi` (impersonate Chrome)
- Búsqueda: GET `/search/players?q={name}`
- Stats temporada: GET `/player/{id}/unique-tournament/{ut}/season/{s}/statistics/overall`
- Stats equipo: GET `/team/{id}/unique-tournament/8/season/{s}/statistics/overall` → campo `matches`
- Temporadas: GET `/unique-tournament/8/seasons`
- LaLiga uniqueTournament ID: 8
- Season IDs: 26/27=97268, 25/26=77559, 24/25=61643

---

## Componentes Compartidos (angular-app/src/app/shared/)

### Pipes
- `MoneyPipe` — formatea números como dinero (€)

### Components
- `ScrollTopComponent` — FAB fijo abajo-derecha, scroll to top (usa querySelector en mat-sidenav-content)
- `SofascoreBadgeComponent` — píldora compacta para tablas (colores oficiales Sofascore)
- `SofascoreCardBadgeComponent` — badge para tarjetas ("Sofa" + valor, fondo semi-transparente)
- `StarterBadgeComponent` — píldora compacta para tablas (escala rojo→verde)
- `StarterCardBadgeComponent` — badge para tarjetas ("Tit" + valor, escala rojo→verde)

---

## Desarrollo Local (Docker)

### Comandos
- **Build + deploy local**: `echo "javi" | sudo -S docker compose up -d --build`
- **Solo frontend**: `echo "javi" | sudo -S docker compose up -d --build frontend`
- **Solo backend**: `echo "javi" | sudo -S docker compose up -d --build backend`
- **Ver logs**: `echo "javi" | sudo -S docker compose logs -f backend`
- **Parar todo**: `echo "javi" | sudo -S docker compose down`

### Notas
- Docker requiere `sudo` — la contraseña del usuario es `javi`.
- Siempre usar `up -d --build` (no solo `build`) para que el contenedor se recree con la nueva imagen.
- URLs locales: `futmondo.localhost` (frontend) / `futmondo-api.localhost` (backend).
- El proxy nginx (compose service `proxy`) rutea por `server_name`.
- La BD Neon es compartida entre local y producción (mismos datos).
- Deploy producción manual: `cd backend && ~/.fly/bin/flyctl deploy && cd ../angular-app && ~/.fly/bin/flyctl deploy`
- Deploy cron manual: `cd backend && ~/.fly/bin/flyctl deploy --config ../cron/fly.toml --ha=false`

### Versionado
- Versión en `angular-app/src/app/version.ts` + `package.json`
- Tags git: `git tag -a vX.Y.Z -m "msg" && git push origin vX.Y.Z`
- Releases GitHub: `gh release create vX.Y.Z --title "..." --notes "..."`

---

## Mapa de equipos LaLiga (IDs Futmondo)

Usado como fallback estático cuando la API no devuelve nombre/logo del equipo real:

```
504e581e4d8bec9a670000c6 → Real Madrid
504e581e4d8bec9a670000c7 → Barcelona
504e581e4d8bec9a670000c8 → Atlético de Madrid
504e581e4d8bec9a670000c9 → Athletic de Bilbao
504e581e4d8bec9a670000ca → Rayo Vallecano
504e581e4d8bec9a670000cb → Valencia
504e581e4d8bec9a670000cc → Betis
504e581e4d8bec9a670000cd → Getafe
504e581e4d8bec9a670000ce → Real Sociedad
504e581e4d8bec9a670000cf → Levante
504e581e4d8bec9a670000d0 → Espanyol
504e581e4d8bec9a670000d1 → Osasuna
504e581e4d8bec9a670000d5 → Sevilla
504e581e4d8bec9a670000d6 → Málaga
504e581e4d8bec9a670000d8 → Deportivo de la Coruña
504e581e4d8bec9a670000d9 → Celta de Vigo
51b889b1e401a15f2c0000f0 → Elche
51b890f5b986415a2c000012 → Villarreal
52038563b8d07d930b00008a → Alavés
520e4ee4a776cc826b00004b → Racing
```

### URLs de imágenes Futmondo
- Jugadores: `https://static01.mondocore.com/futmondo/img/faces/64/{slug}.png`
- Equipos: `https://static02.mondocore.com/futmondo/img/teams/64/{logo}`
