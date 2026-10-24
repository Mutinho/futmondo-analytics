# Business Overview — Futmondo Analytics

> Merge CURRENT (store `261023-latencia-market-favorito`). Prosa previa
> **preservada**; refresco enfocado en el **sync completo de jugadores** (intent
> `261023-sync-jugador-completo`): persistir toda la info por jugador para que
> Favoritos y Mercado se sirvan desde el sync sin depender de `market_today` ni
> de llamadas en vivo. Conciso por profundidad Minimal.

## Dominio

Aplicación web multi-usuario (PWA, instalable en iPhone) para gestionar y
analizar campeonatos de **Futmondo** (fantasy football de LaLiga). Permite
controlar presupuestos, analizar el mercado, obtener ratings de Sofascore, pujar
por jugadores, gestionar favoritos y calcular finanzas. En producción en Fly.io
(París) con base de datos Neon PostgreSQL (Frankfurt).

## Funcionalidad clave (relevante a este intent)

- **Mercado** (`/market/today`): jugadores del computer disponibles hoy con puja
  sugerida (calculada por % de sobrepago histórico desde `transactions`), rating
  Sofascore y % titularidad. Lee caché `market_today` + pujas del usuario en
  vivo.
- **Favoritos** (`/favorites/my`): jugadores marcados como favoritos (agentes
  libres) enriquecidos con valor/stats y Sofascore.
- **Sincronización** (`sync_players_full` y hermanos): sync en background (11
  pasos) que pre-sincroniza datos de Futmondo a Neon (jugadores, transacciones,
  standings, premios, performance, sofascore…).
- **Presupuesto / Balances** (`/analytics/balances`): saldo por equipo
  (200M − compras + ventas + premios), valor de plantilla y rendimiento.

## Problema de negocio que motiva el intent

Favoritos y Mercado deben mostrar por cada jugador **todos** los campos del
contrato (puntos totales, `change`/tendencia, logo de equipo, medias
casa/fuera, partidos), pero hoy esos campos solo existen para una minoría de
jugadores: `points` vive en `player_performance` (vacío para agentes libres) y
`change`/medias-detalle/`team_logo` solo en `market_today` (~30 jugadores del
día). En producción, 32 de 33 favoritos agentes libres salen con esos campos
vacíos. El objetivo del intent es **enriquecer el sync de jugadores**
(`sync_players_full`) para que persista la info completa por jugador en las
tablas sincronizadas, de modo que Favoritos y Mercado sirvan cada campo desde el
sync, sin `market_today` ni llamadas en vivo.

## Usuarios

Cada usuario se autentica con sus credenciales de Futmondo; sus campeonatos se
auto-detectan al primer login. Los datos del campeonato (transacciones,
jugadores, standings) se comparten entre usuarios del mismo campeonato; las
pujas y favoritos son por usuario.

## Restricciones de negocio durables

- **Coste 0 €**: solo tiers gratuitos (Neon free, Fly.io free, GitHub Actions
  free). Excepción acotada: publicación de distribución nativa.
- Gate de CI bloqueante antes de fusionar a `main`.
- Nunca almacenar la contraseña Futmondo en claro.
- Characterization-first antes de refactorizar `sync_players_full`; no ampliar
  los god-files ni el SQL-en-router; contrato de respuesta de los endpoints
  intacto.
