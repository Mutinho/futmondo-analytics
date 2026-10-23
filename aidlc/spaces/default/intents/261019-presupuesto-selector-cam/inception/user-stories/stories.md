# User Stories — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (user-stories). Idioma: castellano; tokens técnicos verbatim en inglés.
> Formato BDD (Given/When/Then). MoSCoW. Trazabilidad a FR/NFR.

## US1 — Ver el presupuesto del campeonato activo (Must)
**Como** propietario que acaba de entrar en la app, **quiero** ver los saldos por equipo del campeonato activo, **para** controlar el presupuesto desde el iPhone igual que en la web.

- **AC1.1** (FR1.1, FR1.2) **Given** un campeonato activo válido, **When** se abre Presupuesto, **Then** se muestra una fila por equipo con las **4 métricas primarias/secundarias** visibles: `team_name`, `balance`, `performance`, `max_bid`, `prizes`. (Refinamiento de refined-mockups: la fila muestra estas métricas; `team_value`, `total_spent`, `total_income` y ops quedan **disponibles en el DTO** pero diferidas al detalle de equipo, follow-up. FR1.2 se cumple exigiendo que los 9 campos estén disponibles, no todos en la fila.)
- **AC1.2** (FR1.3) **Given** un equipo con `balance` o `performance` negativo, **When** se renderiza su fila, **Then** el valor usa el estilo `money-negative` con signo `−` y formato M/K; si es ≥0 usa `money-positive`. El color no es el único portador (hay signo).
- **AC1.3** (FR4.1, FR4.2) **Given** la carga de balances, **When** está en curso, **Then** aparece un indicador de carga (<100 ms); **When** falla, **Then** aparece un mensaje de error con Reintentar sin corromper el campeonato activo.

## US2 — Cambiar de campeonato (Must)
**Como** propietario con varios campeonatos, **quiero** cambiar el campeonato activo desde un control siempre accesible y no invasivo, **para** ver el presupuesto de cualquiera de ellos sin salir de la pantalla.

- **AC2.1** (FR3.1) **Given** la pantalla de Presupuesto, **When** toco el nombre del campeonato en la navigation bar, **Then** se despliega un menú con todos los campeonatos (`user/championships`, fallback `championships`) y el activo marcado.
- **AC2.2** (FR3.2) **Given** el menú abierto, **When** elijo otro campeonato, **Then** la pantalla recarga su presupuesto y la selección se persiste en `UserDefaults`.
- **AC2.3** (FR3.2) **Given** que cambié de campeonato, **When** reabro la app, **Then** el campeonato activo es el último seleccionado.
- **AC2.4** (FR3.3) **Given** el primer arranque sin selección previa, **When** se carga la lista, **Then** el activo es el primer campeonato.

## US3 — Ordenar la lista de equipos (Should)
**Como** propietario, **quiero** ordenar los equipos por distintas métricas, **para** comparar rápidamente saldos, rendimiento o puja máxima.

- **AC3.1** (FR2.1) **Given** la lista cargada, **When** elijo una clave de orden (`balance`, `performance`, `max_bid`, `team_value`, `total_spent`, `total_income`), **Then** la lista se reordena descendente por esa clave y la clave activa se indica en el control.

## US4 — Navegación nativa de base (Must)
**Como** propietario, **quiero** que la app tenga una barra inferior nativa moderna, **para** que se sienta como una app iOS actual y quede lista para crecer con más secciones.

- **AC4.1** (FR5.1) **Given** la app tras el login, **When** arranca, **Then** la raíz es un `TabView` con la pestaña "Presupuesto" activa y la pantalla dentro de un `NavigationStack`; el `TabView` adopta el material del sistema (Liquid Glass en iOS 26) sin código de efecto propio.

## Requisitos no funcionales ligados
- NFR1 (cero deps), NFR2 (seguridad reutiliza F1), NFR3 (fidelidad al tema Angular, validación en dispositivo), NFR4 (60 fps / <100 ms), NFR5 (accesibilidad VoiceOver + Dynamic Type), NFR6 (lógica pura en `FutmondoKit` con `swift test`) aplican transversalmente a US1–US4.

## Trazabilidad (resumen)
US1 ← FR1, FR4. US2 ← FR3. US3 ← FR2. US4 ← FR5. NFR1–NFR6 transversales. (Detalle en `traceability.json`.)

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/{business-overview,component-inventory}.md`

## Assumptions & Open Questions

None.
