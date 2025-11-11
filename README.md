# 🏆 Futmondo Web Application

Aplicación web completa para visualizar y analizar datos de Futmondo (fantasy football). Permite ver la evolución de puntos y posiciones de todos los equipos jornada a jornada con gráficos interactivos.

## 🚀 Despliegue Rápido en Railway

Para desplegar en Railway, consulta la [Guía de Despliegue en Railway](./RAILWAY_DEPLOY.md).

### Resumen Rápido:
1. Crea un repositorio GitHub con este código
2. Crea un proyecto en Railway y conecta el repo
3. Añade 3 servicios: Backend, Frontend, y PostgreSQL
4. Configura las variables de entorno según `RAILWAY_DEPLOY.md`
5. Ejecuta una sincronización inicial (`/api/v1/sync/trigger?sync_type=all`) para poblar estadísticas y cuotas
6. ¡Listo! 🎉

## 🏗️ Arquitectura

- **Backend**: FastAPI (Python) - API REST en puerto 8000
- **Frontend**: Node.js + Express - Interfaz web en puerto 3000
- **Visualización**: Chart.js para gráficos interactivos

## 📁 Estructura del Proyecto

```
FutmondoAPI/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints API
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           └── matchdays.py
│   │   ├── core/           # Configuración
│   │   │   └── config.py
│   │   ├── models/         # Modelos Pydantic (para futuros endpoints)
│   │   │   └── models.py
│   │   ├── services/       # Lógica de negocio
│   │   │   ├── futmondo_client.py
│   │   │   ├── data_manager.py
│   │   │   ├── analyzers.py
│   │   │   ├── team_analyzer.py
│   │   │   └── futmondo_service.py
│   │   └── main.py         # Aplicación FastAPI
│   ├── requirements.txt
│   └── run.py
├── frontend/               # Frontend Node.js
│   ├── public/
│   │   ├── index.html
│   │   └── app.js
│   ├── package.json
│   └── server.js
├── futmondo_data.db        # Base de datos SQLite (generada automáticamente)
└── README.md
```

## 🚀 Instalación y Uso

### 🐳 Opción 1: Docker (Recomendado)

La forma más fácil de ejecutar la aplicación es usando Docker. Consulta la **[Guía Completa de Docker](./DOCKER_README.md)** para más detalles.

#### Inicio Rápido con Docker:

```bash
# 1. Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Futmondo

# 2. Iniciar todos los servicios
./docker-start.sh

# 3. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# (Opcional) Túnel ngrok para el frontend
# Requiere NGROK_AUTHTOKEN en tu .env y levantar el perfil ngrok:
# docker compose --profile ngrok up frontend-ngrok
# ngrok dashboard: http://localhost:4040
```

#### Scripts Docker Disponibles:

- `./docker-start.sh` - Inicia todos los servicios Docker
- `./docker-stop.sh` - Detiene todos los servicios
- `./docker-status.sh` - Muestra el estado de los servicios
- `./docker-logs.sh` - Muestra los logs (o `./docker-logs.sh backend` para un servicio específico)
- `./docker-shell.sh [backend|frontend]` - Accede al shell de un contenedor
- `./docker-db-shell.sh` - Accede a la base de datos SQLite

Para más información, consulta **[DOCKER_README.md](./DOCKER_README.md)**.

### ⚙️ Opción 2: Instalación Manual

#### Prerrequisitos

- Python 3.8 o superior
- Node.js 16 o superior y npm
- ngrok (opcional, para acceso público al frontend)

#### Scripts Disponibles

- `./start-backend.sh` - Inicia el backend (detiene procesos anteriores automáticamente)
- `./start-frontend.sh` - Inicia el frontend
- `./start-ngrok.sh` - Crea túnel público con ngrok
- `./kill-backend.sh` - Detiene el backend si está corriendo

### Paso 1: Configurar el Backend

1. **Navegar al directorio backend:**
```bash
cd backend
```

2. **Crear entorno virtual (recomendado):**
```bash
python3 -m venv venv
```

3. **Activar el entorno virtual:**
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Configurar credenciales (opcional):**
Edita `backend/app/core/config.py` para cambiar credenciales de Futmondo si es necesario:
```python
FUTMONDO_EMAIL = "tu_email@ejemplo.com"
FUTMONDO_PASSWORD = "tu_contraseña"
CHAMPIONSHIP_ID = "tu_championship_id"
```

6. **Iniciar el servidor backend:**
```bash
python run.py
```

El backend estará disponible en: **http://localhost:8000**

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Paso 2: Configurar el Frontend

Abre una **nueva terminal** (mantén el backend corriendo):

1. **Navegar al directorio frontend:**
```bash
cd frontend
```

2. **Instalar dependencias:**
```bash
npm install
```

3. **Iniciar el servidor frontend:**
```bash
npm start
```

El frontend estará disponible en: **http://localhost:3000**

### Paso 3: Acceso Público con ngrok (Opcional)

Si quieres compartir el frontend con tus amigos, puedes usar ngrok:

1. **Instalar ngrok** (si no lo tienes):
   - Descarga desde: https://ngrok.com/download
   - O con Homebrew (macOS): `brew install ngrok`

2. **Iniciar ngrok en una nueva terminal:**
```bash
ngrok http 3000
```

3. **Copiar la URL pública:**
ngrok te dará una URL pública como: `https://xxxx-xx-xx-xxx.ngrok.io`

4. **Compartir la URL:**
Comparte esa URL con tus amigos para que puedan acceder al frontend desde cualquier lugar.

**Nota:** ngrok crea una URL temporal. Cada vez que reinicies ngrok, obtendrás una nueva URL.

## 🌐 URLs de Acceso

### Desarrollo Local

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Público (con ngrok)

- **Frontend público**: `https://xxxx-xx-xx-xxx.ngrok.io` (la URL que ngrok proporciona)
- El backend sigue siendo local, pero el frontend lo consume a través del proxy

## 📡 Endpoints API

### Matchdays

#### `GET /api/v1/matchdays/evolution`
Obtiene datos completos de evolución para todos los equipos.

**Response:**
```json
{
  "success": true,
  "data": {
    "matchdays": [1, 2, 3, ...],
    "teams": [
      {
        "team_id": "...",
        "team_name": "Nombre del Equipo",
        "points_evolution": [40, 70, 100, ...],
        "positions_evolution": [1, 2, 1, ...]
      }
    ]
  }
}
```

#### `GET /api/v1/matchdays/teams`
Obtiene lista de todos los equipos del campeonato.

#### `GET /api/v1/matchdays/teams/{team_id}/rounds`
Obtiene los rounds (puntos por jornada) de un equipo específico.

## 📊 Analytics API

Se han añadido endpoints avanzados para reforzar el scouting y la toma de decisiones. Todos están disponibles bajo el prefijo `/api/v1/analytics`.

- `GET /championship/trends` — Evolución de puntos/posiciones por equipo (parámetro `window` para últimas jornadas).
- `GET /championship/custom-classification` — Clasificación filtrable por últimas jornadas con exclusión de jornadas concretas.
- `GET /championship/heatmap` — Heatmap de puntos por jornada.
- `GET /players/form` — Form de jugadores (media, tendencia) en una ventana móvil.
- `GET /players/value-trend` — Evolución de precios de mercado frente a cláusulas sugeridas.
- `GET /users/consistency` — Índice de consistencia y volatilidad de managers.
- `GET /users/market-activity` — Actividad de mercado (compras/ventas/cláusulas) por equipo.
- `GET /market/watchlist` — Agentes libres ordenados por relación puntos/cláusula.
- `GET /clauses/network` — Grafo de cláusulas pagadas/recibidas.
- `GET /opportunities/streaks` — Rachas activas de jugadores por encima de un umbral de puntos.
- `GET /projections/matchday` — Dificultad proyectada de la próxima jornada combinando odds y forma.

Cada endpoint acepta `championship_id` como query param (opcional si está configurado en `config.py`).

## 🔐 Acceso a la aplicación

La aplicación arranca en modo invitado, mostrando únicamente el contenido no premium (sin pestaña de Finanzas ni Jugadores Clausulables, y con Analytics limitado a Visión General y Clasificación Dinámica).  
Para desbloquear todo el contenido pulsa “Iniciar sesión” (arriba a la derecha) e introduce:

- Usuario premium: `patxo`
- Contraseña: `aporlavictoria2026.`

Al cerrar sesión vuelves automáticamente al modo invitado.

## 🎨 Características

- ✅ Visualización interactiva de puntos acumulados
- ✅ Visualización de posiciones jornada a jornada con números en cada punto
- ✅ Gráficos responsivos con Chart.js
- ✅ Diseño moderno y atractivo
- ✅ Clasificación dinámica con filtros de jornadas
- ✅ API REST limpia y documentada
- ✅ CORS configurado para desarrollo
- ✅ Acceso público con ngrok

## 🛠️ Desarrollo

### Añadir nuevos endpoints

1. Crear endpoint en `backend/app/api/v1/endpoints/`
2. Registrar en `backend/app/main.py`
3. Consumir desde `frontend/public/app.js`

### Añadir nuevas visualizaciones

1. Crear función en `frontend/public/app.js`
2. Añadir elemento canvas en `frontend/public/index.html`
3. Usar Chart.js para crear gráficos interactivos

### Modos de ejecución

**Backend:**
- `python run.py` - Inicia con auto-reload (recomendado para desarrollo)

**Frontend:**
- `npm start` - Inicia servidor (producción)
- `npm run dev` - Inicia con nodemon (auto-reload, requiere nodemon instalado)
- `npm run ngrok` - Inicia ngrok (requiere ngrok instalado y configurado)

## 🔧 Solución de Problemas

### Backend no inicia - Puerto 8000 en uso

Si obtienes el error `[Errno 48] Address already in use`:

**Opción 1: El script lo detiene automáticamente**
- El script `start-backend.sh` detecta y detiene procesos anteriores automáticamente
- Simplemente ejecuta: `./start-backend.sh`

**Opción 2: Detener manualmente**
```bash
# Detener proceso en puerto 8000
./kill-backend.sh

# O manualmente:
lsof -ti:8000 | xargs kill  # Detener suavemente
lsof -ti:8000 | xargs kill -9  # Forzar detención
```

**Opción 3: Cambiar puerto**
Edita `backend/app/core/config.py` y cambia:
```python
API_PORT = 8001  # O cualquier otro puerto libre
```

### Otros problemas

- Verifica que Python 3.8+ esté instalado
- Asegúrate de que todas las dependencias estén instaladas: `pip install -r requirements.txt`
- Verifica que el puerto 8000 no esté en uso: `lsof -ti:8000`

### Frontend no conecta con backend

- Verifica que el backend esté corriendo en puerto 8000
- Revisa la configuración de CORS en `backend/app/main.py`
- Verifica la URL de la API en `frontend/public/app.js`

### ngrok no funciona

- Asegúrate de tener ngrok instalado: `ngrok version`
- Verifica que el frontend esté corriendo en puerto 3000
- Si usas cuenta gratuita, la URL expira después de un tiempo

## 📝 Notas

- El backend realiza auto-login con las credenciales configuradas
- Los datos se obtienen en tiempo real desde la API de Futmondo
- Los gráficos se generan en el frontend usando Chart.js
- El frontend actúa como proxy para las llamadas API
- La base de datos SQLite se crea automáticamente en la raíz del proyecto

## 📄 Licencia

MIT
