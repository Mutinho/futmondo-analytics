# Intent Capture — Preguntas (F3 Mercado)

> Modo **Guíame**: cada pregunta lleva opciones con una **recomendación**;
> decides tú. Responde escribiendo tu elección en el tag `[Answer]:` (o dímelo en
> el chat y lo relleno). La opción `X. Other (please specify)` está siempre
> disponible.

---

## Q1 — Alcance de escritura (DECISIÓN CLAVE)

El Mercado, a diferencia de Presupuesto (F2, sólo lectura), incluye **escritura**:
pujar por un jugador y cancelar una puja activa afectan al estado compartido del
campeonato (se propagan a Futmondo). Sería la **primera operación de escritura**
del cliente nativo.

¿Qué alcance tiene F3?

- **A.** Lectura + orden + escritura completa: banner, cards, selector de orden,
  **pujar** (con diálogo de importe validado) y **cancelar** puja (con
  confirmación). ← **recomendada**: es el valor real del Mercado; reproduce la
  vista Angular completa y la sesión autenticada de F1 ya soporta la escritura.
- **B.** Sólo lectura + orden en esta iteración (banner, cards, orden); pujar y
  cancelar se difieren a un intent posterior.
- **C.** Lectura + orden + sólo pujar (sin cancelar) en F3; cancelar se difiere.
- **X.** Other (please specify)

[Answer]: A

---

## Q2 — Campos de la card de jugador

La card Angular muestra: avatar (link Sofascore), nombre (link), equipo + logo,
badge Sofascore, badge % titular, chip(s) de posición (position + position2), y
un grid de métricas: VALOR, TENDENCIA (▲/▼), PRECIO MERCADO, SUGERIDA (acento),
PUNTOS (+ nº de partidos), MEDIA.

¿Qué reproducimos en la card nativa?

- **A.** Todos los campos anteriores, 1:1 con la card Angular. ← **recomendada**:
  fidelidad con la fuente de verdad; es la información que el usuario usa para
  decidir una puja.
- **B.** Un subconjunto esencial (nombre, equipo, valor, precio mercado, puja
  sugerida, Sofascore) y el resto se difiere.
- **X.** Other (please specify)

[Answer]: A

---

## Q3 — Detalle Sofascore

Al tocar el badge Sofascore, la web abre un diálogo con el rating grande y un
grid de ~16 estadísticas, cargadas de forma **asíncrona** desde un **endpoint
aparte** (no viene en el payload de `/market/today`), con estados loading/error.

¿Entra en el alcance de F3?

- **A.** Sí, como **sheet** nativa con carga asíncrona (rating + stats, estados
  loading/error). ← **recomendada**: completa la paridad con la web y es una
  decisión informada del usuario para la puja.
- **B.** Diferir el detalle Sofascore a un intent posterior; en F3 el badge sólo
  muestra el rating en la card (sin sheet de detalle).
- **X.** Other (please specify)

[Answer]: A

---

## Q4 — Navegación / pestañas

Hoy el `TabView` nativo tiene **1 pestaña** (Presupuesto). F3 añade Mercado.

- **A.** `TabView` con **2 pestañas**: "Presupuesto" + "Mercado" (Mercado como
  segunda sección). ← **recomendada**: coincide con la descripción del intent y
  deja la Calculadora (F4) para su propio intent.
- **X.** Other (please specify)

[Answer]: A

---

## Assumption Confirmation

Si no respondes pregunta por pregunta, puedo asumir las opciones recomendadas
(Q1=A, Q2=A, Q3=A, Q4=A) y seguir.

- **A. Accept assumptions** — sigo con las recomendadas (escritura completa
  incluida).
- **B. Convert to follow-up questions** — prefiero responder las preguntas una a
  una antes de continuar.

[Answer]: A. Accept assumptions

---

## Consolidated Summary Confirmation

Resumen de lo capturado en Intent Capture & Framing para F3 = Mercado
(intent `261020-mercado-pujas`):

- **Qué**: pantalla de Mercado nativa (SwiftUI) que reproduce la vista Angular,
  como **segunda pestaña** del `TabView` tras Presupuesto (Q4=A).
- **Lectura**: banner de usuario (Presupuesto, En pujas, Balance, Puja máxima,
  Disponible) + lista de **cards** de jugador (campos 1:1 con la card Angular,
  Q2=A) + selector de **orden descendente** (mismos campos que F2).
- **Escritura (confirmada, Q1=A)**: **pujar** (`POST /api/v1/market/bid`, importe
  validado entre precio de mercado y disponible para pujas) y **cancelar**
  (`POST /api/v1/market/cancelbid`, con confirmación); mensaje de resultado que
  distingue aceptada/rechazada por backend y error de red; refresco tras cada
  acción. Usa la sesión autenticada de F1 (Keychain), sin credenciales nuevas.
- **Detalle Sofascore (Q3=A)**: sheet nativa con carga asíncrona (rating + stats).
- **Fuera de alcance**: vista de tabla (sólo cards), Calculadora/Finanzas (= F4),
  cualquier cambio de backend/contrato de API.
- **Reviewer advisory** (product-lead) sobre `intent-statement.md`: **READY**,
  0 Major; 4 Minor aplicados (tope de importe, resultado aceptada/rechazada,
  sección de supuestos sin preguntas abiertas, alineación Sofascore en
  stakeholder-map).
- **Siguiente etapa**: Market Research.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo antes de continuar.

[Answer]: Looks correct
