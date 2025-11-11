# 🐳 Guía de Docker - Futmondo API

Esta guía explica cómo usar Docker para ejecutar la aplicación Futmondo API con todos sus servicios.

## 📋 Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 2.0 o superior)
- Git (opcional)

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales de Futmondo:

```env
FUTMONDO_EMAIL=tu_email@ejemplo.com
FUTMONDO_PASSWORD=tu_contraseña
CHAMPIONSHIP_ID=tu_championship_id
```

### 2. Iniciar Servicios

Usa el script de inicio (recomendado):

```bash
./docker-start.sh
```

O usa Docker Compose directamente:

```bash
docker-compose up -d --build
```

### 3. Verificar Estado

```bash
./docker-status.sh
```

O directamente:

```bash
docker-compose ps
```

## 🌐 Servicios Disponibles

Una vez iniciados, los servicios estarán disponibles en:

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **ngrok Dashboard (opcional)**: http://localhost:4040 *(si habilitas el túnel)*

## 📝 Comandos Útiles

### Iniciar Servicios

```bash
./docker-start.sh               # Usando script
docker-compose up -d            # Usando Docker Compose
docker-compose --profile ngrok up -d frontend-ngrok  # (Opcional) Iniciar túnel ngrok
```

### Detener Servicios

```bash
./docker-stop.sh            # Usando script
docker-compose down         # Usando Docker Compose
```

### Ver Logs

```bash
./docker-logs.sh                  # Todos los servicios
./docker-logs.sh backend          # Solo backend
./docker-logs.sh frontend         # Solo frontend
./docker-logs.sh frontend-ngrok   # Solo ngrok

# O usando Docker Compose
docker-compose logs -f            # Todos los servicios
docker-compose logs -f backend    # Solo backend
docker-compose logs -f frontend   # Solo frontend
docker-compose --profile ngrok logs -f frontend-ngrok   # Solo ngrok
```

### Ver Estado

```bash
./docker-status.sh
docker-compose ps
```

### Reiniciar un Servicio

```bash
docker-compose restart backend
docker-compose restart frontend
```

### Reconstruir Imágenes

```bash
docker-compose build --no-cache
docker-compose up -d
```

## 🗄️ Gestión de Base de Datos

### PostgreSQL (Base de datos principal)

PostgreSQL está configurado como la base de datos principal del proyecto.

#### Ver Estado de PostgreSQL

```bash
./docker-db-status.sh
```

#### Acceder a PostgreSQL Shell (psql)

```bash
./docker-pg-shell.sh
```

O manualmente:

```bash
docker-compose exec postgres psql -U futmondo -d futmondo
```

#### Acceder a pgAdmin (Interfaz Web)

1. Abre tu navegador en: **http://localhost:5050**
2. Login con:
   - **Email**: `admin@futmondo.com` (o el configurado en `.env`)
   - **Password**: `admin123` (o el configurado en `.env`)
3. Agrega un servidor PostgreSQL:
   - **Name**: Futmondo
   - **Host**: `postgres`
   - **Port**: `5432`
   - **Database**: `futmondo`
   - **Username**: `futmondo`
   - **Password**: `futmondo123` (o el configurado en `.env`)

#### Comandos Útiles de PostgreSQL

```sql
-- Listar todas las bases de datos
\l

-- Listar todas las tablas
\dt

-- Ver estructura de una tabla
\d tabla_nombre

-- Ver datos de una tabla
SELECT * FROM tabla_nombre LIMIT 10;

-- Contar registros
SELECT COUNT(*) FROM tabla_nombre;

-- Ver tamaño de la base de datos
SELECT pg_size_pretty(pg_database_size('futmondo'));

-- Salir
\q
```

### SQLite (Alternativa - actualmente deshabilitado)

Si prefieres usar SQLite en lugar de PostgreSQL, puedes cambiar `DATABASE_TYPE=sqlite` en tu `.env`. Sin embargo, PostgreSQL está recomendado para producción.

Para acceder a SQLite (si está habilitado):

```bash
./docker-db-shell.sh
```

O manualmente:

```bash
docker-compose exec backend sqlite3 /app/data/futmondo_data.db
```

### Comandos SQLite Útiles

```sql
.tables              # Ver todas las tablas
.schema              # Ver el esquema completo
.schema players      # Ver esquema de una tabla específica
SELECT COUNT(*) FROM players;  # Contar registros
.quit                # Salir
```

### Ver Ubicación de la Base de Datos

La base de datos SQLite se encuentra en:

```
./backend/data/futmondo_data.db
```

Este directorio está montado como volumen en Docker, por lo que los datos persisten incluso si se eliminan los contenedores.

### Hacer Backup de la Base de Datos

```bash
docker-compose exec backend cp /app/data/futmondo_data.db /app/data/futmondo_data.db.backup
```

O desde el host:

```bash
cp ./backend/data/futmondo_data.db ./backend/data/futmondo_data.db.backup
```

## 🔧 Shell de Contenedores

### Acceder al Shell del Backend

```bash
./docker-shell.sh backend
```

### Acceder al Shell del Frontend

```bash
./docker-shell.sh frontend
```

## 📊 Monitoreo y Health Checks

Todos los servicios tienen health checks configurados. Puedes verificar el estado:

```bash
docker-compose ps
```

Los servicios mostrarán su estado de salud:
- `healthy`: Servicio funcionando correctamente
- `unhealthy`: Servicio con problemas
- `starting`: Servicio iniciando

## 🔄 Actualizar Servicios

### Reconstruir e Iniciar

```bash
docker-compose up -d --build
```

### Reconstruir Solo un Servicio

```bash
docker-compose build backend
docker-compose up -d backend
```

## 🧹 Limpieza

### Detener y Eliminar Contenedores

```bash
docker-compose down
```

### Eliminar Contenedores, Redes y Volúmenes

```bash
docker-compose down -v
```

**⚠️ Cuidado**: Esto eliminará también los datos de la base de datos si usas volúmenes de Docker.

### Eliminar Imágenes

```bash
docker-compose down --rmi all
```

### Limpiar Todo (Contenedores, Imágenes, Volúmenes no usados)

```bash
docker system prune -a --volumes
```

**⚠️ Cuidado**: Esto eliminará todos los contenedores, imágenes y volúmenes no utilizados del sistema.

## 🗂️ Estructura de Volúmenes

Los siguientes directorios están montados como volúmenes:

- `./backend/data` → `/app/data` (Base de datos y datos persistentes)
- `./backend/static` → `/app/static` (Fotos y archivos estáticos)

Esto asegura que los datos persistan incluso si se eliminan los contenedores.

## 🐛 Troubleshooting

### Los servicios no inician

1. **Verificar logs**:
   ```bash
   docker-compose logs
   ```

2. **Verificar estado**:
   ```bash
   docker-compose ps
   ```

3. **Verificar puertos**:
   ```bash
   lsof -i :8000  # Backend
   lsof -i :3000  # Frontend
   ```

### Error de permisos

Si tienes problemas de permisos con los volúmenes:

```bash
sudo chown -R $USER:$USER ./backend/data
sudo chown -R $USER:$USER ./backend/static
```

### La base de datos no persiste

Asegúrate de que el directorio `./backend/data` existe:

```bash
mkdir -p ./backend/data
```

### Reconstruir desde cero

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 🔐 Seguridad

### Variables de Entorno

- **NUNCA** subas el archivo `.env` al repositorio Git
- El archivo `.env` está en `.gitignore`
- Usa `.env.example` como plantilla

### Credenciales

Las credenciales de Futmondo están en el archivo `.env` y se inyectan como variables de entorno en los contenedores.

## 📚 Recursos Adicionales

- [Documentación de Docker](https://docs.docker.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [API Documentation](./README.md#api-endpoints)

## 🔮 PostgreSQL (Opcional)

Si en el futuro quieres usar PostgreSQL en lugar de SQLite, descomenta las secciones correspondientes en `docker-compose.yml`:

```yaml
postgres:
  image: postgres:15-alpine
  # ... configuración
```

Y actualiza las variables de entorno para usar PostgreSQL.

---

**¿Problemas?** Revisa los logs con `./docker-logs.sh` o abre un issue en el repositorio.

