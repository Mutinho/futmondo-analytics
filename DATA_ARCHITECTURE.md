# 🏗️ Arquitectura de Datos - Futmondo API

## 📋 Resumen Ejecutivo

Esta arquitectura de datos está diseñada para almacenar y analizar información completa del campeonato Futmondo, permitiendo análisis estadísticos avanzados y actualizaciones diarias eficientes.

## 🗄️ Estructura de Base de Datos

### Tablas Principales

#### 1. **`users`** - Usuarios del campeonato
- `id` (TEXT, PRIMARY KEY): UUID único del usuario
- `username` (TEXT, UNIQUE): Nombre de usuario
- `team_id` (TEXT): ID del equipo en Futmondo
- `team_name` (TEXT): Nombre del equipo
- `last_updated` (TEXT): Última actualización

**Uso**: Gestión de usuarios y equipos, vinculación con transacciones

---

#### 2. **`players`** - Jugadores del campeonato
- `id` (TEXT, PRIMARY KEY): ID del jugador
- `name` (TEXT): Nombre del jugador
- `role` (TEXT): Posición (POR, DEF, MED, DEL)
- `team` (TEXT): Equipo de fútbol real
- `current_value` (INTEGER): Valor actual
- `current_points` (INTEGER): Puntos acumulados
- `userteam_id` (TEXT): Equipo que lo tiene
- `userteam_name` (TEXT): Nombre del equipo que lo tiene
- `average_performance` (TEXT): Estadísticas promedio (JSON)
- `photo_url` (TEXT): URL de la foto
- `photo_local_path` (TEXT): Ruta local de la foto descargada
- `last_updated` (TEXT): Última actualización

**Uso**: Catálogo completo de jugadores, análisis de rendimiento, gestión de fotos

---

#### 3. **`transactions`** - Transacciones de mercado
- `id` (INTEGER, PRIMARY KEY): ID único de la transacción
- `player_id` (TEXT): ID del jugador
- `seller_user_id` (TEXT): ID del usuario vendedor
- `buyer_user_id` (TEXT): ID del usuario comprador
- `seller_team_id` (TEXT): ID del equipo vendedor
- `buyer_team_id` (TEXT): ID del equipo comprador
- `price` (INTEGER): Precio de la transacción
- `date` (TEXT): Fecha de la transacción
- `transaction_type` (TEXT): Tipo ("TRADE")

**Uso**: Análisis de beneficios, seguimiento de mercado, cálculo de ganancias

---

#### 4. **`teams`** - Equipos extendidos
- `team_id` (TEXT, PRIMARY KEY): ID del equipo
- `user_id` (TEXT): ID del usuario propietario
- `team_name` (TEXT): Nombre del equipo
- `owner_name` (TEXT): Nombre del propietario
- `current_points` (INTEGER): Puntos actuales
- `team_value` (INTEGER): Valor del equipo
- `last_access` (TEXT): Último acceso
- `is_admin` (BOOLEAN): Es administrador
- `initial_budget` (INTEGER): Presupuesto inicial (270M)
- `last_updated` (TEXT): Última actualización

**Uso**: Gestión de equipos, análisis financiero, estadísticas de equipos

---

### Tablas de Datos Temporales (Jornada a Jornada)

#### 5. **`team_matchday_data`** - Datos históricos por jornada
- `id` (INTEGER, PRIMARY KEY)
- `matchday` (INTEGER): Número de jornada
- `team_id` (TEXT): ID del equipo
- `points` (INTEGER): Puntos acumulados
- `position` (INTEGER): Posición en el ranking
- `points_this_matchday` (INTEGER): Puntos de esta jornada
- `best_player_id` (TEXT): Mejor jugador de la jornada
- `best_player_points` (INTEGER): Puntos del mejor jugador
- `saved_at` (TEXT): Fecha de guardado

**Uso**: Evolución jornada a jornada, análisis de tendencias, gráficos de evolución

---

#### 6. **`player_matchday_performance`** - Rendimiento por jugador y jornada
- `id` (INTEGER, PRIMARY KEY)
- `player_id` (TEXT): ID del jugador
- `team_id` (TEXT): ID del equipo que lo tiene
- `matchday` (INTEGER): Número de jornada
- `points` (INTEGER): Puntos en esa jornada
- `value` (INTEGER): Valor en esa jornada
- `was_best_player` (BOOLEAN): Fue mejor jugador
- `saved_at` (TEXT): Fecha de guardado

**Uso**: Análisis de rendimiento individual, mejores jugadores por jornada

---

#### 7. **`round_rankings`** - Rankings por jornada 🆕
- `id` (INTEGER, PRIMARY KEY)
- `round` (INTEGER): Número de jornada
- `championship_id` (TEXT): ID del campeonato
- `team_id` (TEXT): ID del equipo
- `position` (INTEGER): Posición en el ranking
- `points` (INTEGER): Puntos acumulados
- `previous_position` (INTEGER): Posición anterior
- `position_change` (INTEGER): Cambio de posición (+ = sube, - = baja)
- `saved_at` (TEXT): Fecha de guardado

**Uso**: Análisis de evolución de posiciones, equipos con mayor ascenso/descenso, tendencias

---

#### 8. **`player_matchday_stats`** - Estadísticas detalladas por jornada 🆕
- `id` (INTEGER, PRIMARY KEY)
- `player_id` (TEXT): ID del jugador
- `team_id` (TEXT): ID del equipo
- `matchday` (INTEGER): Número de jornada
- `championship_id` (TEXT): ID del campeonato
- `points` (INTEGER): Puntos en esa jornada
- `value` (INTEGER): Valor en esa jornada
- `performance_data` (TEXT): Datos de rendimiento (JSON)
- `saved_at` (TEXT): Fecha de guardado

**Uso**: Análisis detallado de rendimiento, estadísticas avanzadas, comparativas

---

### Tablas de Datos de Mercado y Noticias

#### 9. **`market_players`** - Jugadores en el mercado 🆕
- `id` (INTEGER, PRIMARY KEY)
- `player_id` (TEXT): ID del jugador
- `championship_id` (TEXT): ID del campeonato
- `market_price` (INTEGER): Precio en el mercado
- `availability` (TEXT): Disponibilidad
- `market_statistics` (TEXT): Estadísticas de mercado (JSON)
- `saved_at` (TEXT): Fecha de guardado
- `last_updated` (TEXT): Última actualización

**Uso**: Análisis de mercado, valores actuales, jugadores disponibles, oportunidades

---

#### 10. **`pressroom_news`** - Noticias y actualizaciones 🆕
- `id` (TEXT, PRIMARY KEY): ID único de la noticia
- `championship_id` (TEXT): ID del campeonato
- `title` (TEXT): Título de la noticia
- `content` (TEXT): Contenido de la noticia
- `news_date` (TEXT): Fecha de la noticia
- `news_type` (TEXT): Tipo de noticia
- `related_teams` (TEXT): Equipos relacionados (JSON)
- `related_players` (TEXT): Jugadores relacionados (JSON)
- `image_url` (TEXT): URL de imagen
- `saved_at` (TEXT): Fecha de guardado

**Uso**: Timeline de eventos, correlación noticias-rendimiento, contexto histórico

---

#### 11. **`team_rosters`** - Rosters detallados por equipo 🆕
- `id` (INTEGER, PRIMARY KEY)
- `team_id` (TEXT): ID del equipo
- `player_id` (TEXT): ID del jugador
- `championship_id` (TEXT): ID del campeonato
- `formation_position` (TEXT): Posición en la formación
- `is_starter` (BOOLEAN): Es titular
- `lineup_order` (INTEGER): Orden en el once
- `saved_at` (TEXT): Fecha de guardado
- `last_updated` (TEXT): Última actualización

**Uso**: Análisis de formaciones, mejores combinaciones, estrategias de equipo

---

### Tablas de Soporte

#### 12. **`user_profits`** - Análisis de beneficios por usuario
- `user_id` (TEXT, PRIMARY KEY)
- `username` (TEXT): Nombre de usuario
- `team_id` (TEXT): ID del equipo
- `team_name` (TEXT): Nombre del equipo
- `total_profit` (REAL): Beneficio total
- `total_transactions` (INTEGER): Total de transacciones
- `successful_trades` (INTEGER): Transacciones exitosas
- `failed_trades` (INTEGER): Transacciones fallidas
- `best_profit` (REAL): Mejor beneficio
- `worst_loss` (REAL): Peor pérdida
- `avg_profit_per_trade` (REAL): Promedio por transacción
- `profit_percentage` (REAL): Porcentaje de beneficio
- `last_updated` (TEXT): Última actualización

**Uso**: Rankings de beneficios, análisis de gestión, comparativas

---

#### 13. **`player_photos`** - Gestión de fotos de jugadores
- `player_id` (TEXT, PRIMARY KEY)
- `photo_url` (TEXT): URL original de la foto
- `local_path` (TEXT): Ruta local de la foto descargada
- `downloaded_at` (TEXT): Fecha de descarga
- `file_size` (INTEGER): Tamaño del archivo
- `file_hash` (TEXT): Hash del archivo
- `last_checked` (TEXT): Última verificación

**Uso**: Servicio de fotos local, optimización de carga, cacheo

---

#### 14. **`cache_metadata`** - Metadatos de caché
- `data_type` (TEXT, PRIMARY KEY): Tipo de dato
- `last_updated` (TEXT): Última actualización
- `expires_at` (TEXT): Fecha de expiración
- `next_update_scheduled` (TEXT): Próxima actualización programada

**Uso**: Control de actualizaciones diarias, validación de caché

---

## 📊 Índices para Optimización

### Índices Creados:
- `idx_team_matchday_data_matchday`: Búsqueda por jornada
- `idx_team_matchday_data_team`: Búsqueda por equipo
- `idx_player_matchday_performance_matchday`: Rendimiento por jornada
- `idx_player_matchday_performance_team`: Rendimiento por equipo
- `idx_player_matchday_performance_player`: Rendimiento por jugador
- `idx_round_rankings_round`: Rankings por jornada
- `idx_round_rankings_team`: Rankings por equipo
- `idx_market_players_player`: Mercado por jugador
- `idx_market_players_championship`: Mercado por campeonato
- `idx_pressroom_news_championship`: Noticias por campeonato
- `idx_pressroom_news_date`: Noticias por fecha
- `idx_team_rosters_team`: Rosters por equipo
- `idx_team_rosters_player`: Rosters por jugador
- `idx_player_matchday_stats_matchday`: Estadísticas por jornada
- `idx_player_matchday_stats_player`: Estadísticas por jugador
- `idx_player_matchday_stats_team`: Estadísticas por equipo

---

## 🔄 Actualización Diaria

### Estrategia de Caché

El sistema utiliza un mecanismo de caché diario que:

1. **Actualiza datos una vez al día**: Los datos se actualizan automáticamente cada 24 horas
2. **Validación de caché**: El sistema verifica si los datos están vencidos antes de hacer nuevas peticiones
3. **Programación flexible**: Se puede programar la próxima actualización según necesidades

### Tipos de Datos con Caché:
- `players`: Jugadores del campeonato
- `user_profits`: Análisis de beneficios
- `matchday_evolution`: Evolución jornada a jornada
- `round_rankings`: Rankings por jornada
- `market_players`: Jugadores del mercado
- `pressroom_news`: Noticias
- `team_rosters`: Rosters de equipos

### Métodos de Actualización:

```python
# Verificar si necesita actualización
data_manager.should_update_cache("round_rankings")

# Actualizar datos
data_manager.save_round_ranking(round_number, championship_id, teams_data)
data_manager.update_cache_metadata("round_rankings")
```

---

## 📈 Análisis Estadísticos Posibles

### Con `round_rankings`:
- ✅ Evolución de posiciones jornada a jornada
- ✅ Equipos con mayor ascenso/descenso
- ✅ Análisis de tendencias en el ranking
- ✅ Predicción de posiciones finales
- ✅ Equipos más consistentes (menos variación de posición)

### Con `market_players`:
- ✅ Análisis de valores de mercado
- ✅ Jugadores más demandados
- ✅ Oportunidades de inversión
- ✅ Comparación de precios vs rendimiento
- ✅ Evolución de precios de mercado

### Con `pressroom_news`:
- ✅ Timeline de eventos del campeonato
- ✅ Correlación entre noticias y rendimiento
- ✅ Análisis de contexto histórico
- ✅ Eventos relevantes por jornada

### Con `team_rosters`:
- ✅ Análisis de formaciones más efectivas
- ✅ Mejores combinaciones de jugadores
- ✅ Rendimiento por posición
- ✅ Estrategias de equipo
- ✅ Comparativa de formaciones

### Con `player_matchday_stats`:
- ✅ Rendimiento detallado por jugador
- ✅ Estadísticas avanzadas por jornada
- ✅ Comparativas de jugadores
- ✅ Mejor jugador por jornada
- ✅ Análisis de rendimiento temporal

---

## 🔌 Integración con API

### Endpoints Implementados:

1. **`/1/ranking/round`**: Rankings por jornada
2. **`/1/userteam/roster`**: Rosters detallados
3. **`/1/market/players`**: Jugadores del mercado
4. **`/1/locker/pressroom`**: Noticias y actualizaciones
5. **`/1/player/summary`**: Resumen detallado de jugador (ya existente)

### Métodos en `futmondo_client.py`:

- `get_round_ranking(championship_id, round_number)` → `round_rankings`
- `get_userteam_roster(championship_id, team_id)` → `team_rosters`
- `get_market_players(championship_id)` → `market_players`
- `get_pressroom_news(championship_id)` → `pressroom_news`
- `get_player_summary(championship_id, player_id, team_id)` → `player_matchday_stats`

### Métodos en `data_manager.py`:

- `save_round_ranking(round_number, championship_id, teams)` → Guarda ranking
- `get_round_ranking(round_number, championship_id)` → Obtiene ranking
- `save_market_players(championship_id, players)` → Guarda mercado
- `get_market_players(championship_id)` → Obtiene mercado
- `save_pressroom_news(championship_id, news_items)` → Guarda noticias
- `get_pressroom_news(championship_id, limit)` → Obtiene noticias
- `save_team_roster(team_id, championship_id, players)` → Guarda roster
- `get_team_roster(team_id, championship_id)` → Obtiene roster
- `save_player_matchday_stats(...)` → Guarda estadísticas
- `get_player_matchday_stats(...)` → Obtiene estadísticas

---

## 🚀 Próximos Pasos

### Servicios de Actualización Diaria:

1. **Crear servicio de actualización automática**:
   - Verificar qué datos necesitan actualización
   - Actualizar solo los datos vencidos
   - Programar actualizaciones diarias

2. **Endpoints API para nuevos datos**:
   - `/api/v1/rankings/{round}`: Ranking por jornada
   - `/api/v1/market/players`: Jugadores del mercado
   - `/api/v1/pressroom/news`: Noticias recientes
   - `/api/v1/teams/{team_id}/roster`: Roster de equipo

3. **Análisis estadísticos**:
   - Crear módulos de análisis para cada tipo de dato
   - Generar insights automáticos
   - Visualizaciones avanzadas

---

## 📝 Notas de Implementación

1. **Compatibilidad**: Todas las tablas nuevas son compatibles con la estructura existente
2. **Migraciones**: Las nuevas columnas se añaden con `ALTER TABLE IF NOT EXISTS` para evitar errores
3. **Índices**: Todos los índices están optimizados para consultas frecuentes
4. **Caché**: El sistema de caché diario está implementado y funcionando
5. **Fotos**: Sistema completo de descarga y gestión de fotos implementado

---

## 🔍 Consultas Útiles

### Obtener evolución de posición de un equipo:
```sql
SELECT round, position, points, position_change 
FROM round_rankings 
WHERE team_id = ? 
ORDER BY round ASC
```

### Obtener mejores jugadores del mercado:
```sql
SELECT p.name, mp.market_price, mp.availability 
FROM market_players mp
JOIN players p ON mp.player_id = p.id
ORDER BY mp.market_price DESC
LIMIT 10
```

### Obtener noticias recientes:
```sql
SELECT title, news_date, news_type 
FROM pressroom_news 
WHERE championship_id = ?
ORDER BY news_date DESC 
LIMIT 20
```

### Análisis de rendimiento por jugador:
```sql
SELECT matchday, points, value 
FROM player_matchday_stats 
WHERE player_id = ? 
ORDER BY matchday ASC
```

---

**Última actualización**: 2025-01-XX  
**Versión**: 2.0.0
