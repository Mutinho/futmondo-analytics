# Frontend Components — Optimización del bundle inicial (frontend Angular)

> Stage 3.1 Functional Design · Intent `260914-bundle-optimization` · scope refactor · Minimal.
> Fuente: `requirements.md` (FR1–FR3), `entities.md`, `functional-spec.md`, y `codekb/futmondo-analytics/code-structure.md` (ubicación de los componentes).
> Documenta los componentes/ficheros Angular afectados y sus puntos de carga. Sin cambio funcional: la jerarquía visual y las props/estado NO cambian; solo cambia el momento de carga.

## Sources

- `requirements.md` — FR1 (charts), FR2 (chat/marked), FR3 (precarga).
- `functional-spec.md` — flujos WF1–WF5 y transiciones de carga.
- `entities.md` — AppBootstrapConfig, LazyLoadBoundary, DeferredLibrary, PreloadingPolicy.
- `codekb/futmondo-analytics/code-structure.md` — rutas de los componentes.

## Componentes/ficheros afectados y sus puntos de carga

| Componente / fichero | Rol | Carga hoy | Carga objetivo | Regla |
|----------------------|-----|-----------|----------------|-------|
| `src/app/app.config.ts` (AppBootstrapConfig) | Configuración de arranque | eager | eager (pero sin registro global de charts ni PreloadAllModules) | BR1.1, BR3.1 |
| `src/app/app.ts` (App root) | Shell (Material chrome + FAB del asistente) | eager | eager (sin cambios) | — |
| `src/app/shared/components/assistant-fab.component.ts` | FAB que abre el chat | eager | eager; deja de importar estáticamente el chat | BR2.1 |
| `src/app/shared/components/assistant-chat.component.ts` | Chat (renderiza Markdown con marked) | eager (import estático desde el FAB) | lazy (bajo demanda al abrir el chat) | BR2.1, BR2.3 |
| `src/app/features/evolution/evolution.component.ts` | Vista de gráficos (evolution) | lazy (ruta) — pero charts registrados eager en config | lazy; registro de Chart.js a nivel de la ruta/componente | BR1.1, BR1.3 |
| `src/app/features/stats/stats.component.ts` | Vista de gráficos (stats) | lazy (ruta) — ídem | lazy; registro de Chart.js a nivel de la ruta/componente | BR1.1, BR1.3 |

## Fronteras de carga diferida (interaction flows)

### Frontera `assistant-chat` (FR2)
- **Disparador**: acción del usuario (pulsar el FAB del asistente).
- **Qué se difiere**: código de `AssistantChatComponent` + `marked`.
- **Flujo**: FAB (eager) → al abrir, carga bajo demanda el componente del chat → renderiza Markdown (mismo saneo/lógica).
- **Props/estado**: sin cambios; el estado `chatOpen()` y la comunicación FAB↔chat se preservan (la carga diferida es transparente a la lógica del componente).
- **Validación de formulario**: el input del chat conserva su validación actual (sin cambios).

### Fronteras `feature-evolution` / `feature-stats` (FR1)
- **Disparador**: navegación a la ruta lazy correspondiente.
- **Qué se difiere**: registro y uso de Chart.js/ng2-charts (`BaseChartDirective`).
- **Flujo**: navegación → carga de la ruta lazy → registro de Chart.js a nivel de ruta/componente → render del gráfico (idéntico).
- **Props/estado**: sin cambios; los datos de gráficos y su binding se preservan.

## Puntos de integración con API

Ninguno nuevo ni modificado. El refactor no toca llamadas a la API ni contratos; los componentes afectados siguen consumiendo los mismos endpoints (`/api/v1/*`) exactamente igual. Detalle en `codekb/futmondo-analytics/api-documentation.md`.

## Estrategia de precarga (FR3)

- La `PreloadingPolicy` (`delayed-idle`) se declara en `AppBootstrapConfig`. No es un componente visual: gobierna cuándo se descargan en segundo plano los chunks de ruta lazy tras inactividad.
- No afecta a la jerarquía ni al estado de ningún componente; es transparente para el usuario salvo por el momento de descarga de chunks.

## Notas de accesibilidad y `data-testid`

- El refactor no añade ni cambia elementos interactivos; conserva los `data-testid`/atributos de accesibilidad existentes en los componentes afectados. No se degrada la accesibilidad actual (NFR2 — sin cambio funcional).
