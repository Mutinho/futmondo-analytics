# Visión de Negocio — Futmondo Analytics

> Artefacto de reverse-engineering (escaneo FULL, primera vez, profundidad
> Standard, proyecto brownfield). Basado en el handoff del developer y en la
> lectura del código fuente real. Repo raíz: `/home/javi/futmondo-analytics`.

## Dominio y propósito

Futmondo Analytics es una aplicación web multi-usuario (PWA) que gestiona y
analiza campeonatos de **Futmondo** (fantasy football). El dominio de negocio es
el análisis financiero y de mercado de una liga fantasy: cada usuario opera sobre
sus propios campeonatos y obtiene visibilidad de presupuestos, mercado de
jugadores, finanzas por participante y evolución a lo largo de la temporada.

El sistema no es un juego en sí: es una capa analítica **sobre** la plataforma
Futmondo. Se autentica con las credenciales Futmondo del propio usuario, valida
esas credenciales contra la API oficial de Futmondo y, a partir de ahí, sincroniza
y enriquece los datos del campeonato (transacciones, cláusulas, plantillas,
clasificaciones, premios) para presentarlos como analítica accionable en un
frontend instalable como app en iPhone.

Los datos del campeonato (transacciones, jugadores, standings) se comparten entre
los usuarios de un mismo campeonato; las credenciales y la sesión Futmondo son
individuales de cada usuario — no existen credenciales globales.

## Funcionalidad clave

- **Presupuesto**: saldos por equipo con detalle de altas/bajas, puja máxima y
  rendimiento.
- **Mercado**: jugadores del "computer" en venta con puja sugerida (derivada del
  histórico real de sobrepago vía `transactions.market_value_at_purchase` en
  `market.py::_calculate_suggested_bid`), rating de Sofascore y tendencia. Incluye
  puja real proxeada a Futmondo (`market.py::place_bid`).
- **Sincronización asíncrona (11 pasos)**: sync en background con progreso paso a
  paso (players, transactions, clauses, punishments_bonuses, dream_teams,
  player_performance, rosters, team_standings, match_odds, prizes, phantoms). Es
  la transacción de negocio más pesada del sistema.
- **Finanzas por usuario**: cálculo de dinero por participante (presupuesto +
  puntos×€ + profit de transacciones + dream team + MVP + clasificación con la
  fórmula proporcional de Futmondo + castigos/bonificaciones).
- **Evolución, Estadísticas, Clausulables, Analytics, Phantoms**: gráficos e
  informes derivados; detección de "phantom players" (jugadores en plantilla sin
  compra registrada).
- **Asistente IA**: chat conversacional (Gemini con fallback Groq) con
  persistencia de conversaciones.
- **PWA + Dark Mode**: service worker, manifest, meta tags Apple; tema oscuro
  persistido en `localStorage`.

## Actores y flujos de valor

- **Usuario final** (participante de la liga): se autentica, dispara syncs,
  consulta finanzas/mercado y realiza pujas desde el iPhone/navegador.
- **Cron programado** (`futmondo-cron`, `backend/scripts/sync_data.py`): job
  one-shot multi-championship que refresca datos sin intervención del usuario.
- **Cron Sofascore** (`sofascore-sync.yml`): refresca la caché de ratings
  Sofascore, con tolerancia al baneo de IP (exit code 2).

El valor de negocio es convertir los datos crudos de Futmondo en decisiones:
cuánto pujar, quién sobra financieramente, cómo evoluciona cada equipo y dónde
hay margen de mejora en la liga.

## Restricciones de negocio relevantes

- **Coste 0€** es una regla de proyecto vigente (`project.md`): toda mejora debe
  sostenerse en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions
  free). Esto condiciona la infraestructura (Fly `min_machines_running=1`, crons
  one-shot) y descarta dependencias con gasto recurrente.
- **Dependencia de APIs de terceros**: Futmondo (oficial) y Sofascore (no
  oficial, con riesgo de baneo de IP). La disponibilidad del análisis depende de
  la disponibilidad de esas APIs externas.
