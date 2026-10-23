# Feasibility Assessment — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (feasibility). Idioma: castellano; tokens técnicos verbatim en inglés.

## 1. Viabilidad técnica

**Alta.** Todo lo necesario ya existe en el stack:
- La **capa de red y auth** (`FutmondoKit`: `URLSessionNetworkClient`, `AuthService`, Keychain) de F1 cubre las llamadas autenticadas a los endpoints existentes.
- La **librería de diseño** (`DSColor`/`DSFont`/`DSSpacing` + componentes) de F1 da los tokens para reproducir la vista.
- Los **endpoints existentes** (`GET /api/v1/analytics/balances?championship_id=…`, `GET /api/v1/user/championships`) devuelven exactamente los datos que la web ya consume; no hay cambios de backend.
- El **selector** y la **lista** son patrones nativos estándar de SwiftUI (`Menu` en toolbar, `List`/`LazyVStack`).

## 2. Esfuerzo (orden de magnitud)

- Capa de datos nativa: modelos `Codable` para `TeamBudget`/`BalancesResponse` y `Championship` + dos llamadas de red (reutilizan el `NetworkClient`). Lógica pura testeable en `FutmondoKit`.
- Estado del campeonato activo: un store nativo (equivalente a `ChampionshipService`) con persistencia en `UserDefaults`.
- Vistas SwiftUI: `BudgetView` (lista ordenable) + el menú de selector en la navigation bar.

## 3. Riesgo dominante

**El patrón de navegación del selector sin sidebar.** En Angular el selector vive en el sidebar siempre visible; en iOS hay que elegir un idiom que sea "siempre accesible pero no invasivo" sin ese contenedor. Decidido Q1-A (menú en la navigation bar). Riesgo residual: que el menú de navigation bar resulte poco descubrible o incómodo con muchos campeonatos; se valida en dispositivo y, si molesta, se revisa el patrón (bajo/medio).

## 4. Riesgo secundario

**Formato y fidelidad de datos de dinero.** El `money` pipe de la web abrevia a M/K con signo para rendimiento; reproducirlo fielmente en Swift requiere replicar esa lógica de formateo (lógica pura, testeable en `FutmondoKit`). Bajo.

## 5. Viabilidad de coste

**0 €.** Sólo SDK de Apple; sin dependencias nuevas, sin cambios de infraestructura. Apple Developer Program (~99 €/año) sigue sin activarse en este intent (no hay publicación).

## 6. Veredicto

**Viable.** Sin bloqueantes. El único diseño genuinamente nuevo es el patrón del selector; el resto es portabilidad de UI sobre cimientos ya construidos y verificados en F1.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md`.
- `angular-app/src/app/features/budget/budget-overview/*`, `core/services/championship.service.ts`, `core/models/budget.model.ts` — fuente de verdad funcional.
- `ios/Sources/FutmondoKit/*`, `ios/Sources/FutmondoApp/DesignSystem/*` — cimientos de F1 reutilizados.
- [memory:M1] `project.md`/`team.md`: coste 0 €, tema Angular como fuente de verdad, verificación en dispositivo.

## Assumptions & Open Questions

None.
