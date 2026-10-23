# Requirements — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (requirements-analysis). Idioma: castellano; tokens técnicos verbatim en inglés.
> Scope: `feature`. Brownfield. Cada requisito tiene criterio de aceptación verificable.

## Functional Requirements

### FR1 — Carga y visualización de Presupuesto
- **FR1.1** La app muestra, tras el login, la pantalla de Presupuesto del campeonato activo, obtenida de `GET /api/v1/analytics/balances?championship_id=<id>`.
  - *Aceptación*: con un campeonato activo válido, la lista muestra una fila por equipo del response `teams[]`.
- **FR1.2** Cada fila de equipo muestra: `team_name`, `balance`, `team_value`, `total_spent`, `total_income`, ops (`purchases_count + sales_count`), `performance`, `prizes`, `max_bid`.
  - *Aceptación*: los 9 campos de `TeamBudget` están presentes y mapeados al campo correcto del DTO.
- **FR1.3** Los valores monetarios se formatean abreviados (M/K) con signo, equivalente al `money` pipe de la web; `balance` y `performance` usan el token `money-positive` (≥0) o `money-negative` (<0).
  - *Formato concreto* (a caracterizar como lógica pura testeable): valor absoluto ≥ 1.000.000 → sufijo `M` dividiendo entre 1.000.000; ≥ 1.000 y < 1.000.000 → sufijo `K` dividiendo entre 1.000; < 1.000 → número tal cual. Un decimal cuando la parte fraccionaria aporta (p. ej. `12,4M`), sin decimal cuando es entero (p. ej. `8M`); redondeo half-up; separador decimal el de la locale (coma en es). El signo `+`/`−` se antepone en `performance` (como el `money:true` de la web); `balance` muestra `−` sólo cuando es negativo. *Aceptación*: una tabla de casos (p. ej. `12.400.000 → "12,4M"`, `8.000.000 → "8M"`, `-1.200.000 → "−1,2M"`, `5.500 → "5,5K"`, `950 → "950"`) pasa en `swift test`.

### FR2 — Ordenación
- **FR2.1** La pantalla permite ordenar la lista por: `balance`, `performance`, `max_bid`, `team_value`, `total_spent`, `total_income` (las claves de la web).
  - *Decisión explícita*: el orden es **sólo descendente** por la clave elegida (como el `sortCards` de la web); el toggle ascendente/descendente queda **diferido** (follow-up), no es una omisión.
  - *Aceptación*: elegir una clave reordena la lista de forma descendente por ese campo; la clave activa se indica en el control.

### FR3 — Selector de campeonato
- **FR3.1** La navigation bar muestra el nombre del campeonato activo con un affordance de menú (chevron); al activarlo, despliega la lista de campeonatos obtenida de `GET /api/v1/user/championships`, con fallback a `GET /api/v1/championships`.
  - *Aceptación*: el menú lista todos los `championships[]`; el activo aparece marcado.
  - *Caso de fallo*: si **ambos** endpoints fallan, se aplica FR4.2 (error + reintento) sin corromper el campeonato activo previamente persistido.
- **FR3.2** Al seleccionar otro campeonato, la pantalla recarga el Presupuesto de ese campeonato y persiste la selección en `UserDefaults`.
  - *Aceptación*: tras seleccionar, los datos corresponden al nuevo `championship_id`; al reabrir la app se restaura el mismo campeonato activo.
- **FR3.3** En el primer arranque sin selección previa, se toma el primer campeonato de la lista.
  - *Aceptación*: sin valor en `UserDefaults`, el activo es `championships[0]`.

### FR4 — Estados de carga y error
- **FR4.1** Mientras se cargan los datos, la pantalla muestra un indicador de carga.
  - *Aceptación*: al iniciar la carga de balances (incluido el cambio de campeonato), aparece el indicador de carga en <100 ms y desaparece al llegar los datos o al mostrarse el error.
- **FR4.2** Si falla la carga de balances o de campeonatos, la pantalla muestra un mensaje de error con acción de reintento, sin corromper el campeonato activo.
  - *Aceptación*: ante un fallo de red simulado, aparece el error + Reintentar; al reintentar con red OK, carga correctamente.

### FR5 — Andamiaje de navegación
- **FR5.1** La raíz de la app es un `TabView` con una única pestaña "Presupuesto"; la pantalla de Presupuesto vive dentro de un `NavigationStack` con su navigation bar.
  - *Aceptación*: la app arranca (tras login) en la pestaña Presupuesto; el `TabView` adopta el material del sistema (Liquid Glass en iOS 26) sin código de efecto propio.
### FR6 — Detalle de equipo (ampliación de alcance aprobada 2026-10-20)
- **FR6.1** Al tocar una card de equipo en Presupuesto, la app navega a una pantalla de **detalle de equipo** del `team_id`, obtenida de `GET /api/v1/analytics/balances/{team_id}` (`TeamDetailResponse`).
  - *Aceptación*: tocar una fila abre el detalle del equipo correcto (mismo `team_id`); un botón/gesto de volver regresa a la lista con el campeonato activo intacto.
- **FR6.2** El detalle muestra un **summary** (saldo actual, gastado, ingresado con tokens de dinero) y dos secciones: **Altas (Compras)** (jugador, precio, procedencia, fecha) y **Bajas (Ventas)** (jugador, precio, destino, fecha), con contador de elementos y estado vacío por sección.
  - *Aceptación*: los importes y recuentos coinciden con el response; sección sin elementos muestra "No hay compras/ventas registradas.".
- **FR6.3** Estados de carga y error del detalle con reintento, sin corromper la lista ni el campeonato activo.

## Non-Functional Requirements

### NFR1 — Coste y dependencias
- **NFR1.1** Cero dependencias externas nuevas; sólo SDK de Apple. `Package.swift` mantiene `dependencies: []`.
  - *Aceptación*: `git diff` de `Package.swift` no añade dependencias.

### NFR2 — Seguridad
- **NFR2.1** F2 reutiliza el `AuthService`/Keychain de F1; no introduce nuevo almacenamiento de credenciales ni expone secretos en errores (sin password/token en `message`/`repr`).
  - *Aceptación*: las llamadas van autenticadas con el token en memoria; ningún log/UI muestra credenciales.

### NFR3 — Fidelidad de diseño
- **NFR3.1** La pantalla reproduce la jerarquía visual y los tokens del tema Angular (verde Material 3, `Roboto`, claro/oscuro, money-positive/negative) consumiendo el DesignSystem de F1; donde no haya equivalente 1:1, Apple HIG.
  - *Aceptación*: validación visual en iPhone 13 Pro frente a la vista Angular de referencia.

### NFR4 — Rendimiento (percibido)
- **NFR4.1** El scroll de la lista es fluido (objetivo 60 fps) y el feedback de carga aparece de inmediato (<100 ms) al cambiar de campeonato.
  - *Aceptación*: observación en iPhone 13 Pro, sin jank perceptible (verificación manual; no medible en WSL).

### NFR5 — Accesibilidad
- **NFR5.1** Cada fila es un elemento VoiceOver con label compuesto; la UI escala con Dynamic Type; el significado money-positive/negative no depende sólo del color.
  - *Aceptación*: con VoiceOver activo, cada equipo se anuncia con sus métricas; con tamaño de texto grande, la UI no se rompe.

### NFR6 — Verificación
- **NFR6.1** La lógica pura (formateo de dinero, mapeo de DTOs, estado del campeonato activo, ordenación) vive en `FutmondoKit` y se cubre con `swift test`; las vistas SwiftUI van en `FutmondoApp` bajo `#if canImport(SwiftUI)` y se validan en dispositivo.
  - *Aceptación*: `cd ios && swift build && swift test` en verde; cobertura no numérica en WSL (regla durable).

## Trazabilidad

FR1–FR5 ← scope-document In Scope 1–4 y backlog M1–M6/S1. NFR1–NFR6 ← constraint-register C-01..C-08 y backlog. Endpoints y fórmula (`performance = team_value + balance - initial_budget`) ← codekb `api-documentation.md` (reverse-engineering).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/scope-definition/scope-document.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/{api-documentation,architecture,code-structure}.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/practices-discovery/team-practices.md`

## Assumptions & Open Questions

None.
