# Requirements Analysis — Preguntas de clarificación

Intent: `261021-calculadora-nativa` — pantalla nativa iOS **Calculadora** (SwiftUI).
Fuente de verdad del comportamiento y look&feel: la vista Angular
`angular-app/src/app/features/calculator/` (leída: `calculator.component.ts/html/scss`).

Contexto ya fijado (NO se pregunta): backend existente e inmutable
(`getMyRoster`, `GET /api/v1/market/today` con `balance` + `active_bids_total`/
`active_bids_count`, `getOnSale`, `sell`, `cancelSale`); coste 0 € (SDK de Apple);
identificadores/comentarios en inglés y texto de usuario en castellano; lógica
testeable en `FutmondoKit` (XCTest), vistas SwiftUI en `FutmondoApp`; patrones
nativos ya validados en `knowledge/aidlc-shared/native-ios-ui-patterns.md`.

Responde en cada `[Answer]:` con la letra elegida (o texto libre en `X`). Las
opciones recomendadas están marcadas con ⭐.

---

## A. Alcance de las acciones de escritura (poner a la venta / cancelar venta)

En la web, la Calculadora NO es solo una calculadora: permite **poner jugadores
a la venta** (`sell`, con diálogo de confirmación) y **cancelar una venta**
(`cancelSale`). Son escrituras reales contra el backend.

- A. Incluir ambas acciones de escritura (poner a la venta + cancelar venta),
  igual que la web. ⭐
- B. Solo lectura/simulación en esta primera versión (saldo futuro, proyección,
  selección) y dejar poner/cancelar venta para un intent posterior.
- C. Incluir poner a la venta, pero no cancelar venta todavía.
- D. Incluir cancelar venta, pero no poner a la venta todavía.
- X. Other (please specify)

[Answer]: A

---

## B. Vistas tabla vs. cards en nativo

La web ofrece dos modos (tabla densa con columnas ordenables, y cards), con un
toggle persistido y, en móvil, arranca en cards. En iPhone una tabla ancha de 8
columnas no encaja bien.

- A. Reproducir ambos modos (tabla + cards) con toggle persistido, como la web.
- B. Solo **cards** (tiles), que es el patrón nativo ya usado en Mercado y lo
  natural en iPhone; el orden se mantiene con un `Menu`. ⭐
- C. Solo una **lista/tabla** compacta nativa (filas), sin cards.
- D. Cards en vertical y tabla solo en horizontal (landscape).
- X. Other (please specify)

[Answer]: B — reutilizar la MISMA estética y los tiles/cards ya construidos en la pantalla de Mercado de iOS (mismo tratamiento visual: hero, glass/neon, tipografía y chips), adaptando su contenido a los campos de la Calculadora (valor actual, tendencia, valor proyectado, plusvalía, selección). Solo cards; el orden con un `Menu`.

---

## C. Selección múltiple e interacción de "Vender (N)"

La web selecciona con checkboxes (fila o card) y muestra un FAB flotante
"Vender (N)".

- A. Tap en la card alterna selección (check visible) + botón flotante
  "Vender (N)" que abre confirmación, igual que la web. ⭐
- B. Modo selección explícito (botón "Seleccionar") con barra de acciones
  inferior, estilo Fotos de iOS.
- C. Swipe actions nativas por fila (deslizar para vender) sin selección múltiple.
- X. Other (please specify)

[Answer]: A

---

## D. Proyección por fecha

La web tiene un `datepicker` (fecha de venta) y calcula `valor + tendencia×días`,
mostrando el valor proyectado y el delta por jugador.

- A. Reproducir con un `DatePicker` nativo (rueda/calendario) acotado a hoy o
  después; mostrar "N días a futuro" y el valor proyectado por jugador. ⭐
- B. Reemplazar la fecha por un **stepper/slider de días** a futuro (0–N), más
  directo en móvil que elegir una fecha.
- C. Ofrecer ambos (fecha o días), el usuario elige.
- D. Omitir la proyección en esta versión (solo valores actuales).
- X. Other (please specify)

[Answer]: A

---

## E. Persistencia de preferencias (modo de vista, toggle "incorporar en venta", orden)

La web persiste estas preferencias en `localStorage`. En nativo el equivalente
es `UserDefaults` (no sensible, no son credenciales).

- A. Persistir en `UserDefaults` el modo de vista, el toggle "Incorporar
  jugadores en venta" y el criterio de orden, como la web. ⭐
- B. Persistir solo el toggle de "incorporar en venta" (el más cargado de
  lógica); vista y orden vuelven a su valor por defecto en cada arranque.
- C. No persistir nada; siempre arrancar con valores por defecto.
- X. Other (please specify)

[Answer]: A — con el matiz de que, al elegir solo cards en B), ya no hay modo de vista que persistir: se persisten en `UserDefaults` el toggle "Incorporar jugadores en venta" y el criterio de orden.

---

## X. Punto de entrada en la navegación

Hoy el `RootTabView` nativo tiene Presupuesto y Mercado. ¿Dónde vive la Calculadora?

- A. Nueva pestaña en la tab bar (3.ª pestaña), junto a Presupuesto y Mercado. ⭐
- B. Botón/acceso dentro de la pantalla de Presupuesto (no ocupa pestaña).
- C. Acceso desde Mercado.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones recogidas para la Calculadora nativa iOS:

- Acciones de escritura: se incluyen **poner a la venta** (con confirmación) y
  **cancelar venta**, igual que la web (A).
- Presentación: **solo cards** nativos, reutilizando la **misma estética y los
  tiles ya construidos en la pantalla de Mercado de iOS** (hero, glass/neon,
  tipografía, chips), con el contenido adaptado a la Calculadora (valor actual,
  tendencia, valor proyectado, plusvalía, selección); orden con un `Menu` (B).
- Selección: **tap en la card** alterna selección (check visible) + botón
  flotante **"Vender (N)"** que abre confirmación (A).
- Proyección: **`DatePicker` nativo** acotado a hoy o después; se muestra
  "N días a futuro" y el valor proyectado por jugador = valor + tendencia×días (A).
- Persistencia: **`UserDefaults`** para el toggle "Incorporar jugadores en
  venta" y el criterio de orden (no hay modo de vista que persistir al ser solo
  cards) (A/E).
- Navegación: **nueva pestaña** (3.ª) en el `RootTabView`, junto a Presupuesto y
  Mercado (A).
- Invariantes de dinero (de la fuente de verdad Angular, a fijar como criterios
  de aceptación): Saldo futuro = saldo + total seleccionados + (en venta si el
  toggle ON) − pujas activas; anti-doble-conteo al activar/desactivar el toggle;
  proyección por fecha; cifras positivas/negativas con la semántica money.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
