# Business Overview — Futmondo Analytics

> Artefacto CodeKB (link 2, architect) del pipeline de Reverse Engineering. Base primaria: `developer-scan.md`. Este store es STALE tras un escaneo enfocado (FOCUSED SCAN) del backend `backend/` (durabilidad de estado y credenciales Futmondo).

## Dominio de negocio

Futmondo Analytics es una aplicación web **multi-usuario** que gestiona y analiza campeonatos de **Futmondo** (fantasy football). El dominio es la gestión económica y deportiva de una liga fantasy: presupuestos por equipo, mercado de fichajes con pujas, cláusulas, castigos/bonificaciones, rendimiento de jugadores, y el cálculo de finanzas derivado de la fórmula de premios de Futmondo.

Los usuarios se autentican con sus **credenciales de Futmondo**; el backend valida contra la API de Futmondo y opera con la sesión de cada usuario (no hay credenciales globales). Los datos de campeonato (transacciones, jugadores, clasificación) son compartidos entre usuarios del mismo campeonato.

## Propósito

Ofrecer, desde una **PWA** instalable en iPhone, una capa de analítica y ayuda a la decisión que Futmondo no expone directamente: saldos por equipo, puja sugerida de mercado enriquecida con ratings de Sofascore, finanzas por usuario, evolución histórica y estadísticas avanzadas.

## Funcionalidad clave

- **Autenticación**: login con credenciales Futmondo → JWT propio (access token en memoria, refresh token en cookie HttpOnly). Sesión Futmondo por usuario con TTL y re-auth automática.
- **Presupuesto**: saldos por equipo con detalle de altas/bajas, puja máxima y rendimiento.
- **Mercado**: jugadores del computer con puja sugerida (historial), rating Sofascore y tendencia; puja con validación min/max.
- **Sincronización asíncrona**: sync en background multi-paso (jugadores, transacciones, cláusulas, castigos, dream teams, rendimiento, plantillas, clasificación, odds, phantoms, Sofascore) con seguimiento de progreso por polling.
- **Finanzas**: cálculo de dinero por usuario combinando presupuesto, puntos, profit de transacciones, dream team, MVP, clasificación (fórmula proporcional de Futmondo) y castigos/bonificaciones.
- **Analítica**: evolución, estadísticas, clausulables y analytics avanzado (balances, phantoms) con gráficos.
- **Assistant (IA)**: servicio de asistente apoyado en proveedores `google-genai` / `groq`; su UI en el frontend es el chat (`AssistantChatComponent`) que renderiza Markdown.
- **PWA / Dark mode**: service worker, manifest y meta tags Apple; tema oscuro persistido.

## Actores

- **Usuario del campeonato**: gestiona sus campeonatos, consulta analítica y puja en mercado.
- **Procesos programados (cron Fly)**: sincronización diaria de datos y de Sofascore sin intervención humana.

## Restricciones de negocio relevantes

- **Coste 0 €**: el proyecto se mantiene íntegramente en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). Cualquier mejora debe respetar esta restricción.

## Contexto del intent activo

El intent `260914-durabilidad-estado-y-cre` (durabilidad de estado y credenciales, FR1 + FR5) **no cambia el dominio de negocio**: aborda una deuda técnica y de continuidad operativa. Hoy la **sesión Futmondo por usuario** y el **estado de las tareas de sync** viven exclusivamente en memoria de un único proceso backend, por lo que un reinicio o redeploy en Fly.io los pierde: el usuario conserva JWT válido pero cualquier endpoint que necesite el cliente Futmondo falla con **403** hasta re-login, y una tarea de sync en curso queda huérfana. Además, las credenciales Futmondo (`email`/`password`) se guardan **en claro en memoria**. El intent busca hacer durable ese estado y proteger las credenciales, respetando coste 0 € (Neon ya disponible) y sin asumir instancia única. Ver `code-quality-assessment.md` (deuda de durabilidad y seguridad) y `architecture.md` (flujos de auth/sesión y sync).

## Referencias cruzadas

- Componentes y responsabilidades: `component-inventory.md`.
- Superficies de API e integraciones externas: `api-documentation.md`.
- Arquitectura y flujos de negocio: `architecture.md`.
