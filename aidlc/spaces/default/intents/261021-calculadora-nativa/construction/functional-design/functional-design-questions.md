# Functional Design — Preguntas de diseño

Intent: `261021-calculadora-nativa` · Unidad única (plan a medida).
Consume: `requirements.md` (FR1–FR11, NFR1–NFR7, invariantes FR7).

Hallazgos del código nativo existente (anclan el diseño; no se pregunta sobre
ellos, se exponen como contexto):
- `MarketTodayResponse` + `MarketUserInfo` YA decodifican `balance` y
  `active_bids_total`, pero `MarketUserInfo` **no** expone `active_bids_count`
  (hoy lo ignora). La Calculadora lo necesita (FR2.3) → se añadirá el campo.
- **No** existe cliente nativo para `getMyRoster`, `getOnSale`, `sell`,
  `cancelSale` (solo hay `MarketService` para pujas). → confirma OQ1.
- `MarketPlayer` no cubre `buy_price`/`profit`/`status` del roster → la
  Calculadora necesita su propio modelo.

Responde cada `[Answer]:` con la letra elegida. Recomendación marcada con ⭐.

---

## Q1. Servicio nativo para las llamadas de la Calculadora (OQ1)

- A. Crear un **`RosterService`** nuevo en `FutmondoKit` (protocolo + impl
  `HTTPRosterService` sobre `NetworkClient`) con `fetchRoster`, `fetchOnSale`,
  `sell`, `cancelSale`; y **reutilizar** `MarketService.loadToday` para el
  bloque económico (balance + pujas). Sin tocar backend. ⭐
- B. Un único servicio "CalculatorService" que agrupe todo (roster + on-sale +
  market today + sell/cancel) en un solo protocolo.
- C. Extender `MarketService` con los métodos de roster/venta.
- X. Other (please specify)

[Answer]: A

---

## Q2. Dónde vive la lógica de las invariantes de dinero (FR7)

- A. Una **calculadora pura** `CalculatorMath` (struct sin estado) en
  `FutmondoKit` con funciones puras: `projectedValue(player, days)`,
  `selectedTotal(...)`, `onSaleTotal(...)`, `futureBalance(...)`; cubierta con
  XCTest (happy path + toggle ON/OFF + proyección). El view model orquesta y
  llama a estas funciones. ⭐
- B. Meter la lógica directamente en el view model (`CalculatorViewModel`) en
  `FutmondoApp`, sin tipo puro separado.
- X. Other (please specify)

[Answer]: A

---

## Q3. Modelo de selección y anti-doble-conteo (FR7.5)

En la web, al pasar el toggle de OFF→ON se **descartan** las selecciones
manuales de jugadores que están en venta (para que su valor cuente solo vía
`onSaleTotal`). ¿Cómo lo modelamos en nativo?

- A. Estado de selección = `Set<playerId>`; la lista seleccionable se recompone
  en memoria según el toggle (sin recargar), y al activar el toggle se **filtran**
  del Set los ids en venta. Igual que la web (`rebuildSelectable` +
  `setIncludeOnSale`). ⭐
- B. Permitir seleccionar en venta siempre y resolver el doble conteo solo en el
  cálculo final (más simple pero diverge de la web).
- X. Other (please specify)

[Answer]: A

---

## Q4. Precisión de los findings del revisor (R-01, R-02, R-03)

¿Fijamos en el diseño las tres aclaraciones que dejó el revisor de requisitos?

- A. Sí, las tres: (R-01) el dato "En venta" de la cabecera es permanente y solo
  se oculta la sección de cards en venta con el toggle OFF; (R-02) la venta parcial
  solo retira jugadores y recarga "en venta" cuando `sold == total`, en parcial
  solo informa; (R-03) "Plusvalía" = campo `profit` del roster, presentación con
  signo (verde/rojo), solo-presentación (no entra en las invariantes de FR7). ⭐
- B. Solo R-01 y R-02 (dejar "Plusvalía" sin fijar).
- C. Resolverlas en Code Generation, no en el diseño.
- X. Other (please specify)

[Answer]: A

---

## Q5. Estado de carga y errores de escritura (FR8.3/FR9)

- A. Reutilizar el patrón `MarketWriteOutcome` ya existente (accepted/rejected/
  networkError con mensaje localizado) para `sell`/`cancelSale`, con un
  resultado que distinga éxito total, parcial (`sold/total`) y error. ⭐
- B. Un tipo de resultado nuevo específico de la Calculadora.
- X. Other (please specify)

[Answer]: A — AJUSTE tras revisión adversarial (R-01): `cancelSale` sí reutiliza
`MarketWriteOutcome` (accepted/rejected/networkError), pero `sell` NO cabe en ese
enum porque debe transportar `sold`/`total` del backend `/roster/sell`
(`{success,total,sold,results}`). Por eso `sell` devuelve un tipo DEDICADO
`SellOutcome` (ver entities.md/rules.md) con los casos: `total(sold)` cuando
`sold==total`, `partial(sold,total)` cuando `0<sold<total`, `none` cuando
`sold==0`, y `networkError(message)`. Solo `total` retira jugadores y recarga
(BR8.2).

---

## Consolidated Summary Confirmation

Decisiones de diseño funcional de la Calculadora nativa:

- **Servicio**: `RosterService` nuevo en `FutmondoKit` (protocolo +
  `HTTPRosterService` sobre `NetworkClient`) con `fetchRoster`, `fetchOnSale`,
  `sell`, `cancelSale`; se reutiliza `MarketService.loadToday` para el bloque
  económico (balance + pujas). Sin tocar backend. Se añade `active_bids_count`
  a `MarketUserInfo`.
- **Lógica de dinero**: calculadora pura `CalculatorMath` en `FutmondoKit`
  (funciones puras `projectedValue`, `selectedTotal`, `onSaleTotal`,
  `futureBalance`), cubierta con XCTest; orquestada por el view model.
- **Selección / anti-doble-conteo**: `Set<playerId>`, lista seleccionable
  recompuesta en memoria según el toggle; al activar el toggle se filtran del
  Set los ids en venta (como la web).
- **Findings del revisor fijados**: R-01 (el ítem "En venta" de la cabecera es
  permanente; solo se oculta la sección de cards en venta con el toggle OFF),
  R-02 (venta parcial solo retira/recarga cuando `sold == total`; en parcial
  solo informa), R-03 ("Plusvalía" = `profit` del roster, solo-presentación con
  signo, fuera de las invariantes de FR7).
- **Resultado de escritura**: se reutiliza `MarketWriteOutcome` para
  `sell`/`cancelSale`, distinguiendo éxito total / parcial (`sold/total`) /
  error.

Does this all look correct before I generate the functional design artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
