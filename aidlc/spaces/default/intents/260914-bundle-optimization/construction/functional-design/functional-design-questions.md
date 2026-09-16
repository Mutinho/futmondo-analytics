# Functional Design — Preguntas

> Stage 3.1 (Construction), scope refactor, profundidad Minimal. Zero-Unit (sin units-generation/domain-design): se ejecuta como stage ordinario, trabajando desde `requirements.md` y el codekb (RE) como diseño de dominio de facto.

## Preguntas abiertas

Ninguna. Este es un refactor de optimización del bundle **sin cambio funcional ni nuevos modelos de datos**. Las decisiones de diseño ya quedaron fijadas en Requirements Analysis:

- Objetivo de tamaño y budget (FR4, NFR1): Q1=B.
- Precarga con retardo (FR3, NFR4): Q2=C.
- Diferir `AssistantChatComponent`/`marked` (FR2): Q3=B.
- Registro de Chart.js/ng2-charts a nivel lazy (FR1): del escaneo RE.
- Verificación sin regresión (NFR2): Q4=A.

El diseño funcional se deriva directamente de esos requisitos y del código existente (arquitectura del bundle en `architecture.md`). No hay ambigüedad ni contradicción que resolver con el usuario en esta etapa de Construcción (las preguntas de Construcción son excepcionales, no rutinarias).

## Consolidated Summary Confirmation

El diseño funcional a generar documentará (sin cambio funcional, coste 0 €):

- **Entidades de configuración/carga** (entities.md): los "objetos" de diseño que gobiernan la composición del bundle — la configuración de la app (`ApplicationConfig`), el registro de gráficos, la estrategia de precarga, y la frontera de carga diferida del chat. No hay entidades de datos de negocio nuevas.
- **Reglas de negocio de carga** (rules.md, IDs `BRx.y`): reglas que formalizan qué debe cargarse eager vs lazy y las invariantes de "sin cambio funcional" (los gráficos y el chat siguen operativos), más el orden recortar→restaurar-budget.
- **Especificación funcional** (functional-spec.md): flujos de carga diferida (abrir chat → cargar `AssistantChatComponent`+`marked`; navegar a evolution/stats → cargar Chart.js; precarga con retardo tras inactividad) y las transiciones de estado de carga, con un diagrama ER derivado y resumen de reglas.
- **Componentes frontend** (frontend-components.md): los componentes Angular afectados y sus puntos de carga (`app.config.ts`, `app.ts`, `AssistantFabComponent`/`AssistantChatComponent`, componentes de gráficos), sus fronteras lazy y validaciones.
- **Trazabilidad** (traceability.json): mapeo de los criterios de aceptación (de FR1–FR4/NFR1–NFR4) a las reglas `BRx.y`.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
