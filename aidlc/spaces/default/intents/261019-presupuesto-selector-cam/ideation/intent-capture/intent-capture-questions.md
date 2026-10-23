# Intent Capture — Questions (F2: Presupuesto + selector de campeonato)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.
> Modo "Guíame": cada pregunta lleva mi recomendación; decides tú. Responde en `[Answer]:` con la letra (o `X` + texto).

## Q1 — Patrón nativo del selector de campeonato

¿Cómo quieres que sea el selector de campeonato, siempre accesible pero no invasivo?

- A. **Menú en la navigation bar** (toolbar superior): el título muestra el campeonato activo con un chevron; al tocar, despliega un `Menu` nativo con la lista. No ocupa espacio permanente y es idiomático iOS. **(recomendada)**
- B. **Botón de barra + hoja modal** (`.sheet` / confirmation dialog): un botón a la derecha de la navigation bar abre una hoja con la lista de campeonatos.
- C. **Segmented control / picker fijo** bajo la navigation bar: siempre visible, pero ocupa una franja permanente (más invasivo).
- X. Other (please specify)

[Answer]: A

## Q2 — Alcance de la pantalla de Presupuesto en F2

¿Qué debe incluir Presupuesto en este intent?

- A. **Lista de equipos (solo lectura) con todas las métricas** de `TeamBudget` reproduciendo la jerarquía de la web (saldo, rendimiento, puja máxima, premios, etc.), sin detalle ni diálogos. Navegación al detalle y premios quedan como follow-up. **(recomendada: entrega valor y acota el intent)**
- B. Lista **+ detalle de equipo** (`budget-detail`) en el mismo intent.
- C. Lista **mínima** (solo equipo + saldo + rendimiento) como primer paso, resto diferido.
- X. Other (please specify)

[Answer]: A

## Q3 — Presentación tabla vs cards en iOS

La web ofrece toggle tabla/cards (default cards en móvil). En iPhone, ¿qué adoptamos?

- A. **Solo cards/list nativa** (una fila rica por equipo, estilo `List`/`LazyVStack`), sin toggle: es lo natural en pantalla de teléfono y simplifica. **(recomendada)**
- B. Mantener **toggle tabla/cards** como en la web.
- C. **Tabla** compacta con scroll horizontal.
- X. Other (please specify)

[Answer]: A

## Q4 — Ordenación

La web ordena por saldo/rendimiento/puja máxima/valor/gastado/ingresado.

- A. **Incluir ordenación** (por las mismas claves) vía un control nativo (menú de ordenación en la toolbar). **(recomendada: es parte del valor de la vista)**
- B. **Sin ordenación** en F2 (orden fijo por saldo); diferir.
- X. Other (please specify)

[Answer]: A

## Q5 — Comportamiento al cambiar de campeonato

Al elegir otro campeonato en el selector:

- A. **Recargar la pantalla de Presupuesto** del nuevo campeonato y **persistir la selección** en almacenamiento nativo (equivalente al `localStorage` de la web, aquí `UserDefaults`), de modo que al reabrir la app recuerde el último campeonato. **(recomendada: paridad con la web)**
- B. Recargar pero **no persistir** (vuelve al primero al reabrir).
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

Asumo que: (a) los endpoints existentes (`/api/v1/analytics/balances`, `/api/v1/user/championships`) se consumen tal cual sin cambios de backend; (b) el formato de dinero sigue el patrón de la web (`money` pipe: M/K abreviado); (c) no se toca el modelo de sesión de F1; (d) coste 0 € (solo SDK de Apple).

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions

## Consolidated Summary Confirmation

Resumen del intent F2 (`261019-presupuesto-selector-cam`):

- **Objetivo**: primera pantalla real tras el login en SwiftUI (coste 0 €, sobre la librería de diseño de F1): **Presupuesto** (saldos por equipo) + **selector de campeonato** nativo siempre accesible y no invasivo.
- **Selector**: menú en la navigation bar (título = campeonato activo con chevron). Al cambiar: recarga Presupuesto y persiste en `UserDefaults`.
- **Presupuesto**: lista/cards nativa (solo lectura) con todas las métricas de `TeamBudget` (saldo, valor plantilla, gastado, ingresado, ops, rendimiento, premios, puja máxima), tokens `money-positive`/`money-negative`, con ordenación por las claves de la web. Detalle de equipo y diálogo de premios → follow-up.
- **Sin cambios de backend**: consume `/api/v1/analytics/balances` y `/api/v1/user/championships` tal cual; sesión de F1 intacta.
- **Verificación**: lógica testeable en `FutmondoKit` (`swift test`); UI validada en iPhone 13 Pro.

¿Does this all look correct?

[Answer]: Looks correct
