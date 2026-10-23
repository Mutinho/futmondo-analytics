# Intent Statement — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (intent-capture). Idioma: castellano; tokens técnicos verbatim en inglés.
> Scope: `feature`. Brownfield. Fuente de verdad de diseño: tema Angular (`angular-app/src/styles.scss`) + paridad funcional con `features/budget/budget-overview`.

## Intent

Construir en **SwiftUI** (sólo SDK de Apple, coste 0 €), sobre la librería de diseño nativa ya existente (`FutmondoKit`/`FutmondoApp` DesignSystem), la **primera pantalla real tras el login**: la vista de **Presupuesto** (saldos por equipo), y resolver el **patrón de selección de campeonato** de forma nativa iOS — siempre accesible pero no invasivo — dado que la app nativa **no tendrá sidebar** (donde vive hoy el selector en Angular).

No hay dashboard: tras el login, el usuario aterriza en Presupuesto.

## Problema / oportunidad

La app nativa iOS (F1) hoy sólo cubre el login revestido. Para ser útil necesita su primera pantalla de valor — el Presupuesto, que es la vista de referencia del producto — y una forma nativa de cambiar de campeonato. El selector de Angular (dropdown en el sidebar) no tiene equivalente directo sin sidebar: hay que diseñar un patrón iOS idiomático (p. ej. menú en la navigation bar) que esté siempre a mano sin robar espacio a la pantalla.

## Qué entra (alcance preliminar)

1. **Pantalla de Presupuesto** nativa: lista de equipos con sus métricas (`TeamBudget`: saldo, valor plantilla, gastado, ingresado, ops, rendimiento, premios, puja máxima), con los tokens semánticos `money-positive`/`money-negative`, reproduciendo la jerarquía visual de la vista Angular. Incluye **ordenación** por las claves de la web (saldo, rendimiento, puja máxima, valor plantilla, gastado, ingresado; Q4) y **formato de dinero abreviado M/K** equivalente al `money` pipe (asunción (b)). Consume el endpoint existente de balances.
2. **Selector de campeonato** nativo, siempre accesible y no invasivo, que fija el campeonato activo (equivalente a `ChampionshipService`: lista, selección persistida, recarga reactiva de la pantalla). Criterio verificable (Q5): al cambiar de campeonato **recarga la pantalla de Presupuesto** y **persiste la selección en `UserDefaults`**, de modo que al reabrir la app recuerde el último campeonato.

## Qué NO entra (límites preliminares, a confirmar en scope-definition)

- Detalle de equipo (`budget-detail`), diálogo de premios, ordenación/toggle avanzados: candidatos a follow-up, no núcleo de F2.
- Otras pantallas (Mercado, Finanzas, Sync, etc.).
- Cambios de backend, endpoints o datos: **ninguno**; se consumen las APIs existentes tal cual.
- Navegación global completa (tab bar de toda la app): se diseña sólo lo necesario para alojar Presupuesto + selector; la navegación integral puede ser un intent aparte. **Pendiente para scope-definition** (finding advisory del reviewer): precisar el mínimo de navegación que entra (p. ej. una sola pantalla con navigation bar, sin tab bar global) para blindar el límite y evitar scope creep.

## Restricciones durables (de memoria)

- **Coste 0 €**: sólo SDK de Apple; sin dependencias de pago ni tooling de diseño de pago.
- **Fuente de verdad de diseño**: tema Angular Material 3 (verde/violeta, `Roboto`, claro/oscuro, tokens de dinero); Apple HIG donde no haya equivalente 1:1.
- **Seguridad**: no se toca el modelo de sesión; refresh token en Keychain, access token en memoria (intactos de F1).
- **Verificación**: lógica testeable en `FutmondoKit` con `swift test`; vistas SwiftUI validadas en el iPhone 13 Pro (cobertura no numérica en WSL). **Supuesto/riesgo arrastrado de F1**: la validación de UI en dispositivo depende de un iPhone 13 Pro y del arnés `xtool` disponibles; es un método heredado de F1, no un arnés automatizado confirmado, y se da como supuesto a confirmar (no garantizado).

## Sources

- [desc] Initial description: descripción del trabajo F2 aportada por el propietario (Presupuesto como primera vista tras login; sin dashboard; selector de campeonato siempre visible y no invasivo, repensado sin sidebar).
- [scope] Workflow-selected scope: `feature`.
- `angular-app/src/app/features/budget/budget-overview/budget-overview.component.{html,ts}` — vista de Presupuesto de referencia.
- `angular-app/src/app/core/models/budget.model.ts` — modelo `TeamBudget`/`BalancesResponse`.
- `angular-app/src/app/core/services/championship.service.ts` — comportamiento del selector de campeonato (lista, selección persistida, `activeId` reactivo).
- [memory:M1] `project.md`/`team.md`: coste 0 €, tema Angular como fuente de verdad, librería de diseño nativa ya construida.

## Assumptions & Open Questions

None.
