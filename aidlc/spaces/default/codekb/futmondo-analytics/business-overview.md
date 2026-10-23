# Business Overview — Futmondo Analytics

> Refresco enfocado en **latencia** (intent `261023-latencia-market-favorito`)
> sobre store CURRENT (`261020-mercado-pujas`). Prosa previa preservada y
> extendida con la caracterización de rendimiento de 3 endpoints. Conciso por
> profundidad Minimal; cada inventario se registra una vez y se cruza-referencia.

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
- **Presupuesto / Balances** (`/analytics/balances`): saldo por equipo
  (200M − compras + ventas + premios), valor de plantilla y rendimiento.
- **Sincronización**: sync en background (11 pasos) que pre-sincroniza datos de
  Futmondo a Neon (jugadores, transacciones, standings, premios, sofascore…).

## Problema de negocio que motiva el intent

El usuario percibe lentitud al abrir **Mercado** (~1.6 s) y **Favoritos**
(~3.4 s), mientras **Presupuesto** carga rápido (~0.4 s). El objetivo es entender
y reducir esa latencia preservando el contrato de datos de cada pantalla. La
causa raíz es el número de **llamadas HTTP en vivo a la API de Futmondo por
petición** (ver `architecture.md` → Interaction Diagrams y
`code-quality-assessment.md`).

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
