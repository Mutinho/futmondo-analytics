# 📡 Resumen de APIs Futmondo Disponibles

## 🔐 Autenticación

### `/5/login/with_mail` (POST)
- **Descripción**: Login con email y contraseña
- **Parámetros**: `mail`, `pwd`
- **Respuesta**: Token y user_id para autenticación
- **Estado**: ✅ Implementado y funcionando
- **Uso**: Auto-login en startup

## 🏆 Campeonato

### `/2/championship/teams` (POST)
- **Descripción**: Clasificación/standings del campeonato
- **Parámetros**: `championshipId`, `matchday` (opcional)
- **Respuesta**: Lista de equipos con puntos, posición actual
- **Estado**: ✅ Implementado
- **Problema**: Solo devuelve datos de la jornada actual/cumulativos, no históricos por jornada

### `/1/ranking/round` (POST) 🆕
- **Descripción**: Ranking completo por jornada del campeonato
- **Parámetros**: `championshipId`, `round` (número de jornada)
- **Respuesta**: Ranking completo con equipos ordenados por puntos acumulados en esa jornada
- **Estructura**:
  - Lista de equipos con posición, puntos, cambios de posición
  - Datos estadísticos del ranking
- **Estado**: ⚠️ Pendiente de implementar
- **Uso**: Análisis de evolución del ranking jornada a jornada, cambios de posición

### `/1/userteam/rounds` (POST)
- **Descripción**: Puntos por jornada de un equipo específico
- **Parámetros**: `championshipId`, `userteamId`
- **Respuesta**: Lista de rounds con:
  - `id`: ID del round
  - `number`: Número de jornada
  - `status`: 'closed' o 'running'
  - `points`: Puntos de esa jornada
  - `negative`: Boolean
- **Estado**: ✅ Implementado
- **Uso**: **PRINCIPAL** para evolución jornada a jornada

## 👥 Jugadores

### `/5/league/championshipplayers` (POST)
- **Descripción**: Todos los jugadores del campeonato
- **Parámetros**: `championshipId`
- **Respuesta**: Lista de jugadores con:
  - `id`, `name`, `role`, `team`, `value`, `points`
  - `userteamId`, `userteam` (equipo que lo tiene)
  - `average`: Estadísticas promedio
  - `photo`: URL de foto (si disponible)
- **Estado**: ✅ Implementado
- **Nota**: Puede incluir URLs de fotos

### `/1/player/summary` (POST)
- **Descripción**: Resumen detallado de un jugador
- **Parámetros**: `championshipId`, `userteamId`, `playerId`
- **Respuesta**: Información detallada del jugador incluyendo:
  - Datos del jugador (nombre, equipo, posición, valor, puntos)
  - **Historial de transacciones** (compras/ventas) - `owners` array
  - Estadísticas detalladas por jornada
  - Historial de puntos por jornada
  - Foto del jugador
- **Estado**: ✅ Implementado
- **Uso**: Análisis de transacciones y beneficios, estadísticas detalladas

### `/1/market/players` (POST) 🆕
- **Descripción**: Jugadores disponibles en el mercado de transferencias
- **Parámetros**: `championshipId`, posiblemente filtros adicionales
- **Respuesta**: Lista de jugadores disponibles para compra/venta con:
  - Datos del jugador
  - Precio de mercado
  - Estadísticas de mercado
  - Disponibilidad
- **Estado**: ⚠️ Pendiente de implementar
- **Uso**: Análisis de mercado, valores actuales, jugadores disponibles

## ⚽ Equipos

### `/1/userteam/roster` (POST) 🆕
- **Descripción**: Plantilla/roster completo de un equipo
- **Parámetros**: `championshipId`, `userteamId`
- **Respuesta**: Lista detallada de jugadores en el equipo con:
  - `id`, `name`, `role`, `team`, `value`, `points`
  - `photo`: URL de foto del jugador
  - Posición en el equipo (formación)
  - Estadísticas individuales
- **Estado**: ⚠️ Pendiente de implementar correctamente
- **Uso**: Ver plantilla actual de un equipo, mejores jugadores, análisis de equipo

### `/1/userteam/nightmareteam` (POST)
- **Descripción**: Peor equipo de la jornada/campeonato
- **Parámetros**: `championshipId`, `matchday` (opcional)
- **Respuesta**: Equipo con peores puntuaciones
- **Estado**: ✅ Implementado

### `/1/userteam/dreamteam` (POST)
- **Descripción**: Mejor equipo de la jornada/campeonato
- **Parámetros**: `championshipId`, `matchday` (opcional)
- **Respuesta**: Equipo con mejores puntuaciones
- **Estado**: ✅ Implementado

## 📅 Partidos

### `/1/match/list` (POST)
- **Descripción**: Lista de partidos del campeonato
- **Parámetros**: `championshipId`, `matchday` (opcional)
- **Respuesta**: Lista de partidos con equipos, resultados, fechas
- **Estado**: ✅ Implementado

## 📰 Noticias y Prensa

### `/1/locker/pressroom` (POST) 🆕
- **Descripción**: Noticias y actualizaciones del campeonato
- **Parámetros**: `championshipId`, posiblemente filtros por fecha/tipo
- **Respuesta**: Lista de noticias/actualizaciones con:
  - Título, contenido, fecha
  - Tipo de noticia
  - Referencias a equipos/jugadores
  - Imágenes relacionadas
- **Estado**: ⚠️ Pendiente de implementar
- **Uso**: Actualizaciones del campeonato, noticias relevantes, historial de eventos

---

## 📊 Datos Disponibles vs Necesarios

### ✅ Tenemos Implementado:
- ✅ Autenticación y tokens
- ✅ Clasificación general del campeonato
- ✅ Puntos acumulados por equipo por jornada
- ✅ Posiciones por jornada (calculables desde puntos)
- ✅ Lista completa de jugadores del campeonato
- ✅ Resumen detallado de jugadores con transacciones
- ✅ Transacciones por jugador (historial completo)
- ✅ Mejor/peor equipo por jornada
- ✅ Lista de partidos
- ✅ Fotos de jugadores (descarga y almacenamiento local)

### ⚠️ Pendiente de Implementar:
- ⚠️ **Ranking por jornada** (`/1/ranking/round`): Cambios de posición jornada a jornada
- ⚠️ **Roster detallado** (`/1/userteam/roster`): Plantilla completa con fotos y estadísticas
- ⚠️ **Jugadores del mercado** (`/1/market/players`): Análisis de mercado y valores
- ⚠️ **Prensa/noticias** (`/1/locker/pressroom`): Actualizaciones y noticias del campeonato

### 💡 Oportunidades de Análisis Estadístico:

#### Con `/1/ranking/round`:
- Evolución de posiciones jornada a jornada
- Equipos con mayor ascenso/descenso
- Análisis de tendencias en el ranking
- Predicción de posiciones finales

#### Con `/1/market/players`:
- Análisis de valores de mercado
- Jugadores más demandados
- Oportunidades de inversión
- Comparación de precios vs rendimiento

#### Con `/1/locker/pressroom`:
- Timeline de eventos del campeonato
- Correlación entre noticias y rendimiento
- Análisis de contexto histórico

#### Con `/1/userteam/roster` mejorado:
- Análisis de formaciones más efectivas
- Mejores combinaciones de jugadores
- Rendimiento por posición
- Estrategias de equipo

---

## 🏗️ Arquitectura de Datos Propuesta

### Tablas Nuevas Necesarias:

1. **`round_rankings`**: Rankings por jornada
   - `round` (jornada), `team_id`, `position`, `points`, `previous_position`, `position_change`
   
2. **`market_players`**: Jugadores en el mercado
   - `player_id`, `market_price`, `availability`, `last_updated`
   
3. **`pressroom_news`**: Noticias y actualizaciones
   - `id`, `title`, `content`, `date`, `type`, `championship_id`, `related_teams`, `related_players`
   
4. **`team_rosters`**: Rosters detallados por equipo
   - `team_id`, `player_id`, `formation_position`, `is_starter`, `last_updated`
   
5. **`player_matchday_stats`**: Estadísticas detalladas por jugador y jornada
   - `player_id`, `team_id`, `matchday`, `points`, `value`, `performance_data` (JSON)

### Optimizaciones:
- **Índices**: En `matchday`, `team_id`, `player_id` para consultas rápidas
- **Cache diario**: Actualizar datos una vez al día automáticamente
- **Historial completo**: Mantener todos los datos históricos para análisis temporal

---

## 📝 Notas de Implementación

1. **Fotos de jugadores**: Ya implementado - se descargan automáticamente y se almacenan localmente
2. **Caching diario**: Sistema implementado con `cache_metadata` y `next_update_scheduled`
3. **Transacciones**: Sistema completo de tracking con usuarios, precios, fechas
4. **Evolución jornada a jornada**: Funcionalidad completa para puntos y posiciones

### Próximos Pasos:
1. ✅ Actualizar resumen de APIs
2. ⚠️ Implementar nuevos endpoints en `futmondo_client.py`
3. ⚠️ Extender `data_manager.py` con nuevas tablas
4. ⚠️ Crear servicios de actualización diaria
5. ⚠️ Implementar endpoints API para nuevos datos

