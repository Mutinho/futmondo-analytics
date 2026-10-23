# NFR Design — Security (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Diseño (cómo se cumplen SR1-SR3)

- **SR1 (sin credenciales en la UI)**: el `BudgetViewModel` sólo depende de los **protocolos públicos** de U1 (`BudgetService`, `ChampionshipService`, `ActiveChampionshipStore`), nunca del `NetworkClient` ni del `AuthService`; no ve tokens. En la transición a `error`, el VM toma el `localizedDescription` del error tipado de U1 **verbatim** (sin concatenar `championship_id`, la petición ni tokens) → `ErrorState` lo muestra. La garantía de no-fuga queda en U1 (sus tests cubren `NetworkError` y `DecodingError`); el VM no la reabre porque no compone strings con datos de petición.
- **SR2 (`UserDefaults`)**: el VM cambia el campeonato activo llamando a `ActiveChampionshipStore.setActive(id)` de U1; no escribe `UserDefaults` directamente ni guarda otra cosa que el id.
- **SR3 (sin red nueva)**: todas las llamadas pasan por los servicios de U1 → `NetworkClient` de F1 (HTTPS). U2 no instancia clientes ni URLs.

## Modelo de amenazas

Sin cambios respecto a F1/U1. U2 es presentación; no amplía superficie.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-requirements/security-requirements.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-design/security-design.md`

## Assumptions & Open Questions

None.
