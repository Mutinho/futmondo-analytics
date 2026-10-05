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
- **Sincronización asíncrona**: sync en background con progreso paso a paso que
  ingesta jugadores, transacciones, cláusulas, castigos, dream teams, rendimiento,
  plantillas, clasificación, odds y sofascore desde las integraciones externas
  hacia Neon. Coordinada por `DataSyncService`. El detalle del dominio sync vive en
  los artefactos del store previo (prosa preservada); esta pasada focaliza la
  **capa de acceso a datos** que todos esos dominios consumen.
- **Finanzas**: cálculo de dinero por usuario (presupuesto + puntos×€ + profit de
  transacciones + dream team + MVP + clasificación con fórmula proporcional +
  castigos/bonificaciones).
- **Premios (`prizes`)**: cálculo puro de premios por jornada (`calculator.py`) y
  persistencia atómica del conjunto (`team_prizes_writer.replace_team_prizes`,
  patrón de referencia del dominio, ver `component-inventory.md`).
- **Analítica y asistente**: evolución, estadísticas, clausulables y un asistente
  (contextos DDD `analytics/` y `assistant/`).

## Acceso a datos como capacidad transversal (foco de esta pasada)

Toda la funcionalidad anterior (sync, finanzas, premios, analítica, asistente,
estadísticas) comparte una **única capa de acceso a datos**: la clase
`DataManagerV2` (`backend/app/services/data_manager_v2.py`). Según el handoff del
desarrollador, concentra la persistencia y lectura históricas sobre
PostgreSQL/Neon en 57 métodos públicos (19 `save_*`, 26 `get_*`, 6 privados `_*`)
que cubren ~14 responsabilidades de negocio: players, teams/standings,
performance, transactions, clauses, punishments/bonuses, dream-teams/MVP, prizes,
market/roster, match-odds, news/articles, users/stats/evolution,
sync-metadata/cache y schema/lifecycle. Es la fuente de verdad de lectura y
escritura del campeonato: cualquier dato que el usuario ve en la PWA pasó por uno
de sus `get_*`, y cualquier ingesta de las integraciones externas se materializó
en Neon por uno de sus `save_*`.

## Contexto del intent activo (`261005-data-manager-god-file`)

El intent es un **refactor** (continuación de las oleadas de `sync` y `assistant`):
descomponer el **último god-file original sin tocar**, `data_manager_v2.py` (~162
KB / 3692 líneas, clase única `DataManagerV2`), al patrón DDD ya probado en el
mismo repo (facade delgado → orchestrator → domain/ports `Protocol`
consumer-owned sin SQL + `infrastructure/*_adapter` que envuelve el SQL verbatim;
reemplazo de conjunto atómico). El objetivo es **preservar la superficie pública
exacta** (constructor `skip_init=True`, nombres y firmas de los 57 métodos) porque
8 routers + los adapters de las 4 oleadas DDD la envuelven verbatim, con
**characterization-first estricto por responsabilidad** y sin ampliar god-files ni
el patrón SQL-en-router. La deuda técnica y el patrón objetivo se documentan en
`code-quality-assessment.md`, `architecture.md` y `code-structure.md`.
