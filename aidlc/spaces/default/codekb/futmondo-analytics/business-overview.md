# Business Overview — futmondo-analytics

## Business Domain

Aplicación web multi-usuario de **analítica de fantasy football** construida sobre
la liga **Futmondo**. Es una PWA (instalable en iPhone/Safari) que permite a cada
usuario gestionar y analizar sus campeonatos privados: presupuestos, mercado,
pujas, finanzas y estadísticas, enriquecidos con ratings externos de **Sofascore**.

## Purpose

Dar a cada participante de un campeonato Futmondo una capa analítica que la propia
Futmondo no ofrece: proyección de balance, puja sugerida con histórico, rating y
tendencia de jugadores, y un cálculo de dinero por usuario que reconcilia premios,
transacciones y clasificación con la fórmula proporcional de Futmondo.

## Key Functionality

- **Autenticación por usuario**: login con credenciales Futmondo del propio usuario;
  el backend valida contra la API de Futmondo y emite JWT (access en memoria,
  refresh en cookie HttpOnly). No hay credenciales globales; cada endpoint usa la
  sesión Futmondo del usuario logado (TTL 12h, re-auth automática).
- **Multi-campeonato / multi-usuario**: campeonatos auto-detectados al primer login;
  configuración (presupuesto, premios, cláusulas) obtenida de la API Futmondo. Los
  datos del campeonato (transacciones, jugadores, standings) se comparten entre
  usuarios.
- **Calculadora** (foco del intent `calculadora-mejora`): pantalla
  `/calculator` que hoy es un **planificador de ventas / proyección de balance**
  (no un cálculo de premios). Combina plantilla propia, mercado del día y jugadores
  en venta para proyectar un `futureBalance`. Detalle de implementación y flujo en
  `architecture.md` (Interaction Diagrams) y `component-inventory.md`.
- **Finanzas por usuario**: cálculo de dinero por participante agregando presupuesto
  inicial, profit de transacciones, ranking, MVP, dream-team, puntos y ajustes,
  leyendo todo el dinero de premio desde la tabla `team_prizes` como única fuente de
  verdad. Es un flujo de backend distinto de la Calculadora frontend (ver
  `component-inventory.md`).
- **Sincronización asíncrona**: sync en background en 11 pasos (jugadores,
  transacciones, cláusulas, castigos, dream teams, rendimiento, plantillas,
  clasificación, odds, phantoms, sofascore) con progreso paso a paso y reconexión al
  task.
- **Analítica visual**: presupuestos, mercado, evolución, estadísticas,
  clausulables y analytics con gráficos Chart.js; asistente IA (Gemini/Groq).

## Integrations

- **API Futmondo** — fuente primaria de datos del campeonato y autenticación.
- **API Sofascore** — ratings y rendimiento de jugadores (vía `curl_cffi`).
- **Gemini / Groq** — asistente IA conversacional.

## Sources

- Evidencia de escaneo: `developer-scan.md` (Handoff Summary, APIs Discovered).
- `README.md` (dominio, funcionalidades, multi-usuario, PWA).
- Detalle técnico cruzado en `architecture.md`, `component-inventory.md`,
  `api-documentation.md`.
