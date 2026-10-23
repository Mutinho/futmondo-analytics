# Requirements Analysis — Preguntas de clarificación

Intent: `261022-favoritos-nativa` — pantalla nativa iOS **Favoritos** (SwiftUI).
Fuente de verdad: la vista Angular `angular-app/src/app/features/favorites/`
(leída: `favorites.component.ts/html`).

Contexto ya fijado (NO se pregunta): backend existente e inmutable
(`getMyFavorites`, `unfollow`); coste 0 € (SDK de Apple); identificadores/
comentarios en inglés y texto de usuario en castellano; lógica testeable en
`FutmondoKit` (XCTest), vistas SwiftUI en `FutmondoApp`; patrones nativos ya
validados (cards de Mercado/Calculadora, `RosterService`-style, `ConfirmSheet`,
haptics, `DataFreshness`, cross-invalidación); NO se crean favoritos (eso se
hace en la app de Futmondo). La pantalla es una pestaña más.

Responde cada `[Answer]:` con la letra elegida. Recomendación marcada con ⭐.

---

## A. Presentación (cards vs. tabla)

La web ofrece tabla densa + cards con toggle. En Mercado/Calculadora decidimos
solo cards nativas.

- A. Solo **cards** nativas, reutilizando la estética/tiles de Mercado y
  Calculadora (coherencia con las otras pantallas). ⭐
- B. Reproducir ambos modos (tabla + cards) con toggle.
- X. Other (please specify)

[Answer]: A

---

## B. Contenido de cada card

La web muestra: foto, nombre (enlace Sofascore), equipo, posición(es), rating
Sofascore, % titular, valor, tendencia, puntos (con jornadas), media (tooltip
casa/fuera/partidos).

- A. Reproducir todo el contenido, adaptando el tooltip de media (no hay hover
  en iOS) a un formato nativo: mostrar media y, si existen, casa/fuera y nº de
  partidos como texto secundario en la card (sin tooltip). ⭐
- B. Card compacta con lo esencial (foto, nombre, equipo, valor, tendencia,
  rating) y el resto en un detalle al tocar.
- X. Other (please specify)

[Answer]: A

---

## C. Acción de quitar de favoritos

La web usa un botón con confirmación (diálogo) y un snackbar de resultado.

- A. Botón/acción de **quitar** en cada card con **confirmación** (el
  `ConfirmSheet` nativo ya hecho) y aviso de resultado; recarga la lista tras el
  éxito. ⭐
- B. Swipe-to-delete nativo (deslizar la card) con confirmación.
- C. Ambos (botón + swipe).
- X. Other (please specify)

[Answer]: A

---

## D. Acceso a Sofascore

En la web, el nombre/foto enlaza al perfil de sofascore.com y el badge abre un
detalle. En Mercado tenemos el menú "…" con "Ver estadísticas" / "Ver perfil
Sofascore".

- A. Reproducir el mismo patrón de Mercado: menú "…" por card con "Ver perfil
  Sofascore" (abre la web) y, si aplica, "Ver estadísticas" (hoja de detalle). ⭐
- B. Solo enlace al perfil Sofascore (abrir web) al tocar la foto/nombre, sin
  hoja de detalle.
- C. Omitir el acceso a Sofascore en esta pantalla.
- X. Other (please specify)

[Answer]: A

---

## E. Orden y persistencia

La web ordena por valor/tendencia/sofascore/titularidad/puntos y persiste vista
en `localStorage`.

- A. Orden con `Menu` nativo (mismos criterios) persistido en `UserDefaults`;
  sin modo de vista que persistir (solo cards). ⭐
- B. Orden fijo por valor, sin selector.
- X. Other (please specify)

[Answer]: A

---

## X. Punto de entrada en la navegación

Hoy el `RootTabView` tiene Presupuesto, Mercado y Calculadora (3 pestañas).

- A. Nueva pestaña (4.ª) en la tab bar. ⭐
- B. Acceso desde otra pantalla (no ocupa pestaña).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Decisiones recogidas para la pantalla nativa Favoritos:

- Presentación: **solo cards** nativas, reutilizando la estética/tiles de
  Mercado y Calculadora (A).
- Contenido de card: todo el de la web (foto, nombre, equipo, posición(es),
  rating Sofascore, % titular, valor, tendencia, puntos con jornadas, media),
  convirtiendo el tooltip de media en **texto secundario** nativo (media +
  casa/fuera/partidos si existen), sin hover (A/B).
- Quitar de favoritos: **botón** por card con **confirmación** (`ConfirmSheet`
  nativo) + aviso de resultado + recarga tras éxito (A).
- Sofascore: mismo patrón de Mercado — menú "…" con "Ver perfil Sofascore"
  (abre web) y "Ver estadísticas" (hoja de detalle) (A).
- Orden: `Menu` nativo (valor/tendencia/sofascore/titularidad/puntos)
  persistido en `UserDefaults`; sin modo de vista (solo cards) (A).
- Navegación: **4.ª pestaña** en el `RootTabView`, junto a Presupuesto, Mercado
  y Calculadora (A).
- Estado vacío con mensaje (no hay favoritos libres). Reactiva al campeonato
  activo; caché en memoria `DataFreshness` + pull-to-refresh; cross-invalidación
  tras quitar un favorito si procede.
- NO se crean favoritos (se hace en la app de Futmondo). Backend inmutable
  (`getMyFavorites`, `unfollow`).

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
