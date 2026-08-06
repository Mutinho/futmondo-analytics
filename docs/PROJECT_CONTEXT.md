# Contexto del Proyecto — Futmondo Analytics

## Estado Actual (6 agosto 2026)

### Resumen
Aplicación multi-usuario de gestión de ligas Futmondo (fantasy football). Frontend Angular 22 (PWA) + backend FastAPI. Autenticación JWT con HttpOnly cookies. Base de datos Neon PostgreSQL. Deploy en Fly.io.

### Repo
- **GitHub**: https://github.com/Mutinho/futmondo-analytics
- **Branch**: main
- **Deploy**: Fly.io (futmondo-app.fly.dev / futmondo-api.fly.dev)

---

## Arquitectura Técnica

### Frontend (angular-app/)
- **Angular 22.1.0** con standalone components y signals
- **Angular Material 22** — tema custom verde + dark mode
- **ng2-charts** (Chart.js) para gráficos
- **PWA** — service worker, manifest, instalable en iPhone
- **Auth** — access token en memoria, refresh via HttpOnly cookie
- **Build**: multi-stage Docker (Node 24 → nginx)

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
- **Fly.io** — 2 máquinas (frontend + backend), región París (cdg)
- **GitHub Actions** — deploy automático en push a main
- **HTTPS** automático via Fly.io

---

## Autenticación

### Flujo
1. Usuario entra → splash screen → intenta refresh via cookie
2. Si cookie válida → recupera sesión → navega a /budget
3. Si no → navega a /login → login con credenciales Futmondo
4. Backend valida contra API Futmondo → genera JWT + HttpOnly cookie
5. Access token (1h) en memoria, refresh token (30d) en cookie
6. Interceptor auto-refresh transparente al expirar

### Seguridad
- Refresh token: HttpOnly, Secure (en prod), SameSite=Lax, path=/auth
- Access token: nunca en localStorage, solo en memoria JS
- Sesión Futmondo: por usuario, 12h TTL, re-auth automática
- Middleware protege todos los /api/v1/* endpoints
- 403 = sesión Futmondo expirada → force re-login

---

## Tablas de la Base de Datos

| Tabla | Descripción |
|-------|-------------|
| `app_users` | Usuarios de la app (id, email, futmondo_user_id, display_name) |
| `refresh_tokens` | Tokens de refresh (hash, user_id, expires, revoked) |
| `user_championships` | Campeonatos por usuario + config completa (premios, cláusulas) |
| `players` | Jugadores (player_id, name, role, real_team) |
| `teams` | Equipos de los campeonatos |
| `users` | Managers de Futmondo (no de la app) |
| `transactions` | Historial de compras/ventas |
| `championships` | Referencia mínima para FKs |
| `team_standings` | Clasificación por jornada |
| `player_performance` | Rendimiento por jornada |
| `dream_teams_mvps` | Dream team y MVPs |
| `punishments_bonuses` | Castigos y bonificaciones |
| `clauses` | Cláusulas ejecutadas |
| `sync_metadata` | Metadatos de sincronización (compartido) |
| `sofascore_cache` | Caché de ratings/stats de Sofascore |
| `team_rosters` | Plantillas de equipos |
| `player_championship_stats` | Stats de cláusulas y medias |
| `match_odds` | Cuotas de partidos |
| `matchday_articles` | Artículos generados por jornada |

---

## Configuración de campeonatos (user_championships)

Campos por campeonato:
- `initial_budget` — presupuesto inicial
- `has_clauses` — si tiene cláusulas activas
- `excluded_teams` — equipos excluidos del análisis
- `money_per_point` — € por punto por jornada
- `money_per_ranking` — € pool por clasificación por jornada
- `dream_team_bonus` — € por jugador en dream team
- `mvp_bonus` — € por MVP
- `ranking_mode` — "flop" (últimos cobran menos) o "top" (primeros cobran más)
- `users_to_rank` — cuántos usuarios se rankean (-1 = todos)

Se auto-detectan desde la API de Futmondo al primer login. Resincronizables manualmente.

---

## Fórmula de Finanzas

```
total_money = presupuesto_inicial
            + (puntos_totales × money_per_point)
            + (ventas - compras)
            + (dream_team_count × dream_team_bonus)
            + (mvp_count × mvp_bonus)
            + ranking_money_acumulado
            + net_castigos_bonificaciones
```

### Ranking money (fórmula de Futmondo)
```python
total_pct = sum(1..N)  # N = usuarios a rankear
ratio[posición] = (N - posición + 1) / total_pct
premio = money_per_ranking × ratio
```
Se calcula por cada jornada jugada y se acumula.

---

## Sincronización

### Flujo async
1. Frontend: POST /sync/trigger → recibe task_id (202)
2. Backend: lanza thread con 11 pasos
3. Frontend: polling GET /sync/task/{id} cada 2s
4. UI: progreso step-by-step con checkmarks

### Pasos del sync
1. Jugadores (batch insert 507 en 300ms)
2. Transacciones (batch users+teams+players+transactions)
3. Cláusulas
4. Castigos/bonificaciones
5. Dream teams/MVPs
6. Rendimiento por jornada (batch por matchday)
7. Plantillas
8. Clasificación
9. Cuotas de partidos
10. Verificar fantasmas
11. Ratings Sofascore (rate-limited 750ms/request)

### Performance
- Full sync: ~7-8s (antes: 70s)
- Batch inserts con `execute_values` (PostgreSQL)
- Cuello de botella: API de Futmondo, no la DB

---

## APIs externas

### Futmondo
- Login: POST `/5/login/with_mail`
- Campeonatos activos: POST `/2/user/activechampionships`
- Config campeonato: POST `/2/championship/teams`
- Mercado: POST `/1/market/players`
- Sala de prensa: POST `/1/classic/championship/pressroom`
- Standings: POST `/1/classic/championship/matchday/standings`

### Sofascore (no oficial)
- Base: `https://api.sofascore.com/api/v1`
- Requiere `curl_cffi` (impersonate Chrome)
- Rate limit: 750ms entre requests
- Búsqueda: GET `/search/players?q={name}`
- Stats: GET `/player/{id}/statistics/seasons`

---

## Notas técnicas

1. **Connection pool**: 5-20 conexiones, valida antes de usar (Neon cierra idle tras ~5min), recrea pool si todas muertas.
2. **Session store**: In-memory, keyed por user_id, 12h TTL. Lock por usuario para evitar race conditions en re-auth.
3. **Task manager**: In-memory, auto-expira tasks >10min, máximo 20 en memoria.
4. **Sync metadata**: Compartido entre usuarios (quien sincroniza, beneficia a todos).
5. **PWA**: Service worker con strategy freshness para API, prefetch para app shell.
6. **Cookie auth**: COOKIE_SECURE=false en local (HTTP), true en producción (HTTPS).
