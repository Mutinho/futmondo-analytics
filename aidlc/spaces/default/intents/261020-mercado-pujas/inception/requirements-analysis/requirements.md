# Requirements — F3 Mercado (app nativa iOS)

> Requisitos funcionales (FR) y no funcionales (NFR) verificables para la pantalla
> de Mercado nativa. Cada FR traza a un artefacto de Ideación y/o a la fuente de
> verdad (vista Angular + contrato de backend confirmado en Reverse Engineering).

## Sources

- `.../ideation/intent-capture/intent-capture-questions.md` (decisiones Q1–Q4 =
  A), `.../ideation/scope-definition/scope-document.md` e `intent-backlog.md`
  (MoSCoW M1–M7, S1–S2, W1–W5),
  `.../ideation/feasibility/constraint-register.md` (restricciones C1–C9).
- `.../inception/practices-discovery/team-practices.md`.
- CodeKB: `api-documentation.md` (contratos `/market/*` y `/sofascore/player/*`),
  `component-inventory.md` (MarketPlayer, user_info).
- Fuente de verdad: `angular-app/src/app/features/market/`.

## Requisitos funcionales

### FR1 — Pestaña de Mercado
- **FR1.1** El `RootTabView` presenta **dos pestañas**: "Presupuesto" (existente)
  y "Mercado" (nueva, segunda). (Traza: M1, Q4.)
  - *Aceptación*: al abrir la app autenticada, existen exactamente dos pestañas y
    "Mercado" es seleccionable y muestra la pantalla de Mercado.

### FR2 — Carga y estados
- **FR2.1** Al seleccionar Mercado (o cambiar el campeonato activo), la app llama
  a `GET /api/v1/market/today?championship_id=<activo>` y muestra el resultado.
  (Traza: M2.)
- **FR2.2** La pantalla discrimina los estados **cargando**, **error**
  (con reintento), **vacío** ("No hay jugadores del computer…") y **con datos**.
  - *Aceptación*: cada estado se renderiza de forma distinta y verificable; un
    error de red muestra el estado error, no una lista vacía silenciosa.

### FR3 — Banner de usuario
- **FR3.1** Se muestra un banner con: **Presupuesto** (`balance`), **En pujas**
  (`active_bids_total`), **Balance** (`balance − active_bids_total`), **Puja
  máxima** (`max_bid`), **Disponible** (`available_for_bids`). (Traza: M3.)
  - *Aceptación*: los cinco valores se formatean como moneda (es-ES, 0 decimales)
    vía `MoneyFormatter`; Balance y Disponible cambian de color según signo/valor
    (positivo/negativo).

### FR4 — Lista de cards
- **FR4.1** Cada jugador se muestra como **card** con: avatar, nombre (enlace a
  `sofascore_url` si existe), equipo + `team_logo`, badge de rating Sofascore,
  badge de % titular, chip(s) de posición (`position`, `position2`), grid de
  métricas (VALOR, TENDENCIA con ↗/↘ y signo, PRECIO MERCADO, SUGERIDA, PUNTOS
  con nº de partidos, MEDIA a 1 decimal), y marca de favorito si `is_favorite`.
  (Traza: M4, S2, Q2.)
  - *Aceptación*: una card con `is_favorite=true` se distingue visualmente; la
    tendencia muestra flecha y signo (no sólo color).

### FR5 — Orden
- **FR5.1** Un selector permite ordenar la lista **descendente** por uno de:
  `value`, `change`, `sofascore_rating`, `starter_pct`, `suggested_bid`,
  `points`, `average`. Orden por defecto: `value`. (Traza: M5.)
  - *Aceptación*: cambiar el campo reordena sin recargar; valores nulos quedan al
    final.

### FR6 — Pujar (escritura)
- **FR6.1** En una card **sin puja activa**, el botón "PUJAR {suggested_bid}"
  abre un diálogo (sheet) de puja con importe **default = `suggested_bid`**,
  mínimo = `market_price`, máximo = `available_for_bids`. (Traza: M6, Q1, C9.)
  - *Nota de divergencia (confirmada, Q1=A)*: la vista Angular usa como tope
    `max_bid` ("Puja máxima"); F3 usa el **tope efectivo** `available_for_bids`
    ("Disponible") = `max_bid − active_bids_total`. Es una divergencia
    **intencionada** respecto al 1:1 (el fallback exacto en cascada se decide en
    diseño); el tope absoluto del backend (`price≤5.000.000.000`) no se replica
    en la UI.
- **FR6.2** La puja se **valida inline**: importe vacío o ≤ 0 → "debe ser mayor
  que 0"; < mínimo o > máximo → mensaje con el límite; el botón "Pujar" se
  deshabilita si es inválido.
- **FR6.3** Al confirmar, la app llama a `POST /api/v1/market/bid` con
  `championship_id, player_id, player_slug, price, is_clause=false` en query.
  (El backend valida además `price>0` y `price≤5.000.000.000`.)
- **FR6.4** El resultado se comunica al usuario distinguiendo: **puja aceptada**
  (HTTP 2xx con `success=true` → aviso de éxito), **rechazada por backend**
  (HTTP 2xx con `success=false`, o 422 por `price>0`/`price≤5.000.000.000`, o 400
  sin equipo → aviso con el `message`/`detail`), y **error de red / 5xx** (aviso
  de error genérico). Tras una puja con éxito, la pantalla **recarga** el mercado.
  - *Aceptación*: los tres desenlaces producen avisos distintos; sólo el éxito
    recarga; durante la operación los botones de escritura se deshabilitan.

### FR7 — Cancelar puja (escritura)
- **FR7.1** En una card **con puja activa** (`current_bid`), se muestra "Puja
  activa: {current_bid}" y un botón de cancelar. (Traza: M7.)
- **FR7.2** Cancelar pide **confirmación**; al confirmar llama a
  `POST /api/v1/market/cancelbid` con `championship_id, bid_id=current_bid_id` en
  query.
- **FR7.3** El resultado se comunica (aceptada HTTP 2xx `success=true` / rechazada
  por backend 2xx `success=false` o 4xx / error de red o 5xx); tras éxito, la
  pantalla **recarga**.

### FR8 — Detalle Sofascore (Should)
- **FR8.1** Al tocar el badge Sofascore de un jugador, se abre una **sheet** que
  llama a `GET /api/v1/sofascore/player/{player_name}?championship_id=<activo>` y
  muestra el rating y un grid de estadísticas. (Traza: S1, D3.)
- **FR8.2** La sheet discrimina **cargando**, **error** y **con datos**; un fallo
  del detalle **no** afecta a la lista ni a la capacidad de pujar.

## Requisitos no funcionales

- **NFR1 — Coste 0 €**: sólo SDK de Apple; sin dependencias nuevas. (Traza: C1.)
- **NFR2 — Tema**: reutiliza el `DesignSystem` oscuro/neón de F1/F2; donde no haya
  equivalente, Apple HIG. (Traza: C2.)
- **NFR3 — Seguridad**: toda llamada usa la sesión autenticada de F1 (Bearer); el
  refresh token permanece en Keychain; ningún material de credencial se expone en
  logs ni mensajes de error. (Traza: C4.)
- **NFR4 — Idioma**: identificadores/comentarios en inglés; texto de usuario en
  castellano. (Traza: C5.)
- **NFR5 — Testabilidad**: la lógica pura (formato, orden, validación de importe,
  mapeo de DTO) vive en `FutmondoKit` con XCTest; las vistas SwiftUI se validan en
  dispositivo. (Traza: C6, posture test-after.)
- **NFR6 — Accesibilidad**: contraste del DesignSystem; significado no sólo por
  color; etiquetas accesibles para acciones; operable con VoiceOver.

## Assumptions & Open Questions

None.
