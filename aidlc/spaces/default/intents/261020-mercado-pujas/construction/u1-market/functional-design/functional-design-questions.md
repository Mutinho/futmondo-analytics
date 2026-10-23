# Functional Design — Preguntas (u1-market)

> Unit `u1-market` (kind `ui`): la pantalla de Mercado nativa. El comportamiento
> está mayormente fijado por FR1–FR8, US1–US7, los mockups M1–M4 y el catálogo de
> componentes (C1–C8 + V1–V7). Estas preguntas resuelven los puntos funcionales
> abiertos antes de generar `functional-spec.md`, `frontend-components.md` y
> `traceability.json`. (Al ser UI, esta Unit no produce `entities.md`/`rules.md`:
> el modelo de datos ya está en Domain Design y el backend es inalterado.)

## Q1 — Reintento de carga y cambio de campeonato

Al entrar en Mercado se llama a `GET /market/today?championship_id=<activo>`.

- A. **Carga al aparecer + al cambiar el campeonato activo + botón de reintento en
  el estado de error.** Una recarga sustituye por completo lista y banner (no
  merge incremental). Sin auto-refresh por temporizador. (Coherente con el
  `effect` del Angular sobre `activeId()`.)
- B. Otro (especificar).

[Answer]: A

## Q2 — Orden: estado inicial y persistencia

- A. **Orden por defecto `value` descendente**; el selector arranca en "Valor".
  El criterio de orden es **estado efímero de pantalla** (no se persiste entre
  sesiones). Nulos siempre al final. Reordenar NO recarga (ordena la lista ya
  cargada). (FR5/US4.)
- B. Persistir el criterio de orden entre sesiones.
- C. Otro (especificar).

[Answer]: A

## Q3 — Escritura en vuelo (pujar/cancelar): alcance del bloqueo

- A. **`isWriting` global de pantalla**: mientras una escritura está en vuelo, se
  deshabilitan los botones de puja/cancelar de **todas** las cards (una sola
  escritura a la vez), como el `bidding` del Angular. Sólo `.accepted` recarga;
  `.rejected`/`.networkError` muestran aviso sin recargar. (FR6.4/FR7.3.)
- B. Bloqueo por card (varias escrituras concurrentes).
- C. Otro (especificar).

[Answer]: A

## Q4 — Validación de importe de puja (límites)

- A. **Rango `[market_price, available_for_bids]` y `> 0`.** Default =
  `suggested_bid`. Botón "Pujar" deshabilitado si inválido. El tope efectivo es
  `available_for_bids` ("Disponible"), divergencia intencionada vs `max_bid` de
  Angular (Q1=A de requisitos, ADR-3). El tope absoluto del backend (5e9) NO se
  replica en la UI (el backend lo valida). Mensajes de validación en castellano.
- B. Otro (especificar).

[Answer]: A

## Q5 — Aislamiento del detalle Sofascore

- A. **El sheet de detalle (`GET /sofascore/player/{name}`) tiene estado local al
  sheet** (loading/error/data) y usa `SofascoreService` dedicado; un fallo o
  latencia del detalle **no** afecta a la lista ni a la capacidad de pujar
  (FR8.2/ADR-5). El `404` se trata como "sin datos" dentro del sheet, no como
  error de la pantalla.
- B. Otro (especificar).

[Answer]: A

## Q6 — Mapeo de desenlaces de escritura (los 3 casos)

- A. **`MarketWriteOutcome` tipado** mapea: HTTP 2xx con `success=true` →
  `.accepted` (aviso de éxito + recarga); HTTP 2xx con `success=false` o 4xx
  (422/400) → `.rejected(message)` (aviso con el `message`/`detail`, sin recarga);
  error de red o 5xx → `.networkError` (aviso genérico, sin recarga). Nunca bool
  ni nil silencioso (ADR-2). (FR6.4/FR7.3.)
- B. Otro (especificar).

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Resumen funcional de `u1-market` antes de generar los artefactos:

- **Carga (FR1/FR2/US1)**: `GET /market/today?championship_id=<activo>` al
  aparecer y al cambiar el campeonato activo; estados loading/error(+reintento)/
  empty/data; una recarga sustituye lista+banner por completo; sin auto-refresh.
- **Banner (FR3/US2)**: 5 métricas formateadas como moneda; Balance y Disponible
  con color por signo/umbral.
- **Cards (FR4/US3)**: avatar, nombre, equipo+logo, badges Sofascore y %titular,
  posición(es), grid de métricas (tendencia con flecha+signo), marca de favorito.
- **Orden (FR5/US4)**: `value` desc por defecto, 7 campos, nulos al final,
  efímero, reordenar no recarga.
- **Pujar (FR6/US5)**: sheet default=`suggested_bid`, validación
  `[market_price, available_for_bids]` y `>0`, `POST /market/bid`.
- **Cancelar (FR7/US6)**: confirmación → `POST /market/cancelbid`.
- **Escritura (FR6.4/FR7.3)**: `isWriting` global; `MarketWriteOutcome` tipado
  (aceptada→aviso+recarga / rechazada→aviso sin recarga / error-red→aviso
  genérico sin recarga).
- **Detalle Sofascore (FR8/US7)**: sheet con estado local aislado
  (`GET /sofascore/player/{name}`); un fallo no afecta lista ni puja; `404` = sin
  datos en el sheet.
- **Artefactos a generar**: `functional-spec.md` (workflows + máquinas de estado
  de pantalla, vistas derivadas), `frontend-components.md` (jerarquía de
  componentes, props/estado, validación, puntos de integración) y
  `traceability.json`. (Unit `ui`: sin `entities.md`/`rules.md`.)

¿Todo correcto antes de generar los artefactos?

- **Looks correct** — confirmo y genero.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
