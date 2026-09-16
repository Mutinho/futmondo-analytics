# Build and Test Summary — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield.
> Rol: quality engineer (con devsecops de apoyo). Sin cambio funcional, coste 0 €.

## Veredicto

**El refactor cumple todos los objetivos medibles.** Build de producción verde con `maximumError: 1MB`, chunk inicial por debajo de 1 MB, chart.js/ng2-charts/marked fuera del inicial, suite 11/11 verde. Queda una verificación manual (gráficos y chat) que no es automatizable y se traslada al usuario.

## Resultados clave

| Objetivo | Resultado |
|---|---|
| NFR1 — bundle inicial < 1 MB | **819.05 kB** (build pasa con `maximumError: 1MB`) ✓ |
| FR1.2/BR1.2 — charts fuera del inicial | Verificado por inspección de chunks; charts en chunk lazy ✓ |
| FR2.2/BR2.2 — marked fuera del inicial | Verificado; `assistant-chat-component` es chunk lazy ✓ |
| FR3 — precarga diferida | `IdlePreloadingStrategy` (idleDelay 2000ms), spec 5/5 verde ✓ |
| NFR2/BR5.1 — sin regresión | Suite 11/11 verde ✓ |
| NFR3/BR5.2 — coste 0 €, no sustituir libs | Sin deps nuevas; chart.js movido a lazy, no eliminado ✓ |

## Corrección aplicada en esta etapa

Fallo de compilación **NG8001** detectado en el primer build: el `@defer` de `AssistantChatComponent` exigía mantener el componente en `imports` del `AssistantFabComponent`. Corregido restaurando el import (el compilador segmenta el chunk igual porque su única referencia está dentro de `@defer`). El build y la inspección posteriores confirman que el chat y `marked` siguen fuera del inicial. Este fallo no lo había capturado la revisión de Code Generation porque se apoyó en un build stale; Build and Test lo detectó y resolvió.

## Ficheros de código modificados en esta etapa

- `angular-app/src/app/shared/components/assistant-fab.component.ts` — restaurado el import de `AssistantChatComponent` en `imports` (fix NG8001), manteniendo el `@defer`.

## Pendiente de verificación manual (no bloqueante para el build)

- Navegar a `evolution` y `stats`: gráficos renderizan tras carga lazy (FR1.3/BR1.3).
- Abrir el chat: se carga bajo demanda y renderiza Markdown (FR2.3/BR2.3).

## Siguiente etapa

Deployment Pipeline (`3.7 ci-pipeline` ya se salta por scope; el motor resuelve el siguiente).
