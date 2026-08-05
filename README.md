# 🏆 Futmondo Analytics

Aplicación web para gestionar y analizar campeonatos de Futmondo (fantasy football). Permite controlar presupuestos, analizar el mercado, obtener datos de Sofascore, y pujar por jugadores directamente desde la app.

## 🏗️ Arquitectura

```
futmondo-analytics/
├── angular-app/          # Frontend Angular 22 + Material 22
├── backend/              # Backend FastAPI (Python)
├── proxy/                # Nginx reverse proxy config
├── docs/                 # Documentación técnica
├── docker-compose.yml    # Orquestación Docker
├── .env.example          # Template de variables de entorno
└── .env                  # Variables de entorno (no en git)
```

- **Frontend**: Angular 22 con standalone components, signals, Angular Material 22
- **Backend**: FastAPI (Python) — API REST + proxy a API de Futmondo + integración Sofascore
- **Base de datos**: SQLite (local)
- **Integraciones**: API Futmondo (datos del juego), API Sofascore (ratings reales)

## 🚀 Arrancar el proyecto

### 🐳 Con Docker (recomendado)

La forma más rápida. Solo necesitas Docker instalado:

```bash
# 1. Clonar el repo
git clone https://github.com/Mutinho/futmondo-analytics.git
cd futmondo-analytics

# 2. Configurar credenciales
cp .env.example .env
# Edita .env con tus credenciales de Futmondo

# 3. Arrancar todo
docker compose up --build

# ¡Listo! → http://futmondo.localhost
```

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://futmondo.localhost | App Angular |
| Backend API | http://futmondo-api.localhost | API FastAPI |

> Los dominios `.localhost` resuelven automáticamente a 127.0.0.1 — no hace falta tocar `/etc/hosts`.

Comandos útiles:
```bash
docker compose up -d          # Arrancar en background
docker compose logs -f        # Ver logs en tiempo real
docker compose down           # Parar todo
docker compose down -v        # Parar y borrar volúmenes (resetear DB)
```

### 💻 Sin Docker (desarrollo local)

#### Prerrequisitos
- Node.js v24.15+ (usar `nvm use 24.15`)
- Python 3.12+
- SQLite

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8001, reload=False)"
```

#### Frontend

```bash
cd angular-app
npm install
NODE_TLS_REJECT_UNAUTHORIZED=0 npx ng serve --port 4200
```

#### Variables de entorno (.env en raíz)

```
FUTMONDO_EMAIL=tu_email
FUTMONDO_PASSWORD=tu_password
BASE_URL=https://api.futmondo.com
CHAMPIONSHIP_ID=592416daa3a2dd871a7a9956
DATABASE_TYPE=sqlite
DATABASE_PATH=futmondo_data.db
API_HOST=0.0.0.0
API_PORT=8001
```

## 📱 Funcionalidades

### 💰 Presupuesto
- Tabla de saldos por equipo (presupuesto base - compras + ventas)
- Valor de plantilla, rendimiento, puja máxima
- Click en equipo → detalle de altas y bajas
- Sortable por todas las columnas

### 🛒 Mercado
- Jugadores del computer disponibles hoy para fichar
- Puja sugerida basada en historial de transacciones
- Rating de Sofascore integrado (con enlace a perfil)
- Tendencia de valor (subida/bajada del día)
- Pujas activas y botón para pujar/cancelar directamente
- Banner con: presupuesto, invertido en pujas, puja máxima, disponible

### 📊 Evolución
- Gráficos de puntos acumulados y posiciones por jornada (Chart.js)
- Se llena cuando empieza la temporada

### 📈 Estadísticas
- Gráficos de barras: operaciones y gasto neto por equipo
- Click en barra → modal con movimientos del equipo

### 💰 Finanzas
- Tabla de finanzas por usuario (puntos, profit, dream team, MVP)

### ⚽ Clausulables (solo en ligas con cláusulas)
- Jugadores con mejor relación calidad/cláusula para robar a rivales

### 📊 Analytics Avanzado
- **General**: Tendencias y momentum
- **Clasificación Dinámica**: Filtrable por últimas N jornadas
- **Jugadores**: Top rendimiento reciente
- **Mercado**: Watchlist de agentes libres
- **Oportunidades**: Rachas activas
- **Proyecciones**: Dificultad próxima jornada

## 🔄 Sincronización

Botón global en la toolbar que ejecuta:
1. Sync de transacciones (compras/ventas de Futmondo)
2. Detección de jugadores fantasma (sin compra registrada)
3. Sync de ratings Sofascore (jugadores del mercado)

Muestra fecha de última sincronización.

## ⚙️ Configuración de campeonatos

Tabla `championships_config` en SQLite:
- `592416daa3a2dd871a7a9956` — "Ivan el flautista de Futmondin" (sin cláusulas, 200M)
- `6a5f82a09c06c8d0ceaa40ee` — "Infantino es español" (con cláusulas, 300M)

Selector en el sidebar. La selección se persiste en localStorage.

## 🌙 Dark Mode

Toggle en la toolbar. Se persiste en localStorage. Angular Material adapta automáticamente todos los componentes.

## 📡 Endpoints principales del backend

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/championships` | GET | Lista campeonatos configurados |
| `/api/v1/analytics/balances` | GET | Presupuestos de todos los equipos |
| `/api/v1/analytics/balances/{id}` | GET | Detalle altas/bajas de un equipo |
| `/api/v1/market/today` | GET | Jugadores del mercado + puja sugerida + Sofascore |
| `/api/v1/market/bid` | POST | Realizar puja en Futmondo |
| `/api/v1/market/cancelbid` | POST | Cancelar puja activa |
| `/api/v1/sync/trigger` | POST | Sincronizar datos (transacciones, jugadores, etc.) |
| `/api/v1/sync/sofascore` | POST | Sincronizar ratings de Sofascore |
| `/api/v1/sync/check-phantoms` | POST | Detectar jugadores sin compra registrada |
| `/api/v1/sync/last-sync` | GET | Fecha última sincronización |
| `/api/v1/sofascore/player/{name}` | GET | Stats detalladas de Sofascore de un jugador |
| `/api/v1/user-stats/` | GET | Estadísticas por usuario |
| `/api/v1/matchdays/evolution` | GET | Evolución de puntos/posiciones |

## 📄 Licencia

MIT
