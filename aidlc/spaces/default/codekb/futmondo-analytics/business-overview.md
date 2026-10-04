# Business Overview

## Dominio de negocio

**Futmondo Analytics** es una aplicación web multi-usuario (PWA) para gestionar y
analizar campeonatos de *Futmondo* (fantasy football). El dominio es la analítica
de un juego de fantasy football: presupuestos por equipo, mercado de jugadores,
finanzas, premios por jornada, y ratings deportivos externos (Sofascore). Es un
sistema **brownfield en producción** sobre Fly.io + Neon PostgreSQL.

## Propósito

Dar a cada usuario una visión analítica de sus campeonatos de Futmondo desde el
móvil (PWA instalable en iPhone): controlar el presupuesto, analizar el mercado,
calcular las finanzas de cada participante y decidir pujas con datos objetivos
(historial de pujas + rating Sofascore).

## Funcionalidad clave

- **Autenticación**: el usuario entra con sus credenciales de Futmondo; el backend
  valida contra la API de Futmondo y emite JWT (access en memoria + refresh en
  cookie HttpOnly). Sesión de Futmondo por usuario (12h TTL, re-auth automática).
- **Multi-usuario**: campeonatos auto-detectados al primer login; los datos del
  campeonato (transacciones, jugadores, standings) se comparten entre usuarios.
- **Presupuesto**: saldos por equipo con altas/bajas, puja máxima y rendimiento.
- **Mercado**: jugadores del computer con puja sugerida, rating Sofascore y
  tendencia; modal de puja con min/max validados.
- **Sincronización asíncrona (dominio central de este intent)**: sync en background
  con progreso paso a paso que ingesta jugadores, transacciones, cláusulas,
  castigos, dream teams, rendimiento, plantillas, clasificación, odds y sofascore
  desde las integraciones externas hacia Neon. Coordinada por `DataSyncService`
  (10 operaciones `sync_*` + `sync_all()`). Cada dominio produce un `SyncResult`
  observable cuya forma **no es uniforme** entre dominios (ver `api-documentation.md`
  y `architecture.md` para la superficie y el flujo).
- **Finanzas**: cálculo de dinero por usuario (presupuesto + puntos×€ + profit de
  transacciones + dream team + MVP + clasificación con fórmula proporcional +
  castigos/bonificaciones).
- **Premios (`prizes`)**: cálculo puro de premios por jornada (`calculator.py`) y
  persistencia atómica del conjunto (`team_prizes_writer.replace_team_prizes`,
  patrón de referencia del dominio, ver `component-inventory.md`).
- **Analítica y asistente**: evolución, estadísticas, clausulables y un asistente
  (contextos DDD `analytics/` y `assistant/`).

## Contexto del intent activo (`261002-sync-god-file-8`)

El intent es un **refactor** (continuación de `260929-sync-god-file` y
`261001-sync-god-file-resto`): descomponer los **8 dominios de sync que SIGUEN
inline** en `data_sync_service.py` (~77 KB / ~1806 líneas) al patrón DDD ya
**probado por DOS pilotos** (`match_odds` y `clauses`), y uniformar `sync_prizes`
(cuya lógica pura y escritor atómico ya viven en `prizes/`) al patrón de facade.
Dominios restantes a extraer (orden propuesto de menor a mayor acoplamiento):
`transactions`, `punishments_bonuses`, `dream_teams_mvps`, `rosters`,
`round_rankings` (clave literal `team_standings`), `player_performance`,
`players_full`; más la uniformización de `sync_prizes`. El contrato público (los
10 `sync_*` + `sync_all()` con sus 10 claves literales y orden fijo) se preserva
byte-a-byte (FR5), sin ampliar los god-files ni relajar el piso de cobertura, con
**characterization-first estricto por dominio** y una unidad de trabajo por
dominio (gate por unidad). La deuda técnica y el patrón objetivo se documentan en
`code-quality-assessment.md` y `code-structure.md`.
