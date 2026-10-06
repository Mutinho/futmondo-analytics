# Requirements — Mejora de la Calculadora (toggle "Incorporar jugadores en venta")

Intent: `calculadora-mejora` · Scope: `refactor` (feature acotada sobre pantalla existente) · Fase: Inception
Repositorio: `futmondo-analytics` (brownfield)

## Análisis de intención

El usuario quiere **extender la pantalla Calculadora** (`/calculator`) para que
la inclusión de los jugadores en venta en la proyección de balance sea
**opcional y controlable por el usuario**, mediante un toggle "Incorporar
jugadores en venta". El objetivo es poder calcular "desde cero" (sin el valor de
los jugadores que uno tiene a la venta) **sin** tener que retirar manualmente
esos jugadores del mercado. Las pujas activas deben seguir contando siempre. No
se introducen datos nuevos ni se cambia la fórmula base: es una mejora de la
proyección existente más una preferencia persistente de UI.

Hoy la Calculadora calcula:
`futureBalance = balance + selectedTotal + onSaleTotal − activeBidsTotal`
(ver `codekb/futmondo-analytics/architecture.md` → Interaction Diagrams → "Flujo
Calculadora"). La mejora hace que el término `onSaleTotal` sea condicional al
toggle.

## Requisitos funcionales

### FR1 — Toggle "Incorporar jugadores en venta"
- **FR1.1**: La pantalla Calculadora DEBE mostrar un control toggle etiquetado
  "Incorporar jugadores en venta".
- **FR1.2**: Cuando el toggle está **ON**, el cálculo DEBE incluir el total de
  los jugadores en venta: `futureBalance = balance + selectedTotal + onSaleTotal − activeBidsTotal`
  (comportamiento idéntico al actual).
- **FR1.3**: Cuando el toggle está **OFF**, el cálculo DEBE excluir el total de
  los jugadores en venta: `futureBalance = balance + selectedTotal − activeBidsTotal`.
- **FR1.4**: El cambio del toggle DEBE recalcular y reflejar el `futureBalance`
  de forma reactiva, sin recargar la página ni requerir otra acción del usuario.

### FR2 — Invariante de pujas activas
- **FR2.1**: El total de pujas activas (`activeBidsTotal`) DEBE restarse del
  `futureBalance` SIEMPRE, con independencia del estado del toggle (ON u OFF).

### FR3 — Persistencia de la preferencia
- **FR3.1**: El estado del toggle DEBE persistirse en `localStorage` del
  navegador (mismo patrón que la preferencia de dark mode).
- **FR3.2**: Al abrir o recargar la pantalla Calculadora, el toggle DEBE
  restaurar su último estado guardado desde `localStorage`.
- **FR3.3**: La primera vez (sin valor guardado), el toggle DEBE arrancar en
  **ON** (incluye jugadores en venta), preservando el comportamiento actual de
  la pantalla. (Ver Assumptions → A1.)
- **FR3.4**: Si el valor almacenado en `localStorage` está corrupto, ausente o
  no es parseable a booleano, el toggle DEBE tratarlo como "sin valor" y arrancar
  en **ON** (mismo criterio que FR3.3), sin lanzar error ni romper el render de
  la pantalla.

### FR4 — Preservación del comportamiento existente
- **FR4.1**: La acción de vender jugadores DEBE seguir funcionando como hoy
  (`POST /api/v1/roster/sell`); esta mejora no la altera.
- **FR4.2**: Las fuentes de datos actuales (`getMyRoster()`,
  `GET /api/v1/market/today`, `getOnSale()`) NO cambian. Lo que cambia según el
  toggle es: si `onSaleTotal` entra o no en la suma (FR1), si el bloque "En
  venta" se muestra u oculta y si los jugadores en venta aparecen o no en la
  lista seleccionable (FR5). No se añaden endpoints ni datos nuevos.

### FR5 — Reubicación de los jugadores en venta según el toggle
- **FR5.1**: Cuando el toggle está **ON**, el comportamiento es el actual: el
  bloque "En venta" (sección de tarjetas de `onSalePlayers`) se MUESTRA y esos
  jugadores quedan EXCLUIDOS de la lista seleccionable.
- **FR5.2**: Cuando el toggle está **OFF**, el bloque "En venta" se OCULTA
  (no basta con atenuar el importe de cabecera; se oculta la sección de
  tarjetas) y los jugadores en venta se INCLUYEN en la lista seleccionable.
- **FR5.3**: Los jugadores en venta que pasan a la lista seleccionable con el
  toggle OFF entran **deseleccionados**; el usuario los marca manualmente para
  incluir su valor en `selectedTotal` (simulación de venta desde cero).
- **FR5.4**: Alternar el toggle DEBE reconstruir la lista seleccionable de forma
  reactiva (incluir/excluir los jugadores en venta) sin recargar la página. Al
  volver a **ON**, los jugadores en venta se EXCLUYEN de nuevo de la lista y su
  valor vuelve a contar vía `onSaleTotal` (BR1.1); cualquier selección manual
  que tuvieran con OFF se descarta en esa transición.
- **FR5.5** (invariante anti-doble-conteo): un jugador en venta aporta su valor
  al `futureBalance` por **una sola vía**: vía `onSaleTotal` cuando el toggle
  está ON, o vía `selectedTotal` solo si el usuario lo selecciona con el toggle
  OFF — **nunca por ambas a la vez**.

## Requisitos no funcionales

- **NFR1 (Coste)**: La solución DEBE mantenerse a **coste 0 €** — sin
  dependencias nuevas de pago ni servicios fuera de los tiers gratuitos. No se
  prevén dependencias nuevas; cualquiera sería OSS y fijada a versión exacta.
- **NFR2 (PWA / responsive / accesibilidad)**: El toggle y la pantalla DEBEN
  seguir siendo usables en PWA/responsive (iPhone/Safari). Criterios
  verificables del toggle: (a) usa un control de formulario Material estándar
  (p. ej. `mat-slide-toggle`) con **etiqueta de texto asociada** "Incorporar
  jugadores en venta"; (b) es **operable solo con teclado** (foco visible +
  activación con Espacio/Enter); (c) expone un **estado accesible** on/off
  (atributo `aria-checked`/rol de switch que provee el componente Material).
- **NFR3 (Gate de CI)**: El cambio DEBE pasar el gate de CI bloqueante
  (`pytest` + `ng test`) antes de fusionar a `main`; el ratchet de cobertura
  frontend solo sube, nunca baja.
- **NFR4 (Testabilidad)**: La lógica condicional de `futureBalance` DEBE ser
  verificable con tests de componente/unidad del frontend que aseveren el efecto
  (valor calculado con toggle ON vs OFF, la invariante de pujas, y la
  restauración/fallback de `localStorage` de FR3.2/FR3.4), sin `assert`/specs
  espejo que pasen siempre. Como `calculator.component.ts` no tiene spec hoy,
  aplica el mandato afirmado **characterization-first**: congelar el
  comportamiento existente con tests antes de extender el cálculo con el toggle.
- **NFR5 (Mantenibilidad / arquitectura)**: Si la mejora requiriera backend
  (improbable), el código nuevo DEBE ir tras una capa/función estrecha testeable
  — NUNCA ampliando los god-files existentes (`data_sync_service.py`,
  `data_manager_v2.py`, `assistant_service.py`) ni el patrón SQL-en-router.

## Restricciones

- **C1**: Frontend Angular 22 (standalone components, signals, PWA); el toggle
  se integra en `angular-app/src/app/features/calculator/`.
- **C2**: Idioma: identificadores/comentarios en inglés; texto de UI
  (etiqueta del toggle) y mensajes de commit en castellano.
- **C3**: No cambiar la **fórmula de proyección lineal base**; solo extenderla
  haciendo condicional el término `onSaleTotal`.
- **C4**: Node fijado en `.nvmrc` = `22.22.3`; verificar `npm ci` + `ng test`
  en contenedor `node:22.22.3` solo si se tocan devDependencies del frontend (no
  previsto en este intent).

## Assumptions

- **A1** (confirmada en el resumen): el valor por defecto del toggle la primera
  vez (sin valor en `localStorage`) es **ON**, para no cambiar el comportamiento
  actual de la pantalla. Owner: producto. Estado: confirmada.
- **A2**: La mejora es **solo frontend** (confirmado contra
  `calculator.component.ts`: `onSaleTotal`, la lista seleccionable y el bloque
  "En venta" se gestionan en el componente). Owner: arquitectura/desarrollo.
  Estado: confirmada.
- **A3**: La clave de `localStorage` es `futmondo_calc_include_onsale`
  (prefijo `futmondo_`, valor `"true"`/`"false"`). Owner: desarrollo. Estado:
  confirmada.

## Fuera de alcance

- Incorporar datos financieros/de premios reales (`player-finances` /
  `team_prizes`) a la Calculadora.
- Rating/tendencia de Sofascore, histórico de pujas o proyección temporal
  multi-jornada en la Calculadora.
- Ejecutar compras/pujas reales desde la Calculadora (FR5 solo reubica
  jugadores en la lista para SIMULAR ventas; no crea una acción de compra).
- Cambios en el flujo o la lógica de `sellPlayers()` / `POST /api/v1/roster/sell`.
- Cualquier cambio de backend.

## Preguntas abiertas

- `None.` (A2 y A3 confirmadas; FR5 cierra el comportamiento del toggle OFF.)

## Sources

- `[desc]` Initial description: "Mejora en la pantalla de 'Calculadora' de la aplicación" (`project-description.json`).
- `[scope]` Workflow-selected scope: refactor.
- Respuestas del usuario en `requirements-analysis-questions.md` (Q1–Q6 + ampliación FR5 tras prueba en local + Consolidated Summary Confirmation = `Looks correct`).
- Feedback de la prueba en local (toggle OFF debe ocultar el bloque "En venta" y devolver los jugadores a la lista seleccionable, deseleccionados) → FR5.
- `codekb/futmondo-analytics/business-overview.md` (Calculadora como planificador de ventas/proyección de balance).
- `codekb/futmondo-analytics/architecture.md` (Interaction Diagrams → "Flujo Calculadora": fórmula de `futureBalance`, `POST /api/v1/roster/sell`).
- `codekb/futmondo-analytics/code-structure.md` (`angular-app/src/app/features/calculator/`, patrón signals + `computed()`, persistencia en `localStorage` del dark mode).

## Assumptions & Open Questions

Ver secciones "Assumptions" y "Preguntas abiertas" arriba.
