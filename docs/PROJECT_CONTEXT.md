# Contexto del Proyecto — Futmondo Analytics

## Estado Actual (5 agosto 2026)

### Resumen
Aplicación de gestión de ligas Futmondo (fantasy football) con frontend Angular 22 + Material 22 y backend FastAPI. Integrada con la API de Futmondo (datos del juego) y Sofascore (ratings reales de jugadores).

### Repo
- **GitHub**: https://github.com/Mutinho/futmondo-analytics
- **Branch**: main
- **Tag de rollback visual**: `pre-design-system`

---

## Arquitectura Técnica

### Frontend (angular-app/)
- **Angular 22.1.0** con standalone components
- **Angular Material 22** — tema custom verde + dark mode
- **ng2-charts** (Chart.js) para gráficos
- **Node.js 24.15** requerido (usar `nvm use 24.15`)
- **Proxy**: `proxy.conf.json` → backend en localhost:8001
- **Build**: `NODE_TLS_REJECT_UNAUTHORIZED=0 npx ng build` (necesario por SSL de Google Fonts en WSL)

### Backend (backend/)
- **FastAPI** (Python 3.12)
- **SQLite** (fichero `backend/futmondo_data.db`)
- **curl_cffi** para llamadas a Sofascore (bypass TLS fingerprinting)
- **Venv**: `backend/venv/`
- **Puerto**: 8001

### Entorno
- WSL Ubuntu en Windows 11
- Usuario: javi
- Path: `/home/javi/futmondo`
- nvm instalado en `~/.nvm`

---

## Tablas de la Base de Datos (SQLite)

| Tabla | Descripción |
|-------|-------------|
| `players` | Jugadores (player_id, name, role, real_team) |
| `teams` | Equipos de los campeonatos |
| `users` | Usuarios/managers |
| `transactions` | Historial de compras/ventas |
| `championships` | Info básica de campeonatos |
| `championships_config` | Config propia (has_clauses, initial_budget, excluded_teams) |
| `team_standings` | Clasificación por jornada |
| `player_performance` | Rendimiento por jornada |
| `dream_teams_mvps` | Dream team y MVPs |
| `punishments_bonuses` | Castigos y bonificaciones |
| `clauses` | Cláusulas ejecutadas |
| `sync_metadata` | Metadatos de sincronización |
| `sofascore_cache` | Caché de ratings/stats de Sofascore |
| `team_rosters` | Plantillas de equipos |

---

## Campeonatos Configurados

| ID | Nombre | Cláusulas | Presupuesto | Equipos excluidos |
|----|--------|-----------|-------------|-------------------|
| `592416daa3a2dd871a7a9956` | Ivan el flautista de Futmondin | No | 200M | javier.ortega |
| `6a5f82a09c06c8d0ceaa40ee` | Infantino es español | Sí | 300M | — |

---

## Credenciales y APIs

### Futmondo
- Email: mutinho.bf@gmail.com
- Login endpoint: POST `https://api.futmondo.com/5/login/with_mail`
- Auto-login al arrancar el backend

### Sofascore (no oficial)
- Base: `https://api.sofascore.com/api/v1`
- Requiere `curl_cffi` (impersonate Chrome)
- Rate limit: 1 request/segundo
- Búsqueda: GET `/search/players?q={name}`
- Stats: GET `/player/{id}/statistics/seasons`
- Últimos partidos: GET `/player/{id}/events/last/0`
- Prioridad de stats: LaLiga actual > LaLiga anterior > otra liga actual > fallback últimos partidos (6 meses, mín 3 partidos)

---

## Estructura del Frontend Angular

```
angular-app/src/app/
├── app.ts / app.html / app.scss    # Shell (sidebar + toolbar + router)
├── app.routes.ts                    # Rutas lazy-loaded
├── app.config.ts                    # Providers (animations, http, charts)
├── core/
│   ├── models/                      # Interfaces TypeScript
│   └── services/                    # BudgetService, StatsService, ChampionshipService, etc.
├── shared/
│   ├── pipes/money.pipe.ts
│   └── components/info-card.component.ts
└── features/
    ├── budget/                      # Presupuesto (overview + detail + sync-dialog)
    ├── market/                      # Mercado (tabla + sofascore-detail-dialog + confirm-dialog)
    ├── evolution/                   # Gráficos Chart.js
    ├── stats/                       # Estadísticas + team-movements-dialog
    ├── finances/                    # Finanzas usuarios
    ├── clausulable/                 # Jugadores clausulables
    └── analytics/                   # Shell con sub-tabs
        ├── overview/
        ├── classification/
        ├── players/
        ├── market/
        ├── opportunities/
        └── projections/
```

---

## Funcionalidades Implementadas

### ✅ Completadas
- Selector de campeonato (persistido en localStorage)
- Presupuesto: tabla sortable, detalle altas/bajas, puja máxima
- Mercado: jugadores computer, puja sugerida, Sofascore rating, pujar/cancelar, tendencia
- Estadísticas: gráficos de barras, dialog de movimientos al click
- Evolución: gráficos Chart.js (empty state si no hay jornadas)
- Finanzas y Clausulables: empty state (esperando temporada)
- Analytics: 6 sub-tabs con descripciones (InfoCard component)
- Sync global: transacciones + phantoms + sofascore
- Dark mode con toggle y persistencia
- Sofascore: búsqueda por nombre (con team_hint), rating, stats, enlace al perfil
- Design system aplicado (Stitch)
- Logo personalizado SVG

### 📋 Pendiente (para cuando empiece la temporada)
- Evolución se llenará automáticamente
- Finanzas se llenará con jornadas jugadas
- Clausulables necesita métricas de rendimiento
- Analytics: General, Clasificación, Jugadores, Oportunidades, Proyecciones

### 💡 Ideas futuras
- Cron/scheduler para sync automático diario
- PWA para acceso desde móvil
- Alertas por Telegram cuando un jugador baja de precio
- Mejorar puja sugerida con historial de temporada actual (cuando haya más datos)

---

## Transacciones Manuales Insertadas

Jugadores cuya compra no aparece en la sala de prensa de Futmondo (campeonato Ivan):
- **Gordon** → Suplentes Team, 44.788.555€ (24/07/2026)
- **Guruzeta** → Bordalass, 21.000.000€ (24/07/2026)
- **Ciss** → Bordalass, 8.500.000€ (24/07/2026)
- **Ángel Pérez** → El Dictador FC, 7.438.359€ (24/07/2026)

---

## Notas Técnicas Importantes

1. **SQLite deadlock**: `save_pressroom_transactions` no puede llamar a `save_player()` (abre segunda conexión). Se hizo inline INSERT.
2. **WAL mode**: Activado en `db_connection.py` para permitir lecturas concurrentes.
3. **Timeout 15s**: Todas las requests a la API de Futmondo tienen timeout.
4. **Sofascore rate limit**: Mínimo 1s entre requests. El sync de 24 jugadores tarda ~90s.
5. **HeidiSQL**: No puede abrir la DB vía `\\wsl$`. Copiar a `C:\Users\jaor49489\Desktop\`.
6. **Angular build SSL**: Requiere `NODE_TLS_REJECT_UNAUTHORIZED=0` por certificados en WSL.
