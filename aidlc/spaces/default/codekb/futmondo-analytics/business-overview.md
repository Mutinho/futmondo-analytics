# Visión de Negocio — futmondo-analytics

## Dominio y Propósito

futmondo-analytics es una aplicación web multi-usuario (PWA) que gestiona y analiza
campeonatos de **Futmondo** (fantasy football). Da a cada usuario una vista sobre sus
propios campeonatos: control de presupuestos, análisis de mercado, ratings de Sofascore,
pujas por jugadores y cálculo de finanzas, todo accesible desde el navegador o instalado
como app en iPhone.

El sistema no tiene credenciales globales: cada usuario se autentica con su email/password
de Futmondo, el backend valida contra la API de Futmondo y emite un JWT propio. Los
endpoints operan con las credenciales Futmondo del usuario logado.

## Funcionalidad Clave

- **Autenticación delegada + JWT propio**: login contra Futmondo, access token en memoria
  del navegador (1h) y refresh token en cookie `HttpOnly` (30 días). La revocación se apoya
  en una tabla `refresh_tokens` persistida (ver `component-inventory.md`).
- **Presupuesto y finanzas**: saldos por equipo, altas/bajas, puja máxima y cálculo de
  dinero por usuario (fórmula proporcional de Futmondo: puntos, profit de transacciones,
  dream team, MVP, clasificación, castigos/bonificaciones).
- **Mercado y pujas**: mercado del día con puja sugerida, rating Sofascore y tendencia; el
  usuario puja por jugadores vía `POST /api/v1/market/bid` (proxy a Futmondo).
- **Sincronización asíncrona**: sync en background por pasos (jugadores, transacciones,
  cláusulas, clasificación, Sofascore, etc.), con crons programados de coste ~0.
- **Analítica visual**: evolución, estadísticas, clausulables y sub-tabs de analytics con
  gráficos Chart.js.

## Premios de Jornada (dominio central de un intent previo)

El **cálculo de premios de jornada** (matchday prizes) es la mecánica de negocio que
reparte el dinero que gana cada equipo en cada jornada de un campeonato. Es la base de las
vistas de Presupuesto y Finanzas: el saldo y las finanzas de cada usuario se derivan, en
parte, de la suma de premios acumulados. Los términos de negocio por (equipo, jornada) son:

- **points_prize** — pago por los puntos que hace el equipo esa ronda
  (`round_points * money_per_point`). Se paga SIEMPRE, incluso en jornadas adelantadas.
- **ranking_prize** — premio por la posición del equipo en el ranking de la ronda, sólo si
  la ronda se jugó por completo y está cerrada. Reparto proporcional entre miembros activos;
  el campeonato elige modo `flop` (premia a los peores) u otro modo (premia a los mejores).
- **mvp_prize** — bonus para el equipo cuya alineación contenía al MVP del dream team.
- **dream_team_prize** — bonus proporcional al número de jugadores del once ideal presentes
  en la alineación del equipo.

Estos importes se **precalculan una sola vez por sincronización** y se persisten como fuente
de verdad; las pantallas de saldos y finanzas sólo leen y suman. La mecánica técnica exacta,
sus entradas y su tabla de salida están en `architecture.md` (Diagramas de Interacción) y
`code-quality-assessment.md` (deuda y riesgos).

## Contexto de Intents Anteriores (Backend Security Hardening)

Un análisis previo de ingeniería inversa sirvió al intent `260916-backend-security-hardeni`
(scope `security-patch`), que agrupaba cinco mejoras de seguridad de esfuerzo pequeño sobre
el backend FastAPI. La naturaleza de aquel intent era «verificar y, si aplica, corregir con
test de regresión»:

- **FR6** — validar `price` (rango/positividad) en `market.py::place_bid`; sólo valida el
  frontend (evadible llamando la API directamente).
- **FR7** — confirmar la exposición de `GET /api/v1/photos/{player_id}` (protegido por
  middleware; la ruta pública real es `/static/photos/*`).
- **FR8** — asegurar que `SSL_VERIFY=0` (sólo en `docker-compose.yml` local) no llega a
  producción; el flag está huérfano.
- **FR9** — corregir el bug de precedencia naive/aware en `is_refresh_token_valid`.
- **FR18** — confirmar la guarda `ENABLE_DB_ADMIN` de `/database/reset|/populate`
  (ya implementada y testeada).

El detalle técnico de cada hallazgo y su evidencia vive en `code-quality-assessment.md`
(deuda técnica) y `api-documentation.md` (superficie afectada); aquí sólo se enmarca el
valor de negocio: reducir la superficie de abuso de las pujas, el acceso de administración
y la sesión de refresco sin salir del stack ni del presupuesto de coste 0 €.

## Contexto de Intents Anteriores (Frontend Coverage Gate)

El intent `260918-frontend-coverage-gate` (scope `classic`) NO añadió comportamiento de
dominio nuevo: fue una intervención de **calidad e ingeniería de entrega** sobre el frontend
Angular y el pipeline CI/CD. Su valor de negocio era de **protección**: hacer que los
cambios de código del frontend estuvieran respaldados por tests significativos que
impidieran que una regresión en lógica cubierta (p. ej. el `auth.interceptor` o los
servicios `core`) llegara a producción. Los hallazgos y el estado de cobertura de aquel
intent viven en `code-quality-assessment.md`; la superficie afectada (schematics, tooling de
test, workflows) se describe en `code-structure.md`, `technology-stack.md` y
`component-inventory.md`.

## Contexto del Intent Activo (Backend Reliability — Manejo de Errores y Contratos de Integración)

El intent activo `260923-backend-fiabilidad-error` es una intervención de **fiabilidad del
backend** sobre el servicio FastAPI. Su valor de negocio es de **integridad y confianza
operativa**: cuando una sincronización toca fuentes externas volátiles (API Futmondo,
Sofascore) o escribe en la caché de datos (Neon PostgreSQL), el sistema debe **distinguir
un fallo recuperable de uno fatal** y, sobre todo, **no corromper datos** ni presentar al
usuario un estado mixto silencioso. Dos áreas funcionales lo enmarcan:

- **FR3.2 — Manejo de errores (recuperable vs. fatal)**: el backend ya tiene un vocabulario
  parcial y de buena calidad para señalizar fallos (excepción tipada que se re-lanza,
  rollback en la capa de conexión, marcado de paso "degradado" para fallos no críticos),
  pero se aplica de forma desigual. El objetivo de negocio es que un fallo no crítico degrade
  la vista sin tumbar toda la sincronización, y que un fallo fatal (p. ej. baneo de IP,
  fallo de conexión) se propague con señal clara en lugar de aparecer como "sin datos".
- **FR4 — Contratos de integración**: el cliente de la API Futmondo hoy señala el fallo
  devolviendo `None`/`bool`, sin exponer un modo de fallo tipado. Esto colapsa "no hay datos"
  con "la integración falló", lo que erosiona la fiabilidad de las pantallas que consumen
  esos datos. El valor de negocio es un contrato de integración explícito por frontera, de
  modo que el consumidor sepa si reintentar, degradar o abortar.

El intent es **acotado y aditivo** sobre un sistema brownfield ya en producción: **NO
reescribe los god-files** (`data_sync_service.py`, `data_manager_v2.py`); cataloga y endurece
el manejo de errores tras capas/funciones estrechas testeables. El detalle técnico de la
realidad actual (vocabulario recuperable-vs-fatal ya presente, huecos de FR3.2/FR4 y el
punto de corromper-datos) es propietario de `code-quality-assessment.md`, con los flujos de
fiabilidad en `architecture.md`.
