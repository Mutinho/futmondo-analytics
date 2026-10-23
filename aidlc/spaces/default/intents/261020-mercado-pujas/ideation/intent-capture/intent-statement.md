# Intent Statement — F3 Mercado (app nativa iOS)

## Intent

Reproducir en la **app nativa iOS (SwiftUI)** la pantalla de **Mercado** del
frontend Angular existente, como **segunda sección** de la app tras el
Presupuesto (F2), estrenando una **nueva pestaña** en el `TabView`. El Mercado
muestra los jugadores del computer disponibles para fichar, con la **puja
sugerida** (basada en el historial), el **rating Sofascore**, la **tendencia** de
valor y el resto de métricas, y permite al usuario **pujar** por un jugador y
**cancelar** una puja activa — la primera funcionalidad **de escritura** del
cliente nativo (F1 y F2 eran sólo lectura).

El tema visual (oscuro/neón) y el `DesignSystem` establecidos en F1/F2 son la
base; la **fuente de verdad del comportamiento** es la vista Angular
(`angular-app/src/app/features/market/`). No hay cambios de backend: el cliente
nativo **consume** los endpoints de Mercado ya existentes.

## Problema / oportunidad

- El usuario gestiona su equipo desde el iPhone. Hoy el Presupuesto (F2) ya vive
  en la app nativa, pero el **Mercado** — donde ocurre la acción de más valor
  (fichar jugadores) — sólo está disponible en la PWA Angular. Para decidir una
  puja el usuario necesita ver, en una sola pantalla, cuánto dinero tiene
  disponible, qué jugadores hay, su puja sugerida y sus indicadores (Sofascore,
  titularidad, tendencia).
- **Oportunidad**: llevar el Mercado completo a nativo da al usuario la pantalla
  de mayor valor accionable del producto directamente en el móvil, con la fluidez
  y el tema del cliente nativo, cerrando el salto entre "consultar" (F2) y
  "actuar" (pujar).

## Resultado esperado (verificable)

- En la app nativa aparece una **segunda pestaña "Mercado"** en el `TabView`,
  junto a "Presupuesto".
- La pantalla de Mercado muestra, para el campeonato activo:
  - un **banner de resumen del usuario** con Presupuesto, En pujas, Balance, Puja
    máxima y Disponible;
  - una **lista de cards de jugador**, cada una con avatar, nombre, equipo +
    logo, badges de Sofascore y % de titularidad, chip(s) de posición, y un grid
    de métricas (valor, tendencia, precio de mercado, puja sugerida, puntos,
    media);
  - un **selector de orden** descendente por el campo elegido (mismo patrón que
    F2).
- El usuario puede **pujar** por un jugador (introduciendo un importe validado
  entre el **precio de mercado** como mínimo y su **disponible para pujas** como
  tope efectivo) y **cancelar** una puja activa, con confirmación y mensaje de
  resultado; tras cada acción la pantalla se **refresca**. El usuario distingue
  una **puja aceptada** de una **rechazada por el backend** (resultado de
  negocio con mensaje), además del error de red, sin que la pantalla quede en
  estado ambiguo.
- El detalle de **Sofascore** de un jugador se puede abrir (rating + estadísticas
  ampliadas).
- El tema oscuro/neón y los componentes del `DesignSystem` se mantienen.

## Scope (límites)

- **Dentro**: pantalla de Mercado nativa (banner + cards + orden), nueva pestaña
  en el `TabView`, lectura de `GET /api/v1/market/today`, y **escritura** de puja
  (`POST /api/v1/market/bid`) y cancelación (`POST /api/v1/market/cancelbid`) con
  confirmación y validación de importe, más el **detalle Sofascore** como sheet
  nativa (Q1=A, Q3=A confirmados).
- **Fuera**: la **vista de tabla** del Angular (nativo reproduce sólo cards,
  igual que F2); la **Calculadora/Finanzas** (= F4, otro intent); cualquier
  **cambio de backend** o de contrato de API; otras secciones no portadas.
- **Supuesto de verificación arrastrado (riesgo de F1/F2)**: la fidelidad visual
  final se valida en dispositivo (iPhone 13 Pro) con `xtool`, no en el build WSL;
  algunos errores arm-only sólo afloran allí.

## Sources

- [desc] Initial description: intent F3 = "pantalla de Mercado reproduciendo la
  vista Angular, como segunda sección tras Presupuesto (F2), estrenando nueva
  pestaña en el `TabView`".
- [scope] Workflow-selected scope: `feature` (brownfield), espacio `default`.
- `angular-app/src/app/features/market/market.component.ts` — flujo `loadData`,
  `confirmBid`, `cancelBid`, `openSofascoreDetail`; `MarketPlayer`; `sortCards`
  descendente; `sortOptions`; `userInfo` (balance, team_value, max_bid,
  active_bids_total, available_for_bids).
- `angular-app/src/app/features/market/market.component.html` — banner de
  usuario, cards (header con avatar/nombre/equipo/badges/posición, grid de stats,
  acciones pujar/cancelar), favorite-card.
- `angular-app/src/app/features/market/bid-dialog.component.ts` — diálogo de puja:
  importe default = `suggestedBid`, mín = `marketPrice`, máx = `maxBid`,
  validación inline; resultado `{ confirmed, price }`.
- `angular-app/src/app/features/market/confirm-dialog.component.ts` — diálogo de
  confirmación de cancelación.
- `angular-app/src/app/features/market/sofascore-detail-dialog.component.html` —
  detalle Sofascore (rating hero + grid de ~16 stats, carga async con
  loading/error).
- `README.md` — endpoints `/api/v1/market/today` (GET), `/api/v1/market/bid`
  (POST); descripción funcional de Mercado.
- [memory:M1] `project.md` / `team.md`: tema Angular como fuente de verdad del
  diseño nativo; coste 0 € (sólo SDK de Apple); refresh token en Keychain, nunca
  en claro; identificadores en inglés y texto de usuario en castellano.
- Base reutilizable de F1/F2 en `ios/`: `FutmondoKit` (NetworkClient,
  AuthService, ActiveChampionshipStore, MoneyFormatter) y `FutmondoApp`
  (DesignSystem oscuro/neón, `RootTabView` con `TabView`).

## Assumptions & Open Questions

> **No quedan preguntas abiertas**: todos los supuestos de abajo están
> confirmados por el propietario (Q1–Q4 = A, 2026-10-20).

- [assumption] F3 incluye la **escritura** (pujar + cancelar) con confirmación y
  validación de importe. **Confirmado (Q1=A)**: es el valor real del Mercado;
  usa la sesión autenticada de F1 (Keychain, sin credenciales nuevas). El tope
  efectivo del importe es el **disponible para pujas** del usuario (el fallback
  exacto en cascada se decide en diseño).
- [assumption] La app nativa reproduce **sólo la vista de cards**, no la tabla
  (mismo criterio que F2).
- [assumption] La card muestra **todos los campos** de la card Angular, 1:1
  (Q2=A confirmado).
- [assumption] El selector de orden nativo ofrece los mismos campos que el
  Angular y ordena **siempre descendente** (mismo patrón que F2).
- [assumption] El detalle de **Sofascore** se presenta como una **sheet** nativa
  con carga asíncrona de estadísticas (endpoint aparte, no incluido en el payload
  de `/today`) — **dentro de alcance** (Q3=A confirmado).
- [assumption] El `TabView` pasa de 1 pestaña (Presupuesto) a **2 pestañas**
  (Presupuesto + Mercado) sin más secciones (Q4=A confirmado).
