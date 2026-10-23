# Entities — Favoritos nativa iOS

Modelo de dominio de la pantalla Favoritos. Technology-agnostic. La fuente de
verdad es el bloque `yaml`; la prosa lo resume.

```yaml
entities:
  - name: FavoritePlayer
    description: >
      Un jugador libre marcado como favorito, devuelto por getMyFavorites. Es la
      fila (card) de la pantalla. Modelo propio (no reutiliza RosterPlayer):
      añade rating/home_average/away_average y no usa buy_price/profit.
    attributes:
      - { name: playerId, type: string, required: true, unique: true, wire: player_id }
      - { name: name, type: string, required: true }
      - { name: slug, type: string, required: true, notes: "clave de imagen (cara)" }
      - { name: position, type: string, required: false }
      - { name: position2, type: string, required: false }
      - { name: team, type: string, required: true }
      - { name: teamLogo, type: string, required: false, wire: team_logo }
      - { name: value, type: integer, required: true, notes: "valor de mercado, €" }
      - { name: change, type: integer, required: false, notes: "tendencia (€); 0 se renderiza '-' (BR-F3)" }
      - { name: points, type: integer, required: false }
      - { name: average, type: number, required: false }
      - { name: homeAverage, type: number, required: false, wire: home_average }
      - { name: awayAverage, type: number, required: false, wire: away_average }
      - { name: matches, type: integer, required: false }
      - { name: rating, type: number, required: false, notes: "campo informativo del backend; NO se muestra en la card (R-02). En la web es number no-opcional; se decodifica como opcional por TOLERANCIA (decodeIfPresent) para no romper el page-decode si el backend lo omite." }
      - { name: sofascoreRating, type: number, required: false, wire: sofascore_rating, notes: "badge y criterio de orden (R-02)" }
      - { name: sofascoreUrl, type: string, required: false, wire: sofascore_url }
      - { name: starterPct, type: integer, required: false, wire: starter_pct }
      - { name: status, type: string, required: false }
    constraints:
      - "playerId identifica de forma única al jugador dentro de una carga."

  - name: FavoritesState
    description: >
      Estado de la pantalla (no persiste salvo FavoritesPreferences). Reactivo
      al campeonato activo.
    attributes:
      - { name: players, type: "list<FavoritePlayer>", required: true, default: "empty" }
      - { name: sortField, type: "enum(value,change,sofascoreRating,starterPct,points)", required: true, default: value }
      - { name: isWriting, type: boolean, required: true, default: false, notes: "guardia de escritura única para unfollow (BR-F5.3)" }
      - { name: phase, type: "enum(idle,loading,data,empty,error)", required: true, default: idle }

  - name: FavoritesPreferences
    description: Preferencia persistida en UserDefaults (no sensible); solo el orden.
    attributes:
      - { name: sortField, type: string, required: true, default: value }

  - name: UnfollowOutcome
    description: >
      Resultado de quitar de favoritos. Reutiliza MarketWriteOutcome
      (accepted/rejected(message)/networkError), sin tipo nuevo.
    variants:
      - { name: accepted, notes: "recarga la lista (BR-F5.2)" }
      - { name: rejected, payload: "message: string", notes: "informa; lista intacta; acción re-habilitada (BR-F5.4)" }
      - { name: networkError, notes: "mensaje genérico; lista intacta; re-habilitada (BR-F5.4)" }
```

## Resumen

- **FavoritePlayer**: fila de la pantalla; modelo propio con home/away/rating.
  `sofascoreRating` manda el badge y el orden; `rating` se decodifica pero no se
  muestra (R-02).
- **FavoritesState** (en memoria) + **FavoritesPreferences** (`UserDefaults`,
  solo orden).
- **UnfollowOutcome** = `MarketWriteOutcome` reutilizado.
