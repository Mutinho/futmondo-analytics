# Requirements — Favoritos nativa iOS

Intent: `261022-favoritos-nativa` · Scope: `refactor` (plan `native-screen-frontend`)
· Fase: INCEPTION.

## Intent analysis

Llevar a la app nativa iOS (SwiftUI) la pantalla **Favoritos** de la PWA
Angular: el usuario ve, desde el iPhone, sus **jugadores libres marcados como
favoritos** (que marca en la app oficial de Futmondo y se actualizan con la
sincronización), con sus métricas, y puede **quitarlos de favoritos**. Es una
pantalla **frontend-only**, de lectura mayoritaria con una única escritura
reversible; no cambia el backend. Fuente de verdad del comportamiento y
look&feel: `angular-app/src/app/features/favorites/`
(`favorites.component.ts/html`).

## Functional requirements

### FR1 — Carga de datos
- FR1.1 Con un campeonato activo, cargar la lista de favoritos libres
  (`getMyFavorites(championshipId)`).
- FR1.2 Mostrar estado de carga; error legible en castellano si falla (mensaje
  del backend si lo hay).
- FR1.3 Recargar al **cambiar el campeonato activo** (observando la propiedad
  `@Observable` del `BudgetViewModel`, como en Mercado/Calculadora tras el bug
  fix — no el getter de `UserDefaults`).
- FR1.4 Reutilizar la caché en memoria `DataFreshness` (`loadIfNeeded()` al
  aparecer; recarga dura al cambiar de campeonato, TTL o pull-to-refresh).

### FR2 — Estado vacío
- FR2.1 Cuando no hay favoritos libres, mostrar un estado vacío con mensaje
  ("No tienes jugadores favoritos libres. Márcalos en la app de Futmondo y
  sincroniza.") e icono de estrella.

### FR3 — Listado (solo cards)
- FR3.1 Presentar la lista **solo en cards** nativas, reutilizando la estética/
  tiles de Mercado y Calculadora (hero, chips de posición, badges).
- FR3.2 Cada card muestra: foto del jugador, nombre, equipo (con escudo),
  **posición(es)** (una o dos), **rating Sofascore**, **% titular**, **valor**,
  **tendencia** (signo/flecha y color), **puntos** (con nº de jornadas),
  **media**. La media muestra, como **texto secundario** (no tooltip, no hay
  hover en iOS), los valores de **casa/fuera** y el nº de **partidos** cuando
  existan.
- FR3.3 Mostrar el recuento "N jugadores favoritos libres".

### FR4 — Orden
- FR4.1 Ofrecer orden por **valor / tendencia / rating Sofascore / % titular /
  puntos** mediante un `Menu` nativo (patrón de Mercado/Calculadora),
  descendente, con nils al final.
- FR4.2 Persistir el criterio de orden en `UserDefaults`.

### FR5 — Quitar de favoritos (unfollow)
- FR5.1 Cada card ofrece **quitar de favoritos** con **confirmación** nativa
  (`ConfirmSheet`: "¿Quitar a {nombre} de tus favoritos?").
- FR5.2 Al confirmar, invocar `unfollow(championshipId, playerId)`; mostrar
  aviso de resultado (éxito/error) en castellano.
- FR5.3 Tras un éxito, **recargar** la lista (el jugador desaparece).
- FR5.4 Guardia de escritura única: una operación a la vez
  (deshabilitar la acción mientras hay una en vuelo).

### FR6 — Acceso a Sofascore
- FR6.1 Cada card ofrece, en un menú "…" (patrón de Mercado): **"Ver perfil
  Sofascore"** (abre `sofascore_url` en el navegador del sistema) y **"Ver
  estadísticas"** (hoja de detalle Sofascore, reutilizando el componente de
  Mercado) cuando el jugador tenga datos.
- FR6.2 Si el jugador no tiene `sofascore_url`, la opción de perfil se omite o
  se deshabilita.

### FR7 — Coherencia cruzada (opcional/condicional)
- FR7.1 Quitar un favorito no cambia saldos, así que no requiere invalidar las
  cachés de Presupuesto/Mercado; si se detectara que alguna pantalla muestra el
  flag de favorito, se invalidaría. (Por defecto, sin cross-invalidación.)

### FR8 — Navegación
- FR8.1 Favoritos es una **nueva pestaña** (4.ª) del `RootTabView`, junto a
  Presupuesto, Mercado y Calculadora, con tinte verde neón y accesibilidad
  (icono + etiqueta). Icono: estrella (`star`/`star.fill`, SF Symbol nativo).

## Non-functional requirements

- NFR1 (Coste) Coste 0 €: solo SDK de Apple; `Package.swift` `dependencies: []`.
- NFR2 (Idioma) Identificadores/comentarios en inglés; texto de usuario en
  castellano.
- NFR3 (Arquitectura/testabilidad) Lógica testeable (DTO decode, sorter) en
  `FutmondoKit` con XCTest; vistas SwiftUI en `FutmondoApp` bajo
  `#if canImport(SwiftUI)`, validadas en dispositivo (llvm-cov no fiable en WSL).
- NFR4 (Look&feel) Reutiliza la estética nativa establecida (cards de Mercado/
  Calculadora, design system).
- NFR5 (Rendimiento) Scroll fluido a 120 Hz; carga con caché en memoria; sin
  escrituras de estado por frame.
- NFR6 (Accesibilidad) Etiquetas accesibles; métricas no solo-color; Reduce
  Motion en animaciones y haptics.
- NFR7 (Seguridad) Sin credenciales; preferencias en `UserDefaults` no
  sensibles; `NetworkClient` autenticado reutilizado; `NetworkError` no filtra
  URL/tokens.

## Constraints

- C1 Backend existente e **inmutable**: `getMyFavorites`, `unfollow`. No se crea
  ni modifica API. No se **crean** favoritos (solo se listan y se quitan).
- C2 Build/verificación en WSL (`swift build`/`swift test`); UI validada en
  dispositivo (`ios/scripts/install-app.sh`).
- C3 Swift 6 strict concurrency en el build de dispositivo: evitar `static var`
  de estado (usar `static let`).

## Assumptions

- A1 `getMyFavorites` devuelve jugadores con los campos que consume la vista
  Angular (`player_id`, `name`, `slug`, `position`, `position2`, `team`,
  `team_logo`, `value`, `change`, `points`, `average`, `home_average`,
  `away_average`, `matches`, `sofascore_rating`, `sofascore_url`, `starter_pct`,
  `status`); se confirmará contra el DTO al diseñar/implementar. (Razón:
  reutilizamos el mismo backend.)
- A2 `unfollow(championshipId, playerId)` devuelve un resultado con
  éxito/mensaje (como la web); se mapeará a `MarketWriteOutcome` reutilizado.
- A3 Las bases de imágenes (caras/escudos) son las de `MarketImageURL`.

## Out of scope

- O1 Crear/marcar favoritos (se hace en la app de Futmondo).
- O2 Modo tabla (solo cards; FR3.1).
- O3 Cambios de backend o de contrato de API.
- O4 CI, despliegue y operación.

## Open questions

- OQ1 Si `getMyFavorites`/`unfollow` aún no tienen cliente nativo en
  `FutmondoKit`, Functional Design decidirá si se extiende el `RosterService`
  existente (de la Calculadora) o se añade un `FavoritesService` nuevo
  reutilizando `NetworkClient`. No cambia el backend.
