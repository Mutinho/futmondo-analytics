# Scope Document — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (scope-definition). Idioma: castellano; tokens técnicos verbatim en inglés.
> Scope: `feature`. Brownfield.

## Ampliación de alcance aprobada (2026-10-20) — Detalle de equipo

El **detalle de equipo** (`budget-detail` de Angular), inicialmente diferido (ver "Out of Scope" abajo), pasa a **In Scope** por decisión del propietario durante la construcción:

- **FR6 (nuevo)** Pantalla de **detalle de equipo**: al tocar una card de equipo, navegar a una vista con: summary (saldo actual, gastado, ingresado) + lista de **Altas (Compras)** (jugador, precio, procedencia, fecha) y **Bajas (Ventas)** (jugador, precio, destino, fecha). Consume `GET /api/v1/analytics/balances/{team_id}` (`TeamDetailResponse`, ya documentado en codekb). Diseño iOS 26+: zoom/navigation transition desde la card, hero colapsable, números con `contentTransition(.numericText())`, segmented glass Compras|Ventas, filas con stagger/`scrollTransition`, haptics. Coste 0 €.
- Esto reduce el `Won't W1` previo: el detalle ya no es follow-up, sino parte de F2. La decisión queda trazada aquí y en requirements/diario.

## In Scope

1. **Pantalla de Presupuesto** nativa (SwiftUI), primera vista tras el login:
   - Lista/cards nativa (solo lectura) de equipos con las métricas de `TeamBudget` (saldo, valor plantilla, gastado, ingresado, ops, rendimiento, premios, puja máxima).
   - Tokens semánticos `money-positive`/`money-negative`; formato de dinero abreviado M/K con signo equivalente al `money` pipe.
   - **Ordenación** por las claves de la web (saldo, rendimiento, puja máxima, valor plantilla, gastado, ingresado) vía control nativo.
   - Estados de carga y error.
2. **Selector de campeonato** nativo:
   - Menú en la navigation bar (campeonato activo + chevron → lista).
   - Al cambiar: recarga Presupuesto del nuevo campeonato y **persiste en `UserDefaults`** (recuerda el último al reabrir).
3. **Capa de datos nativa** para consumir `GET /api/v1/analytics/balances` y `GET /api/v1/user/championships` (modelos `Codable`, reutilizando `NetworkClient`/auth de F1); lógica pura (formateo de dinero, estado del campeonato activo) testeable en `FutmondoKit`.
4. **Navegación mínima** (resuelve el finding advisory R-04, opción A′): **`TabView` nativo (tab bar de abajo) con UNA sola pestaña "Presupuesto"** como andamiaje, más `NavigationStack` + `.toolbar` arriba que aloja el título y el menú del selector. El `TabView` nativo adopta automáticamente **Liquid Glass de iOS 26** (coste 0 €, sin librerías) compilando con el SDK reciente. Futuras secciones sólo añaden pestañas, sin re-estructurar la raíz. **NO** se construyen más pestañas ni sus pantallas en este intent.

## Out of Scope (follow-up)

- **Detalle de equipo** (`budget-detail`) y **diálogo de premios** (`prizes-dialog`).
- **Tab bar global poblada** / shell de navegación con múltiples secciones → intent aparte. (En F2 sí entra el **andamiaje `TabView` con una sola pestaña**; lo diferido son las pestañas/secciones adicionales y sus pantallas.)
- Otras pantallas (Mercado, Finanzas, Sync, Evolución, etc.).
- Toggle tabla/cards (se adopta sólo list nativa, Q3-A).
- Cambios de backend, endpoints, datos, CI/CD o infraestructura: **ninguno**.

## Restricciones (del constraint-register)

C-01 coste 0 €; C-02 sin cambios de backend; C-03 tema Angular como fuente de verdad; C-04 sesión F1 intacta; C-05 verificación `swift test` + dispositivo; C-06 idioma; C-07 gate de CI; C-08 Color Sets en código (WSL).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md` (incl. finding R-04 diferido aquí).
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/feasibility/{feasibility-assessment,constraint-register}.md`.

## Assumptions & Open Questions

None.
