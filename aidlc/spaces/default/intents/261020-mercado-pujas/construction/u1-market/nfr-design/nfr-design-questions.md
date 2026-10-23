# NFR Design — Preguntas (u1-market)

> Unit `u1-market` (kind `ui`). Diseño de patrones para los `NFRx.y` de la etapa
> anterior. Al ser `ui`, produce `performance-design.md`, `security-design.md`,
> `logical-components.md` y `traceability.json` (scalability/reliability/
> observability son de kind `service`, NO aplican). Los patrones reutilizan los
> ya establecidos en F1/F2; estas preguntas confirman el enfoque.

## Q1 — Patrones de rendimiento (UI)

- A. **Render perezoso + estado explícito + sin trabajo bloqueante en el hilo
  principal**: `LazyVStack` para la lista; estados loading/error/empty/data
  explícitos; el ordenado y el formateo de moneda se hacen en memoria en
  `FutmondoKit` (puro); `AsyncImage` con placeholder para avatares/logos; la
  escritura corre en el actor `MarketService` (off-main) y sólo el estado
  observable toca `@MainActor`. (NFR6.1–NFR6.6.)
- B. Otro (especificar).

[Answer]: A

## Q2 — Diseño de seguridad (defensa en profundidad para la escritura)

- A. **Reutilizar la cadena de auth de F1 + validación en dos capas**: el
  `NetworkClient` inyecta `Bearer` por request (token en memoria) y rechaza
  no-https; el refresh/401 lo maneja la capa de `AuthService` existente; la puja
  se valida en cliente (`BidAmountValidator`, UX) **y** en el backend (autoridad);
  los avisos de error nunca incluyen material de credencial (usan `message`/
  `detail` del backend o texto genérico). Sin almacenamiento nuevo de secretos.
  (NFR3.1–NFR3.8.)
- B. Otro (especificar).

[Answer]: A

## Q3 — Componentes lógicos / dominios de fallo

- A. **Aislar el detalle Sofascore como dominio de fallo propio**: `MarketService`
  (lista + escritura) y `SofascoreService` (detalle) son actores separados con
  resultados tipados; el fallo del detalle queda contenido en el sheet (estado
  local) y no propaga a la lista ni a la escritura (FR8.2/ADR-5). La lógica pura
  (`MarketSorter`, `BidAmountValidator`, mapeo `MarketWriteOutcome`) es su propio
  "componente" testeable, aislado de la UI. Blast radius de un fallo de red =
  el estado de esa operación, nunca toda la pantalla. (NFR del aislamiento.)
- B. Otro (especificar).

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Resumen de NFR Design de `u1-market` antes de generar los artefactos:

- **Rendimiento (NFR6.1–NFR6.6)**: `LazyVStack`, estados explícitos, orden/formato
  en memoria (`FutmondoKit` puro), escritura en actor off-main, `@MainActor` sólo
  para el estado observable, `AsyncImage` con placeholder.
- **Seguridad (NFR3.1–NFR3.8)**: cadena de auth de F1 (Bearer por request, rechazo
  no-https, refresh/401 existente); validación en dos capas (cliente UX + backend
  autoridad); avisos sin material de credencial; sin almacenamiento nuevo.
- **Componentes lógicos / dominios de fallo**: `MarketService` y `SofascoreService`
  como actores separados; el fallo del detalle contenido en el sheet (estado
  local), no propaga a lista ni escritura (FR8.2/ADR-5); lógica pura
  (`MarketSorter`, `BidAmountValidator`, mapeo `MarketWriteOutcome`) como
  componente testeable aislado; blast radius = la operación, no la pantalla.
- **Artefactos a generar**: `performance-design.md`, `security-design.md`,
  `logical-components.md`, `traceability.json`. (Unit `ui`: NO scalability/
  reliability/observability — son de kind `service`.)

¿Todo correcto antes de generar los artefactos?

- **Looks correct** — confirmo y genero.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
