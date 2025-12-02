# 🐘 Guía de PostgreSQL - Futmondo API

Esta guía explica cómo usar PostgreSQL como base de datos para el proyecto Futmondo API.

## 🚀 Inicio Rápido

PostgreSQL está configurado automáticamente en `docker-compose.yml`. Simplemente inicia los servicios:

```bash
docker-compose up -d
```

Esto iniciará:
- ✅ PostgreSQL en puerto **5432**
- ✅ pgAdmin en puerto **5050**
- ✅ Backend conectado a PostgreSQL
- ✅ Frontend

## 🌐 Acceder a pgAdmin

1. **Abre tu navegador**: http://localhost:5050

2. **Login**:
   - **Email**: `admin@futmondo.com` (o el configurado en `.env`)
   - **Password**: `admin123` (o el configurado en `.env`)

3. **Agrega el servidor PostgreSQL**:
   - Click derecho en "Servers" → "Register" → "Server"
   - **General Tab**:
     - **Name**: `Futmondo`
   - **Connection Tab**:
     - **Host name/address**: `postgres`
     - **Port**: `5432`
     - **Maintenance database**: `futmondo`
     - **Username**: `futmondo`
     - **Password**: `futmondo123` (o el configurado en `.env`)
     - ✅ Marca "Save password"
   - Click "Save"

## 🔧 Scripts de Gestión

### Ver Estado de PostgreSQL

```bash
./docker-db-status.sh
```

### Acceder a PostgreSQL Shell

```bash
./docker-pg-shell.sh
```

### Ver Logs de PostgreSQL

```bash
./docker-logs.sh postgres
```

### Ver Logs de pgAdmin

```bash
./docker-logs.sh pgadmin
```

## 📊 Comandos SQL Útiles

Una vez dentro de `psql` (con `./docker-pg-shell.sh`):

```sql
-- Listar todas las bases de datos
\l

-- Conectar a la base de datos
\c futmondo

-- Listar todas las tablas
\dt

-- Ver estructura de una tabla
\d users
\d players
\d transactions

-- Ver datos de una tabla
SELECT * FROM users LIMIT 10;
SELECT * FROM players LIMIT 10;
SELECT * FROM transactions LIMIT 10;

-- Contar registros
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM players;
SELECT COUNT(*) FROM transactions;

-- Ver tamaño de la base de datos
SELECT pg_size_pretty(pg_database_size('futmondo'));

-- Ver tamaño de cada tabla
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ver todas las tablas y su tamaño
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size('public.' || table_name)) AS size,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_name = t.table_name) AS columns
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size('public.' || table_name) DESC;

-- Salir
\q
```

## 🔐 Configuración

### Variables de Entorno

En tu archivo `.env`:

```env
# Tipo de base de datos (sqlite o postgresql)
DATABASE_TYPE=postgresql

# Configuración de PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=futmondo
POSTGRES_USER=futmondo
POSTGRES_PASSWORD=futmondo123

# Configuración de pgAdmin
PGADMIN_EMAIL=admin@futmondo.com
PGADMIN_PASSWORD=admin123
PGADMIN_PORT=5050
```

### Cambiar Contraseñas

Para cambiar las contraseñas de PostgreSQL o pgAdmin, edita tu archivo `.env` y reinicia los servicios:

```bash
# Edita .env
nano .env

# Reinicia los servicios
docker-compose down
docker-compose up -d
```

## 💾 Gestión de Datos

### Hacer Backup

```bash
# Backup completo de la base de datos
docker-compose exec postgres pg_dump -U futmondo futmondo > backup_$(date +%Y%m%d_%H%M%S).sql

# O desde fuera del contenedor
docker exec futmondo-postgres pg_dump -U futmondo futmondo > backup.sql
```

### Restaurar Backup

```bash
# Restaurar desde un archivo SQL
docker-compose exec -T postgres psql -U futmondo -d futmondo < backup.sql

# O desde fuera del contenedor
docker exec -i futmondo-postgres psql -U futmondo -d futmondo < backup.sql
```

### Ver Ubicación de los Datos

Los datos de PostgreSQL se almacenan en un volumen de Docker:

```bash
docker volume inspect futmondoapi_postgres-data
```

Esto mostrará la ubicación en el sistema de archivos del host.

## 🔄 Migración de SQLite a PostgreSQL

Si actualmente usas SQLite y quieres migrar a PostgreSQL:

1. **Inicia PostgreSQL**:
   ```bash
   docker-compose up -d postgres
   ```

2. **Copia los datos desde SQLite**:
   - Exporta los datos de SQLite
   - Importa a PostgreSQL usando `pgAdmin` o scripts de migración

3. **Actualiza `.env`**:
   ```env
   DATABASE_TYPE=postgresql
   ```

4. **Reinicia el backend**:
   ```bash
   docker-compose restart backend
   ```

## 📈 Monitoreo

### Ver Estadísticas de PostgreSQL

```bash
docker stats futmondo-postgres
```

### Ver Logs en Tiempo Real

```bash
docker-compose logs -f postgres
```

### Ver Conexiones Activas

```sql
-- Desde psql
SELECT * FROM pg_stat_activity WHERE datname = 'futmondo';
```

## 🐛 Troubleshooting

### PostgreSQL no inicia

1. **Ver logs**:
   ```bash
   docker-compose logs postgres
   ```

2. **Verificar permisos del volumen**:
   ```bash
   docker volume inspect futmondoapi_postgres-data
   ```

3. **Reiniciar**:
   ```bash
   docker-compose restart postgres
   ```

### No puedo conectar desde pgAdmin

1. **Verificar que PostgreSQL está corriendo**:
   ```bash
   docker-compose ps postgres
   ```

2. **Verificar que pgAdmin está corriendo**:
   ```bash
   docker-compose ps pgadmin
   ```

3. **Verificar credenciales en `.env`**:
   ```bash
   grep POSTGRES .env
   ```

4. **Revisar logs**:
   ```bash
   docker-compose logs pgadmin
   ```

### Error de conexión desde el backend

1. **Verificar variables de entorno**:
   ```bash
   docker-compose exec backend env | grep POSTGRES
   ```

2. **Verificar que PostgreSQL está accesible**:
   ```bash
   docker-compose exec backend ping postgres
   ```

3. **Revisar logs del backend**:
   ```bash
   docker-compose logs backend | grep -i database
   ```

## 📚 Recursos

- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de pgAdmin](https://www.pgadmin.org/docs/)
- [Docker PostgreSQL Image](https://hub.docker.com/_/postgres)
- [Docker pgAdmin Image](https://hub.docker.com/r/dpage/pgadmin4)

## 🔒 Seguridad

- **Cambia las contraseñas por defecto** en producción
- **No expongas PostgreSQL directamente** a internet sin protección
- **Usa conexiones SSL** en producción
- **Haz backups regulares** de tu base de datos

---

**¿Problemas?** Revisa los logs con `./docker-logs.sh postgres` o `./docker-logs.sh pgadmin`.








