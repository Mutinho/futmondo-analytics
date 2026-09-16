# Test Results — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield.
> Ejecutado en contenedor `node:22.22.3` (Node local 22.22.1 < mínimo CLI 22.22.3), coste 0 €.

## Resumen

Todas las verificaciones en verde. El refactor cumple NFR1 (bundle < 1 MB), NFR2 (sin regresión), NFR3 (coste 0 €), NFR4 (precarga diferida) sin cambio funcional.

## 1. Build de producción (NFR1 / FR4.3 / BR4.2)

Build completa sin error con `maximumError: 1MB`.

| Chunk inicial | Raw size |
|---|---|
| main-*.js | 427.81 kB |
| chunk (varios, 7) | resto |
| **Initial total** | **819.05 kB** (< 1 MB ✓) |
| Initial transfer estimado | 181.09 kB |

## 2. Verificación de composición del chunk inicial (R-01 / FR1.2 / BR1.2 / FR2.2 / BR2.2)

Inspección de `main-*.js` y de los 7 chunks referenciados en el `modulepreload` de `index.html`:

- **chart.js / ng2-charts**: NO presentes en ningún chunk inicial. ✓ (marcadores `RadialLinearScale`, `BarController`, `getDatasetMeta`, `ng2-charts`, `BaseChartDirective` ausentes del initial).
- **marked**: NO presente en ningún chunk inicial. ✓ (marcadores `Tokenizer`, `Lexer`, `marked` ausentes del initial).
- **chart.js SÍ presente en un chunk LAZY** (`chunk-hE-eqeH-2.js`): confirma que se movió, no se eliminó (BR5.2 ✓).
- Chunks lazy nombrados relevantes: `assistant-chat-component` (62.31 kB), `stats-component` (54.61 kB) — el chat y las vistas de gráficos están diferidos. ✓

## 3. Suite de tests unitarios (NFR2 / BR5.1)

`npx ng test --no-watch` (Vitest 4):

| Fichero | Tests | Resultado |
|---|---|---|
| `idle-preloading-strategy.spec.ts` | 5 | ✓ passed |
| `auth.interceptor.spec.ts` | 6 | ✓ passed |
| **Total** | **11** | **11 passed** |

Sin regresión respecto al estado previo.

## 4. Corrección aplicada durante Build and Test

Se detectó un fallo de compilación **NG8001** (`'app-assistant-chat' is not a known element`): el bloque `@defer` de `AssistantChatComponent` requiere que el componente siga en el array `imports` del `AssistantFabComponent`. El compilador de Angular mueve el componente al chunk diferido cuando su única referencia está dentro de `@defer`, sin necesidad de quitarlo de `imports`. Corregido restaurando el import en `assistant-fab.component.ts`; el build y el desglose de chunks posteriores confirman que `assistant-chat` y `marked` siguen fuera del inicial.

## 5. Verificación manual pendiente (BR5.1 / FR1.3 / FR2.3)

No automatizable en esta etapa (componentes con `skipTests` por convención). A confirmar por el usuario en ejecución real:
- Navegar a `evolution` y `stats`: los gráficos renderizan correctamente tras la carga lazy.
- Abrir el chat del asistente: se carga bajo demanda y renderiza Markdown correctamente.
