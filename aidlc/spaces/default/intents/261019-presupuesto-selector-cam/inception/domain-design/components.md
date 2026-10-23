# Domain Design — Components (F2: Presupuesto nativo + selector de campeonato)

> Fase: inception (domain-design). Idioma: castellano; tokens técnicos verbatim en inglés.
> Target: SwiftUI + `FutmondoKit`/`FutmondoApp`. Reutiliza red/auth de F1; sin cambios de backend.

## Modelos (DTOs) — en `FutmondoKit` (lógica pura, `Codable`)

| Componente | Descripción | Trazabilidad |
|-----------|-------------|--------------|
| `TeamBudget` | DTO de un equipo con los **9 campos** (`team_id`, `team_name`, `balance`, `initial_budget`, `total_spent`, `total_income`, `purchases_count`, `sales_count`, `team_value`, `performance`, `max_bid`, `prizes`). Decodifica el `teams[]` de balances. | FR1.2 |
| `BalancesResponse` | `{success, championship_id, initial_budget, teams:[TeamBudget]}`. | FR1.1 |
| `Championship` | DTO de campeonato (`championship_id`, `name`, `initial_budget`, `has_clauses`, `excluded_teams`, y los extra: `money_per_point`, `money_per_ranking`, `dream_team_bonus`, `mvp_bonus`, `ranking_mode`, `users_to_rank` cuando estén). | FR3.1 |
| `ChampionshipsResponse` | `{success, championships:[Championship]}`. | FR3.1 |

Nota: aunque la lista muestre 4 métricas (refined-mockups), `TeamBudget` modela los 9 para no rehacer el DTO cuando llegue el detalle (tradeoff registrado).

## Lógica pura — en `FutmondoKit` (testeable con `swift test`)

| Componente | Responsabilidad | Trazabilidad |
|-----------|-----------------|--------------|
| `MoneyFormatter` | Formato abreviado M/K con signo (umbral, decimales, redondeo half-up, separador locale) según FR1.3. | FR1.3 |
| `TeamBudgetSort` | Orden descendente por clave (`balance`, `performance`, `max_bid`, `team_value`, `total_spent`, `total_income`). | FR2.1 |
| `BudgetService` (protocolo + impl) | Llama a `GET /api/v1/analytics/balances?championship_id=` vía `NetworkClient`; devuelve `BalancesResponse` o error tipado. | FR1.1, FR4.2 |
| `ChampionshipService` (protocolo + impl) | Llama a `GET /api/v1/user/championships` con fallback a `GET /api/v1/championships`; devuelve lista o error. | FR3.1, FR4.2 |
| `ActiveChampionshipStore` | Lee/escribe el `championship_id` activo en `UserDefaults`; expone el activo y permite cambiarlo. | FR3.2, FR3.3 |

## Vistas y estado — en `FutmondoApp` (SwiftUI, `#if canImport(SwiftUI)`)

| Componente | Responsabilidad | Trazabilidad |
|-----------|-----------------|--------------|
| `RootTabView` | `TabView` con una pestaña "Presupuesto" (Liquid Glass nativo). | FR5.1 |
| `BudgetView` | Pantalla dentro de `NavigationStack`: lista de `BudgetRow`, estados carga/error/vacío, toolbar con selector + orden. | FR1, FR4, US1 |
| `BudgetViewModel` (`@Observable`/`ObservableObject`) | Orquesta `BudgetService` + `ActiveChampionshipStore` + `TeamBudgetSort`; expone estado (loading/loaded/error/empty) y la lista ordenada. | FR1, FR2, FR4 |
| `BudgetRow` | Fila de equipo con las 4 métricas visibles, tokens de dinero (`DSColor`), tipografía (`DSFont`). | FR1.2, FR1.3, NFR3 |
| `ChampionshipMenu` | Contenido del `Menu` en la navigation bar (lista + activo marcado). | FR3.1 |

## Mapa de dependencias

```
RootTabView → BudgetView → BudgetViewModel ──→ BudgetService ──→ NetworkClient (F1)
                                        ├─→ ChampionshipService ─→ NetworkClient (F1)
                                        ├─→ ActiveChampionshipStore → UserDefaults
                                        ├─→ TeamBudgetSort
                                        └─(BudgetRow usa)→ MoneyFormatter + DSColor/DSFont (F1)
```

La capa testeable (`FutmondoKit`) no depende de SwiftUI; las vistas (`FutmondoApp`) dependen de la capa testeable y del DesignSystem.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/{requirements-analysis/requirements.md,user-stories/stories.md,refined-mockups/design-system-mapping.md}`
- `aidlc/spaces/default/codekb/futmondo-analytics/{architecture,component-inventory,api-documentation}.md`

## Assumptions & Open Questions

None.
