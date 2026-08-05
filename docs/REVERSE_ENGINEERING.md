# Reverse Engineering - Frontend Futmondo

**Fecha de análisis:** 2026-08-04  
**Versión analizada:** 1.0.0 (package.json)

---

## 1. Arquitectura General

### Stack Tecnológico
- **Servidor:** Node.js + Express (server.js)
- **Frontend:** Vanilla JavaScript SPA (app.js) — sin framework
- **Visualización:** Chart.js 4.4.0 (CDN)
- **Estilos:** CSS inline en `<style>` dentro del HTML (no hay archivos CSS externos)
- **Proxy API:** Express middleware que reenvía `/api/*` al backend FastAPI
- **Tunnel público:** ngrok integrado (@ngrok/ngrok)

### Patrón Arquitectónico
- **SPA monolítica:** Una sola página HTML con múltiples tabs gestionadas por JavaScript
- **Proxy pattern:** El frontend actúa como proxy hacia el backend (mismo origen para evitar CORS)
- **State management:** Variables globales en `app.js` (sin store/redux/signals)
- **Lazy loading:** Los datos de cada tab se cargan solo al acceder por primera vez

---

## 2. Dependencias (package.json)

### Producción
| Paquete | Versión | Uso |
|---------|---------|-----|
| express | ^4.18.2 | Servidor web y proxy API |
| axios | ^1.6.0 | Llamadas HTTP desde el proxy al backend |
| cors | ^2.8.5 | Middleware CORS |
| @ngrok/ngrok | ^1.0.0 | Túnel público para compartir la app |

### Desarrollo
| Paquete | Versión | Uso |
|---------|---------|-----|
| nodemon | ^3.0.1 | Hot reload durante desarrollo |

### CDN (cargadas en el HTML)
| Librería | Versión | URL |
|----------|---------|-----|
| Chart.js | 4.4.0 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js` |

---

## 3. Servidor (server.js)

### Configuración
```
PORT = process.env.PORT || 3000
API_URL = process.env.API_URL || 'http://localhost:8000'
NGROK_ENABLED = process.env.NGROK_ENABLED === 'true'
NGROK_AUTHTOKEN = process.env.NGROK_AUTHTOKEN
```

### Rutas del servidor
| Ruta | Método | Descripción |
|------|--------|-------------|
| `/api/*` | ALL | Proxy pass → `API_URL/api/*` |
| `/*` | GET | Sirve archivos estáticos o `index.html` (catch-all SPA) |

### Middleware
1. `cors()` — Habilita CORS
2. `express.json()` — Parsea body JSON
3. `express.static('public')` — Archivos estáticos
4. Proxy API — Reenvía todas las peticiones `/api` al backend

---

## 4. Endpoints API Consumidos

### Autenticación (`/api/v1/auth`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | Login con username/password → devuelve token, role, expires_at |
| `/api/v1/auth/session` | GET | Valida token existente (query param `?token=`) |
| `/api/v1/auth/logout` | POST | Cierra sesión (query param `?token=`) |

### Datos de evolución (`/api/v1/matchdays`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/matchdays/evolution` | GET | Evolución de puntos y posiciones por equipo por jornada |

### Finanzas de usuarios (`/api/v1/player-finances/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/player-finances/` | GET | Finanzas de todos los usuarios (puntos, bonos, transacciones) |

### Estadísticas (`/api/v1/user-stats/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/user-stats/` | GET | Estadísticas por usuario (jugadores únicos, cláusulas, operaciones) |

### Jugadores clausulables (`/api/v1/clausulable-players/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/clausulable-players/` | GET | Top jugadores con mejor relación calidad/cláusula |

### Crónicas humorísticas (`/api/v1/humor`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/humor/article?matchday=N` | GET | Artículo humorístico de una jornada específica |

### Sincronización (`/api/v1/sync`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/sync/trigger?sync_type=transactions` | POST | Sincroniza transacciones desde Futmondo |

### Fotos de jugadores (`/api/v1/photos`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/photos/{player_id}` | GET | Foto de un jugador |
| `/api/v1/photos/default` | GET | Foto por defecto (fallback) |

### Analytics (`/api/v1/analytics`)
| Endpoint | Método | Parámetros | Descripción |
|----------|--------|------------|-------------|
| `/api/v1/analytics/championship/trends` | GET | `window` | Evolución y momentum de equipos |
| `/api/v1/analytics/championship/custom-classification` | GET | `window`, `exclude_matchday[]` | Clasificación filtrable |
| `/api/v1/analytics/championship/heatmap` | GET | — | Heatmap de rendimiento por jornada |
| `/api/v1/analytics/players/form` | GET | `window` | Formulario de jugadores (media, tendencia) |
| `/api/v1/analytics/players/value-trend` | GET | `window` | Evolución de precios de mercado |
| `/api/v1/analytics/users/consistency` | GET | `window` | Índice de consistencia de managers |
| `/api/v1/analytics/users/market-activity` | GET | `window_days` | Actividad de mercado por equipo |
| `/api/v1/analytics/market/watchlist` | GET | `limit` | Agentes libres por relación puntos/cláusula |
| `/api/v1/analytics/clauses/network` | GET | — | Red de cláusulas pagadas/recibidas |
| `/api/v1/analytics/opportunities/streaks` | GET | `min_streak`, `threshold` | Rachas de jugadores |
| `/api/v1/analytics/projections/matchday` | GET | — | Proyecciones de dificultad próxima jornada |
| `/api/v1/analytics/balances` | GET | — | Presupuestos de todos los equipos |
| `/api/v1/analytics/balances/{team_id}` | GET | — | Detalle de altas/bajas de un equipo |

---

## 5. Componentes Visuales

### 5.1 Sistema de Tabs Principal
| Tab | ID | Visible para | Carga datos en |
|-----|-----|-------------|----------------|
| 💰 Presupuesto | `budget-tab` | Todos | `loadBudgetTab()` |
| 📊 Evolución | `evolution-tab` | Todos | `init()` (al inicio) |
| 💰 Finanzas Usuarios | `finances-tab` | Solo premium (oculta) | `loadFinancesData()` |
| 📈 Estadísticas | `stats-tab` | Todos | `loadUserStatsData()` |
| ⚽ Jugadores Clausulables | `clausulable-tab` | Premium (bloqueada si guest) | `loadClausulablePlayersData()` |
| 📰 Crónicas Humorísticas | `humor-tab` | Todos | `ensureHumorTabInitialized()` |
| 📊 Analytics Avanzado | `analytics-tab` | Parcial (secciones premium) | `showAnalyticsSection()` |

### 5.2 Sub-tabs Analytics
| Sección | ID | Acceso |
|---------|-----|--------|
| 🌐 Visión General | `overview` | Todos |
| 🏆 Clasificación Dinámica | `custom` | Todos |
| 🔥 Jugadores | `players` | Premium |
| 👥 Usuarios | `users` | Premium |
| 💹 Mercado | `market` | Premium |
| ⚡ Oportunidades | `opportunities` | Premium |
| 🎯 Proyecciones | `projections` | Premium |

### 5.3 Gráficos (Chart.js)
| Chart | Tipo | Ubicación | Descripción |
|-------|------|-----------|-------------|
| `pointsChart` | Line | Evolución | Puntos acumulados por equipo |
| `positionsChart` | Line | Evolución | Posiciones (eje Y invertido) con números en cada punto |
| `uniquePlayersChart` | Bar | Estadísticas | Jugadores únicos alineados por equipo |
| `clausesChart` | Bar (grouped) | Estadísticas | Cláusulas pagadas vs recibidas |
| `transactionsChart` | Bar | Estadísticas | Número de operaciones por equipo |
| `analyticsMomentumChart` | Bar | Analytics Overview | Momentum promedio top 10 |
| `analyticsConsistencyChart` | Bar | Analytics Usuarios | Índice de consistencia |

### 5.4 Tablas
| Tabla | Ubicación | Ordenable | Descripción |
|-------|-----------|-----------|-------------|
| Finanzas de usuarios | Tab Finanzas | No | Puntos, bonos, dream team, MVP, totales |
| Clausulable players (top 20) | Tab Clausulables | ✅ (click en headers) | Jugadores con métricas de clausulabilidad |
| Heatmap | Analytics Overview | No | Rendimiento por equipo/jornada con colores |
| Tendencias | Analytics Overview | No | Resumen puntos, posición delta, momentum |
| Clasificación Dinámica | Analytics Custom | No | Clasificación configurable (ventana + exclusiones) |
| Player Form | Analytics Players | No | Top 20 jugadores por rendimiento reciente |
| Player Value | Analytics Players | No | Variación de precios de mercado |
| Market Activity | Analytics Users | No | Transacciones y cláusulas por equipo |
| Watchlist | Analytics Market | No | Relación puntos/cláusula de agentes libres |
| Clause Network | Analytics Market | No | Flujo de cláusulas entre equipos |
| Streaks | Analytics Oportunidades | No | Rachas activas de jugadores |
| Presupuesto resumen | Tab Presupuesto | No | Balance, valor, gastado, ingresado por equipo |
| Presupuesto detalle | Tab Presupuesto | No | Compras y ventas de un equipo específico |

### 5.5 Tooltips y Modales
| Componente | Tipo | Trigger | Descripción |
|------------|------|---------|-------------|
| Custom Tooltip (best player) | Tooltip posicionado | Click en punto del gráfico | Muestra foto, nombre, equipo, jornada, puntos y puesto del mejor jugador |
| Budget Detail | Panel inline | Click en fila de equipo | Reemplaza tabla resumen con detalle de compras/ventas |

### 5.6 Controles Interactivos
| Control | Ubicación | Tipo | Descripción |
|---------|-----------|------|-------------|
| Ventana de jornadas | Analytics Custom | Input numérico + botones rápidos (3, 5, 10) | Filtra últimas N jornadas |
| Exclusión de jornadas | Analytics Custom | Chips toggle | Excluye jornadas del cálculo |
| Botón "Aplicar filtros" | Analytics Custom | Button | Refresca clasificación |
| Botón "Limpiar exclusiones" | Analytics Custom | Button | Reset de exclusiones |
| Botón "Sincronizar" | Tab Presupuesto | Button | Trigger sync de transacciones |
| Humor sub-tabs | Tab Crónicas | Botones por jornada | Selecciona jornada del artículo |

---

## 6. Flujo de Autenticación

### Modelo de acceso
- **Modo invitado** (por defecto): Acceso parcial, sin tab Finanzas, sin Clausulables, sin secciones premium de Analytics
- **Modo premium**: Acceso completo a todo el contenido

### Flujo de login
```
1. Usuario abre la app → initializeAuth()
2. ¿Hay token en localStorage (AUTH_STORAGE_KEY = 'futmondoAuth')?
   ├─ SÍ → validateSession(token) via GET /api/v1/auth/session
   │   ├─ Válido → setAuthState({authenticated, username, role, token, expiresAt})
   │   └─ Inválido → clearAuthState(), modo invitado
   └─ NO → modo invitado
3. Login manual: usuario rellena form inline en el header
   → handleLoginSubmit() → POST /api/v1/auth/login {username, password}
   → Respuesta: {username, role, token, expires_at}
   → resetAppState() + setAuthState() + reinicia toda la app
4. Logout: click en "Cerrar sesión"
   → POST /api/v1/auth/logout?token=...
   → clearAuthState() + resetAppState() → modo invitado
```

### Persistencia
- Token se guarda en `localStorage` como JSON: `{username, role, token, expires_at}`
- Al recargar la página se valida el token con el backend

### Restricciones de contenido
- **HIDDEN_PREMIUM_TABS:** `['finances']` — Tab completamente oculta para invitados
- **LOCKED_PREMIUM_TABS:** `['clausulable']` — Tab visible pero contenido bloqueado
- **PREMIUM_ANALYTICS_SECTIONS:** `['players', 'users', 'market', 'opportunities', 'projections']`

### Credenciales conocidas (del README)
- **Usuario premium:** `patxo`
- **Contraseña:** `aporlavictoria2026.`

---

## 7. Gestión de Estado

### Variables globales principales
```javascript
let pointsChart = null;           // Instancia Chart.js puntos
let positionsChart = null;        // Instancia Chart.js posiciones
let evolutionData = null;         // Datos de evolución cacheados
let uniquePlayersChart = null;    // Chart estadísticas
let clausesChart = null;          // Chart estadísticas
let transactionsChart = null;     // Chart estadísticas
let analyticsMomentumChart = null;// Chart analytics
let analyticsConsistencyChart = null; // Chart analytics
let appInitialized = false;       // Flag de inicialización

// Estado de analytics con lazy loading
const analyticsState = {
    loaded: { overview, custom, players, users, market, opportunities, projections },
    caches: {}
};

// Estado de clasificación dinámica
let customClassificationState = { window, pendingWindow, excluded, draftExcluded };

// Estado de humor (crónicas)
let humorState = { initialized, matchdays, cache (Map), currentMatchday };

// Estado de autenticación
let authState = { isAuthenticated, username, role, token, expiresAt };

// Estado de presupuesto
let budgetLoaded = false;
```

---

## 8. Patrones UI/UX Identificados

### Paleta de Colores
- **Primario:** `#90EE90` (Light Green)
- **Secundario:** `#000000` (Black)
- **Accent:** `#32CD32` (Lime Green)
- **Background gradient:** `#667eea → #764ba2` (Purple gradient)
- **Positivo:** `#16a34a` / `#228B22` (Green)
- **Negativo:** `#dc2626` / `#DC143C` (Red)
- **Neutral:** `#d97706` (Orange/Amber)

### Sistema de Design
- **Border radius:** 6px (botones), 8px (cards), 12px (chart cards), 20px (pills/chips), 999px (badges)
- **Shadows:** `0 4px 15px rgba(0,0,0,0.1)` (ligera), `0 10px 30px rgba(0,0,0,0.2)` (fuerte)
- **Tipografía:** System fonts (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto...`)
- **Responsive:** Breakpoint a 768px (tabs wrap, controles en columna, gráficos más pequeños)

### Patrones de interacción
1. **Tabs con lazy loading:** Solo carga datos al acceder a una tab
2. **Loading states:** Spinner de texto "Cargando..." en cada sección
3. **Error states:** Banner rojo con mensaje de error
4. **Access messages:** Banners temporales con borde lateral verde (auto-dismiss con timeout)
5. **Empty states:** Hints con fondo verde claro y borde lateral
6. **Click-to-drill:** En presupuesto, click en fila muestra detalle
7. **Sortable tables:** Headers clickeables con indicador de dirección
8. **Chip selection:** Chips toggle para excluir jornadas
9. **Inline login:** Form de login integrado en el header (no redirección)
10. **Tooltip con foto:** Al clickear puntos en gráficos, muestra tooltip con foto del mejor jugador

### Flujo de navegación
```
App Load → initializeAuth() → startAppIfNeeded()
                                    ↓
                              loadEvolutionData()
                                    ↓
                         displayStats() + createCharts()
                                    ↓
                              showContent()
                                    ↓
                    Tab por defecto: "Presupuesto" (guest) / "Evolución" (auth)
```

---

## 9. Funcionalidades Completas

### 9.1 Presupuesto (Tab principal)
- Tabla resumen con saldo, valor plantilla, gastado, ingresado, operaciones, rendimiento
- Click en equipo para ver detalle de compras y ventas
- Botón de sincronización que llama al backend

### 9.2 Evolución
- Gráfico de líneas con evolución de puntos acumulados
- Gráfico de líneas con evolución de posiciones (invertido, pos 1 arriba)
- Tooltip interactivo al hacer click mostrando el mejor jugador de esa jornada
- Stats cards con número de equipos, jornadas y puntos promedio

### 9.3 Finanzas de Usuarios (Premium)
- Tabla con puntos, dinero por puntos, ganancias transacciones, dream team, MVP, totales

### 9.4 Estadísticas
- Gráfico de barras: Jugadores únicos alineados por equipo
- Gráfico de barras agrupadas: Cláusulas pagadas vs recibidas
- Gráfico de barras: Número de operaciones por equipo

### 9.5 Jugadores Clausulables (Premium)
- Tabla sortable con top 20 jugadores más "clausulables"
- Métricas: 3 scores parciales + score final + cláusula actual/sugerida + promedios

### 9.6 Crónicas Humorísticas
- Sub-tabs por jornada
- Artículo con título, fecha de generación, contenido por párrafos
- Resumen en forma de lista
- Caché por jornada para no re-cargar

### 9.7 Analytics Avanzado
- **Visión General:** Momentum chart + Heatmap table + Tendencias table
- **Clasificación Dinámica:** Tabla configurable con ventana y exclusión de jornadas, detalle por jornada
- **Jugadores:** Form table (media, tendencia) + Value table (variación de precios)
- **Usuarios:** Consistency chart + Market activity table
- **Mercado:** Watchlist table + Clause network table
- **Oportunidades:** Streaks table (rachas activas)
- **Proyecciones:** Cards de próximos partidos con dificultad (favorable/neutral/complicado)

---

## 10. Observaciones y Deuda Técnica

### Positivo
- Proxy API evita problemas de CORS
- Lazy loading reduce carga inicial
- Caché local de analytics y humor reduce llamadas repetidas
- Responsive básico implementado
- Persistencia de sesión en localStorage con validación

### Deuda técnica / Oportunidades de mejora
1. **Código duplicado:** La lógica del tooltip se repite exactamente igual para pointsChart y positionsChart (~200 líneas duplicadas)
2. **No hay bundling:** Todo es un único archivo `app.js` de ~3500 líneas
3. **CSS inline:** Todos los estilos están en `<style>` dentro del HTML
4. **No hay testing:** Sin tests unitarios ni E2E
5. **Sem framework:** Estado global mutable sin patrones reactivos
6. **No hay TypeScript:** Sin tipado estático
7. **XSS potencial:** Uso de `innerHTML` con datos de la API en varios lugares (renderBudgetDetail, renderBudgetTable, etc.)
8. **Chart.js plugin global:** `positionLabelsPlugin` se registra globalmente con `Chart.register()` sin desregistrarlo
9. **Funciones expuestas globalmente:** `showTab`, `showAnalyticsSection`, `loadBudgetDetail`, `hideBudgetDetail`, `syncTransactions` son `onclick` en HTML
10. **Sin service worker:** No hay PWA ni caché offline
11. **Variables redeclaradas:** `formatMoney` está definida dos veces (línea ~1680 y ~3360)
12. **Console.log en producción:** Múltiples `console.log` de debug activos
