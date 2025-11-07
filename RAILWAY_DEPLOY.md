# 🚂 Guía de Despliegue en Railway

Esta guía te ayudará a desplegar Futmondo API en Railway usando un solo repositorio con múltiples servicios.

## 📋 Prerrequisitos

1. Cuenta en [Railway](https://railway.app)
2. Repositorio GitHub con el código
3. Tarjeta de crédito (para el plan Hobby, aunque hay créditos gratis)

## 🚀 Pasos de Despliegue

### 1. Preparar el Repositorio GitHub

```bash
# Si aún no tienes git inicializado
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/futmondo-api.git
git branch -M main
git push -u origin main
```

### 2. Crear Proyecto en Railway

1. Ve a [Railway Dashboard](https://railway.app/dashboard)
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona el repositorio `futmondo-api`

### 3. Configurar Servicio PostgreSQL

1. En el proyecto de Railway, click en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente un servicio PostgreSQL
4. **IMPORTANTE**: Copia la variable `DATABASE_URL` que Railway genera automáticamente

### 4. Configurar Servicio Backend

1. En el proyecto de Railway, click en **"+ New"**
2. Selecciona **"GitHub Repo"** → Selecciona tu repo
3. Railway detectará el Dockerfile, pero necesitas configurarlo:
   - **Root Directory**: `/backend`
   - **Dockerfile Path**: `backend/Dockerfile` (o deja en blanco si está en la raíz del servicio)

#### Variables de Entorno del Backend:

```env
# Futmondo API Credentials
FUTMONDO_EMAIL=tu_email@ejemplo.com
FUTMONDO_PASSWORD=tu_contraseña

# Championship IDs
CHAMPIONSHIP_ID=599b0e413f8a751620554699
LEAGUE_ID=504e4f584d8bec9a67000079

# Database (usar DATABASE_URL de Railway PostgreSQL)
DATABASE_TYPE=postgresql
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Railway lo inyecta automáticamente

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Cache
CACHE_DURATION_HOURS=24
```

**Nota**: Railway inyecta automáticamente `DATABASE_URL` desde el servicio PostgreSQL. Puedes usar `${{Postgres.DATABASE_URL}}` o Railway lo hará automáticamente si nombras el servicio "Postgres".

### 5. Configurar Servicio Frontend

1. En el proyecto de Railway, click en **"+ New"**
2. Selecciona **"GitHub Repo"** → Selecciona tu repo
3. Configuración:
   - **Root Directory**: `/frontend`
   - **Dockerfile Path**: `frontend/Dockerfile`

#### Variables de Entorno del Frontend:

```env
PORT=3000
API_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}  # URL pública del backend
NGROK_ENABLED=false
```

**Nota**: Reemplaza `Backend` con el nombre exacto de tu servicio backend en Railway.

### 6. Configurar Dominios Públicos

1. Para cada servicio (Backend y Frontend):
   - Click en el servicio
   - Ve a la pestaña **"Settings"**
   - Click en **"Generate Domain"** para obtener una URL pública
   - O configura un dominio personalizado

2. **Actualiza la variable de entorno del Frontend**:
   - `API_URL` debe apuntar a la URL pública del backend
   - Ejemplo: `https://backend-production-xxxx.up.railway.app`

### 7. Verificar Despliegue

1. **Backend Health Check**:
   ```bash
   curl https://tu-backend.railway.app/health
   ```

2. **Frontend**:
   - Abre la URL pública del frontend en el navegador

3. **Verificar Sincronización**:
   ```bash
   curl https://tu-backend.railway.app/api/v1/sync/status
   ```

## 🔧 Configuración Adicional

### Cron Job para Sincronización

El cron job está configurado en el Dockerfile para ejecutarse a las 02:00 AM UTC. Si necesitas cambiarlo:

1. Edita `backend/Dockerfile` línea 27
2. Cambia el horario: `0 2 * * *` (formato cron)
3. Re-despliega el servicio

### Logs

Para ver logs en Railway:
1. Click en el servicio
2. Ve a la pestaña **"Deployments"**
3. Click en el deployment activo
4. Verás los logs en tiempo real

### Variables de Entorno Compartidas

Railway permite compartir variables entre servicios:
1. Ve a **Project Settings** → **Variables**
2. Define variables compartidas
3. Referéncialas con `${{VariableName}}`

## 💰 Costos Estimados

- **Plan Hobby (Gratis con créditos)**:
  - $5 créditos gratis/mes
  - Backend: ~$0.50-1/mes
  - Frontend: ~$0.50-1/mes
  - PostgreSQL: ~$5/mes (1GB)
  - **Total**: ~$6-7/mes (dentro del crédito gratis)

- **Plan Pro ($20/mes)**:
  - Incluye más recursos y mejor rendimiento
  - Recomendado para producción

## 🐛 Troubleshooting

### Error: "Cannot connect to database"
- Verifica que `DATABASE_URL` esté configurada correctamente
- Asegúrate de que el servicio PostgreSQL esté corriendo
- Verifica que el backend tenga acceso al servicio PostgreSQL (mismo proyecto)

### Error: "Frontend cannot reach backend"
- Verifica que `API_URL` en el frontend apunte a la URL pública del backend
- Asegúrate de que el backend tenga un dominio público generado

### Cron job no funciona
- Verifica los logs del contenedor: `docker logs <container>`
- O usa Railway Cron (servicio separado) en lugar de cron dentro del contenedor

## 📚 Recursos

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Pricing](https://railway.app/pricing)

