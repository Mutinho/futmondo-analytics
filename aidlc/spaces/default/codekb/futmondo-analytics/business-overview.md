# Business Overview — futmondo-analytics

## Dominio de negocio

`futmondo-analytics` es una aplicación web multi-usuario para gestionar y
analizar campeonatos de **Futmondo** (fantasy football). Es un sistema
brownfield **en producción** (Fly.io, región `cdg`) desplegado como dos apps:
backend `futmondo-api` (FastAPI, Python 3.12) y frontend `futmondo-app`
(Angular 22 PWA), con base de datos **Neon PostgreSQL** (Frankfurt, tier free).

El propósito es dar a cada usuario visibilidad y analítica sobre sus
campeonatos de Futmondo: presupuestos por equipo, mercado con puja sugerida,
ratings de Sofascore, finanzas por usuario, evolución/estadísticas y un
asistente conversacional con IA. Restricción de negocio dura: **coste 0 €**
(solo tiers gratuitos).

## Modelo multi-usuario

- Cada usuario se autentica con sus credenciales **Futmondo** (email/password);
  el backend valida contra la API de Futmondo y emite JWT (access token en
  memoria + refresh token en HttpOnly cookie).
- Los campeonatos del usuario se auto-detectan en el primer login; su
  configuración (presupuesto, premios, cláusulas) procede de la API de Futmondo.
- Los datos del campeonato (transacciones, jugadores, standings) son
  **compartidos** entre usuarios de ese campeonato; las operaciones salientes
  usan las credenciales Futmondo del usuario logado (no hay credencial global).

## Funcionalidad clave

- **Presupuesto / Balances**: saldos por equipo con detalle de altas/bajas,
  puja máxima y rendimiento.
- **Mercado**: jugadores del computer con puja sugerida (historial), rating
  Sofascore y tendencia; puja con min/max validados.
- **Sincronización asíncrona**: sync en background de 11 pasos (jugadores,
  transacciones, cláusulas, castigos, dream teams, rendimiento, plantillas,
  clasificación, odds, phantoms, sofascore) con progreso paso a paso y tareas
  durables.
- **Finanzas**: cálculo de dinero por usuario (presupuesto + puntos×€ + profit
  de transacciones + dream team + MVP + clasificación proporcional + castigos).
- **Analytics avanzado**: tendencias, consistencia, watchlist de mercado, red de
  cláusulas, rachas de oportunidad y proyecciones de jornada (paquete DDD
  `analytics/`).
- **Premios**: cálculo de premios por jornada (`prizes/`).
- **Asistente IA**: chat conversacional con guardrails, respuestas factuales
  desde la BD y fallback a LLM (Groq → Gemini), con persistencia de
  conversaciones.
- **PWA / Dark mode**: instalable en iPhone Safari; tema oscuro persistido.

## Contexto del intent activo

El intent activo (**Oleada 2 god-files, FR13**) es de tipo `refactor`: descomponer
el god-file `backend/app/services/assistant_service.py` (51 681 bytes / 1158
líneas) al patrón DDD ya establecido en la Oleada 1 (`analytics/`, `prizes/`),
preservando la superficie pública `get_assistant_service()` + `async ask(...)`.
La analítica de detalle de deuda técnica vive en `code-quality-assessment.md`.

## Trazabilidad

Hallazgos de dominio verificables contra: `README.md`, `docs/` (BACKLOG,
DEPLOY, ROLLBACK, PROJECT_CONTEXT), `backend/app/main.py` (montaje de la API) y
la superficie de servicios en `backend/app/services/`. Inventario de
componentes en `component-inventory.md`.
