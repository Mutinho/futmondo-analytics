# Business Rules — Favoritos nativa iOS

Fuente de verdad: el bloque `yaml`. Los `BRx.y` son claves de trazabilidad
permanentes.

```yaml
rules:
  # Grupo 1 — Carga y frescura
  - id: BR1.1
    statement: "Con un campeonato activo, cargar la lista de favoritos (fetchFavorites); loadIfNeeded al aparecer, recarga dura al cambiar campeonato / TTL / pull-to-refresh."
    category: policy
    applies_to: FavoritesState
    trigger: ".task / cambio de campeonato / refresh."
    logic: "reutilizar DataFreshness (TTL 180s, por campeonato)."
    violation: "Refetch en cada cambio de pestaña."
    source: FR1.1, FR1.4
  - id: BR1.2
    statement: "La recarga por cambio de campeonato observa la propiedad @Observable del BudgetViewModel (activeChampionship), no el getter de UserDefaults."
    category: policy
    applies_to: FavoritesState
    trigger: "onChange(activeChampionship?.championshipId)."
    logic: "SwiftUI solo rastrea propiedades observables; el getter de UserDefaults no dispara."
    violation: "La pantalla no recargaría al cambiar de campeonato (bug ya visto en Mercado/Calculadora)."
    source: FR1.3

  # Grupo 2 — Estado vacío
  - id: BR2.1
    statement: "Sin favoritos, mostrar estado vacío con mensaje e icono de estrella."
    category: policy
    applies_to: FavoritesState
    trigger: "Lista vacía tras carga con éxito."
    logic: "phase = empty → mensaje 'No tienes jugadores favoritos libres…'."
    violation: "Pantalla en blanco."
    source: FR2.1

  # Grupo 3 — Presentación (R-05 nulos/cero)
  - id: BR3.1
    statement: "Los valores nulos o cero que la web muestra como '-' se renderizan '-': starter_pct nulo, sofascore_rating nulo, change==0, average==0, points==0. change>0/<0 con flecha y color; ==0 sin flecha."
    category: policy
    applies_to: FavoritePlayer
    trigger: "Al renderizar la card."
    logic: "replica la lógica condicional de Angular (@if p.change !== 0, etc.); 0 NO es 'ausente' salvo donde la web lo trata así."
    violation: "Mostrar 0 € de tendencia como si fuera un dato, o el bug '0 = sin valor'."
    source: FR3.2
  - id: BR3.2
    statement: "La media muestra, como texto secundario, casa/fuera y nº de partidos cuando existan (no tooltip; no hay hover en iOS). ADAPTACIÓN nativa: en la web esta info vive en el tooltip de la tabla; en nativo se baja a la card como texto secundario para no perderla."
    category: policy
    applies_to: FavoritePlayer
    trigger: "Al renderizar la card con average > 0."
    logic: "media + (home_average, away_average, matches) como línea secundaria si no nulos."
    violation: "Perder la info casa/fuera que la web da en tooltip."
    source: FR3.2
  - id: BR3.3
    statement: "La card usa sofascore_rating para el badge y el orden; el campo rating se decodifica pero NO se muestra."
    category: policy
    applies_to: FavoritePlayer
    trigger: "Al renderizar/ordenar."
    logic: "badge = sofascore_rating; rating = informativo."
    violation: "Mostrar dos ratings y confundir al usuario (R-02)."
    source: FR3.2
  - id: BR3.4
    statement: "La lista se presenta SOLO como cards nativas (sin tabla), con un recuento 'N jugadores favoritos libres' encima."
    category: policy
    applies_to: FavoritesState
    trigger: "Al renderizar la lista con datos."
    logic: "LazyVGrid de FavoritePlayerCard; countLabel = players.count."
    violation: "Un modo tabla fuera de alcance, o perder el recuento (R-05 trazabilidad)."
    source: FR3.1, FR3.3

  # Grupo 4 — Orden
  - id: BR4.1
    statement: "Orden descendente por valor/tendencia/sofascore/titularidad/puntos, nils al final; persistido en UserDefaults."
    category: policy
    applies_to: FavoritesState
    trigger: "Selección en el Menu de orden / arranque."
    logic: "FavoritesSorter.sorted(players, by: field); preferencia en UserDefaults."
    violation: "Orden inestable o nils arriba."
    source: FR4.1, FR4.2

  # Grupo 5 — Quitar de favoritos
  - id: BR5.1
    statement: "Quitar de favoritos requiere confirmación (ConfirmSheet) antes de llamar al backend."
    category: validation
    applies_to: FavoritePlayer
    trigger: "Pulsar 'Quitar' en la card."
    logic: "mostrar ConfirmSheet; solo tras confirmar → unfollow."
    violation: "Quitar sin confirmación."
    source: FR5.1
  - id: BR5.2
    statement: "Tras un unfollow ACEPTADO, eliminar el jugador de la lista EN MEMORIA (sin nueva petición / sin reload) y animar la recolocación de las tarjetas restantes (withAnimation, respetando Reduce Motion); informar éxito."
    category: policy
    applies_to: FavoritesState
    trigger: "UnfollowOutcome.accepted."
    logic: "players.removeAll { $0.playerId == id } (eliminación optimista local), envuelto en withAnimation; NO reload()."
    violation: "Refetch innecesario al backend o lista sin reordenar/animar."
    source: FR5.2, FR5.3
  - id: BR5.3
    statement: "Guardia de escritura única: un unfollow a la vez (deshabilita la acción mientras hay uno en vuelo)."
    category: constraint
    applies_to: FavoritesState
    trigger: "Mientras isWriting."
    logic: "no-op si isWriting; set/reset isWriting alrededor de la llamada."
    violation: "Dobles llamadas concurrentes."
    source: FR5.4
  - id: BR5.4
    statement: "Tras un unfollow FALLIDO (rejected/networkError) la lista permanece intacta, se informa el error y la acción se re-habilita."
    category: policy
    applies_to: FavoritesState
    trigger: "UnfollowOutcome.rejected / .networkError."
    logic: "aviso error; sin reload; isWriting = false."
    violation: "Quitar un jugador de la UI que sigue siendo favorito en el backend (R-05)."
    source: FR5.2

  # Grupo 6 — Sofascore
  - id: BR6.1
    statement: "Menú '…' por card: 'Ver perfil Sofascore' solo si sofascore_url no vacío (abre web); 'Ver estadísticas' siempre (hoja de detalle por nombre), como la web."
    category: policy
    applies_to: FavoritePlayer
    trigger: "Abrir el menú '…'."
    logic: "perfil visible = sofascore_url != nil/empty; estadísticas siempre."
    violation: "Enlace de perfil roto cuando no hay URL."
    source: FR6.1, FR6.2

  # Grupo 7 — Navegación
  - id: BR7.1
    statement: "Favoritos es la 4.ª pestaña del RootTabView (icono estrella), tinte verde, accesible por icono + etiqueta."
    category: policy
    applies_to: FavoritesState
    trigger: "Montaje del RootTabView."
    logic: "Tab 'Favoritos' systemImage star / star.fill."
    violation: "N/A"
    source: FR8.1

  # Grupo 8 — Contrato de backend (inmutable)
  - id: BR8.1
    statement: "Rutas EXACTAS (confirmadas contra favorites.service.ts): fetchFavorites = GET /api/v1/favorites/my?championship_id=<id>; unfollow = POST /api/v1/favorites/unfollow?championship_id=<id>&player_id=<id> con body VACÍO y ambos ids como query params."
    category: constraint
    applies_to: FavoritesService
    trigger: "Toda llamada al backend de favoritos."
    logic: "unfollow NO usa body JSON (a diferencia de RosterService.cancelSale): ambos ids van en la query; ids percent-encoded."
    violation: "Adivinar query-vs-body rompería unfollow; cambiar el backend viola C1."
    source: FR1.1, FR5.2, C1
```

## Resumen de reglas

| Grupo | Tema | Reglas |
|---|---|---|
| BR1 | Carga/frescura (+ observación de campeonato) | BR1.1, BR1.2 |
| BR2 | Estado vacío | BR2.1 |
| BR3 | Presentación (nulos/cero, media, rating, cards/recuento) | BR3.1, BR3.2, BR3.3, BR3.4 |
| BR4 | Orden | BR4.1 |
| BR5 | Quitar de favoritos (confirmación, guardia, fallo) | BR5.1–BR5.4 |
| BR6 | Sofascore | BR6.1 |
| BR7 | Navegación | BR7.1 |
| BR8 | Contrato de backend (rutas exactas) | BR8.1 |
