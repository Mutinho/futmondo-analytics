# Functional Design — Preguntas de diseño

Intent: `261022-favoritos-nativa` · Unidad única.
Consume: `requirements.md` (FR1–FR8).

Hallazgos del código nativo existente (anclan el diseño; no se preguntan):
- Existe `RosterService`/`HTTPRosterService` (Calculadora) con el patrón
  actor+`NetworkClient` y `RosterPlayer`/`RosterResponse` tolerante (array raíz
  o envuelto). `FavoritePlayer` se parece a `RosterPlayer` pero **añade**
  `rating`, `home_average`, `away_average` y **no usa** `buy_price`/`profit`.
- `getMyFavorites` y `unfollow` son endpoints DISTINTOS de los de roster; la
  vista Angular usa `FavoritesService`.
- `ConfirmSheet`, `MarketWriteOutcome`, `DataFreshness`, `MarketImageURL`,
  `CalculatorSorter` (patrón de sorter) y el menú "…" Sofascore de Mercado ya
  existen y se reutilizan.

Responde cada `[Answer]:` con la letra. Recomendación marcada con ⭐.

---

## Q1. Servicio nativo para Favoritos (OQ1)

- A. Crear un **`FavoritesService`** nuevo en `FutmondoKit` (protocolo +
  `HTTPFavoritesService` actor sobre `NetworkClient`) con `fetchFavorites`
  (`GET /api/v1/favorites`-style, confirmando la ruta exacta contra la fuente
  Angular `favorites.service.ts`) y `unfollow`
  (`unfollow(championshipId, playerId)` → `MarketWriteOutcome`). Sin tocar
  backend. ⭐
- B. Extender `RosterService` con `fetchFavorites`/`unfollow`.
- X. Other (please specify)

[Answer]: A

---

## Q2. Modelo `FavoritePlayer` (R-02 — dos campos de rating)

La vista Angular tiene DOS campos: `rating` (number) **y** `sofascore_rating`
(number | null). La card pinta el badge con `sofascore_rating`.

- A. Modelar **`FavoritePlayer`** propio (Codable) con los campos que usa la
  web, incluyendo ambos: `sofascore_rating` (el que pinta el badge y ordena) y
  `rating` (decodificado pero **solo-informativo**, no se muestra salvo que se
  confirme uso); documentar que la card usa `sofascore_rating`. Añadir
  `home_average`/`away_average`/`matches` para el texto secundario de media. ⭐
- B. Reutilizar `RosterPlayer` tal cual (ignorando que faltan rating/home/away).
- X. Other (please specify)

[Answer]: A

---

## Q3. Criterio de disponibilidad de Sofascore (R-03)

En la web, "Ver detalle" se abre para cualquier jugador; el enlace al perfil
depende de `sofascore_url`.

- A. "Ver perfil Sofascore" disponible solo si `sofascore_url` no es vacío;
  "Ver estadísticas" (hoja de detalle) disponible siempre (igual que la web),
  usando el nombre del jugador para la consulta. ⭐
- B. Ambas opciones condicionadas a `sofascore_rating` no nulo.
- X. Other (please specify)

[Answer]: A

---

## Q4. Render de valores nulos/cero y fallo de unfollow (R-05)

- A. Fijar como reglas: (1) campos nulos o cero que la web muestra como "-"
  (`starter_pct` nulo, `sofascore_rating` nulo, `change == 0`, `average == 0`,
  `points == 0`) se renderizan "-" / sin flecha, replicando la lógica
  condicional de la web (evita el bug "0 = ausente"); (2) tras un `unfollow`
  fallido la lista **permanece intacta**, se informa el error y la acción se
  **re-habilita** (guardia de escritura liberada). ⭐
- B. Dejar estos detalles para Code Generation sin fijarlos como reglas.
- X. Other (please specify)

[Answer]: A

---

## Q5. Orden y resultado de escritura

- A. `FavoritesSorter` (patrón de `CalculatorSorter`) por
  valor/tendencia/sofascore/titularidad/puntos, descendente, nulls al final;
  `unfollow` devuelve `MarketWriteOutcome` (accepted/rejected/networkError)
  reutilizado. ⭐
- B. Otro enfoque.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Decisiones de diseño funcional de Favoritos:

- **Servicio**: `FavoritesService` nuevo (protocolo + `HTTPFavoritesService`
  actor sobre `NetworkClient`): `fetchFavorites(championshipId)` y
  `unfollow(championshipId, playerId)` → `MarketWriteOutcome`. Rutas exactas
  confirmadas contra la fuente Angular. Backend inmutable.
- **Modelo**: `FavoritePlayer` propio (Codable); la card usa `sofascore_rating`
  (badge/orden), decodifica `rating` como solo-informativo; añade
  `home_average`/`away_average`/`matches` para el texto secundario de media.
- **Sofascore**: "Ver perfil" si `sofascore_url` no vacío; "Ver estadísticas"
  siempre (como la web).
- **Nulos/cero (R-05)**: "-" para `starter_pct`/`sofascore_rating` nulos,
  `change==0`, `average==0`, `points==0` (replica la lógica condicional de la
  web; evita el bug "0 = ausente").
- **Fallo de unfollow (R-05)**: tras error, la lista permanece intacta, se
  informa y la acción se re-habilita (guardia liberada); en éxito, recarga.
- **Orden**: `FavoritesSorter` (patrón `CalculatorSorter`) por
  valor/tendencia/sofascore/titularidad/puntos, descendente, nulls al final.
- Reutiliza `ConfirmSheet`, `DataFreshness`, `MarketImageURL`, menú "…"
  Sofascore de Mercado. 4.ª pestaña (icono estrella).

Does this all look correct before I generate the functional design artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
