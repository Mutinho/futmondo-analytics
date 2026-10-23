# Entities — Calculadora nativa iOS

Modelo de dominio de la pantalla Calculadora. Technology-agnostic. La fuente de
verdad es el bloque `yaml` siguiente; la prosa lo resume.

```yaml
entities:
  - name: RosterPlayer
    description: >
      Un jugador de la plantilla del usuario, con sus cifras económicas y de
      rendimiento. Es la fila seleccionable de la Calculadora. Mapea el roster
      que hoy consume la vista Angular (getMyRoster). No reutiliza MarketPlayer
      porque añade buy_price/profit/status.
    attributes:
      - { name: playerId, type: string, required: true, unique: true, wire: player_id }
      - { name: name, type: string, required: true }
      - { name: slug, type: string, required: true, notes: "clave de imagen (cara)" }
      - { name: position, type: string, required: false }
      - { name: position2, type: string, required: false }
      - { name: team, type: string, required: true }
      - { name: teamLogo, type: string, required: false, wire: team_logo, notes: "clave de escudo" }
      - { name: value, type: integer, required: true, notes: "valor de mercado actual, en €" }
      - { name: buyPrice, type: integer, required: false, wire: buy_price }
      - { name: profit, type: integer, required: false, notes: "plusvalía; solo-presentación (R-03), fuera de FR7" }
      - { name: change, type: integer, required: false, notes: "tendencia (€/día); puede ser negativa o nil" }
      - { name: points, type: integer, required: false }
      - { name: average, type: number, required: false }
      - { name: matches, type: integer, required: false }
      - { name: sofascoreRating, type: number, required: false, wire: sofascore_rating }
      - { name: sofascoreUrl, type: string, required: false, wire: sofascore_url }
      - { name: starterPct, type: integer, required: false, wire: starter_pct }
      - { name: status, type: string, required: false }
    constraints:
      - "playerId identifica de forma única al jugador dentro de una carga."

  - name: OnSalePlayer
    description: >
      Un jugador que el usuario ya tiene puesto a la venta (getOnSale). Su valor
      cuenta en onSaleTotal. Subconjunto de campos de RosterPlayer.
    attributes:
      - { name: playerId, type: string, required: true, unique: true, wire: player_id }
      - { name: name, type: string, required: true }
      - { name: slug, type: string, required: true }
      - { name: team, type: string, required: false }
      - { name: value, type: integer, required: true }

  - name: EconomySnapshot
    description: >
      El bloque económico del usuario, leído del user_info de
      GET /api/v1/market/today. Fuente de balance y de las pujas comprometidas.
    attributes:
      - { name: balance, type: integer, required: true, notes: "saldo actual, en €" }
      - { name: activeBidsTotal, type: integer, required: true, wire: active_bids_total }
      - { name: activeBidsCount, type: integer, required: false, default: 0, wire: active_bids_count, notes: "NUEVO campo en MarketUserInfo. DEBE añadirse como OPCIONAL-con-default (decodeIfPresent ?? 0) y con parámetro de init por defecto, para NO romper el decode existente de market/today ni los callers del memberwise init (evita regresión en Mercado). R-02." }

  - name: CalculatorState
    description: >
      Estado de simulación de la pantalla (no se persiste salvo las preferencias
      de CalculatorPreferences). Dirige el resumen y la lista seleccionable.
    attributes:
      - { name: selectedIds, type: "set<string>", required: true, default: "empty", notes: "ids de RosterPlayer seleccionados" }
      - { name: includeOnSale, type: boolean, required: true, default: true, notes: "toggle 'Incorporar jugadores en venta' (FR3)" }
      - { name: daysAhead, type: integer, required: true, default: 0, min: 0, notes: "días a futuro derivados de la fecha elegida (FR4)" }
      - { name: sortField, type: "enum(projectedValue,value,change,profit)", required: true, default: projectedValue }
    constraints:
      - "Invariante FR7.5: ningún playerId en venta puede estar a la vez en selectedIds y contar vía onSaleTotal."

  - name: CalculatorPreferences
    description: >
      Preferencias persistidas en UserDefaults (no sensibles). Solo el toggle y
      el orden; no hay modo de vista porque la pantalla es solo cards.
    attributes:
      - { name: includeOnSale, type: boolean, required: true, default: true, notes: "cualquier valor distinto del literal 'false' resuelve a true (BR3.x)" }
      - { name: sortField, type: string, required: true, default: projectedValue }

  - name: SellOutcome
    description: >
      Resultado DEDICADO de la operación de poner a la venta (sell). NO reutiliza
      MarketWriteOutcome porque debe transportar sold/total del backend
      /roster/sell ({success,total,sold,results}) para distinguir éxito total de
      parcial (BR8.2, R-01). Tipo-suma (enum).
    variants:
      - { name: total, payload: "sold: integer", notes: "sold == total; retira jugadores y recarga en venta" }
      - { name: partial, payload: "sold: integer, total: integer", notes: "0 < sold < total; solo informa, NO retira ni recarga" }
      - { name: none, payload: "total: integer", notes: "sold == 0; solo informa el fallo" }
      - { name: networkError, payload: "message: string", notes: "error de red/decodificación, mensaje localizado" }
```

## Resumen

- **RosterPlayer** es la fila seleccionable; añade `profit` (plusvalía,
  solo-presentación) y `change` (tendencia) sobre lo que ya modela `MarketPlayer`.
- **OnSalePlayer** son los jugadores ya en venta (su valor va a `onSaleTotal`).
- **EconomySnapshot** reutiliza `GET /api/v1/market/today`; se añade
  `activeBidsCount` al DTO existente `MarketUserInfo`.
- **CalculatorState** es el estado de simulación en memoria; **CalculatorPreferences**
  es lo único persistido (`UserDefaults`).
