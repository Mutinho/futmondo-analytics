# Domain Design — Decisiones (ADRs) (F3 Mercado)

## Sources

- `.../inception/domain-design/components.md`.
- `.../inception/requirements-analysis/requirements.md`,
  `.../ideation/feasibility/constraint-register.md`.

## ADR-1 — Partición datos (FutmondoKit) vs UI (FutmondoApp)

- **Contexto**: el toolchain WSL no compila el target SwiftUI; la cobertura
  llvm-cov no es fiable en WSL (aprendizaje durable F1).
- **Decisión**: toda la lógica testeable (modelo, servicio, orden, validación,
  mapeo de resultado) va a `FutmondoKit` con XCTest; las vistas/ViewModel van a
  `FutmondoApp` bajo `#if canImport(SwiftUI)`, validadas en dispositivo.
- **Consecuencias**: cobertura verificable en WSL para la lógica; la UI se valida
  en dispositivo (patrón idéntico a F2).
- **Alternativas rechazadas**: poner lógica en las vistas (no testeable en WSL);
  un target de tests de UI en WSL (no soportado).

## ADR-2 — Resultado de escritura tipado (`MarketWriteOutcome`)

- **Contexto**: la escritura tiene tres desenlaces (aceptada / rechazada por
  backend / error de red o 5xx) que la UI debe distinguir (FR6.4/FR7.3).
- **Decisión**: el servicio devuelve un enum tipado `.accepted` /
  `.rejected(message)` / `.networkError`, no un booleano ni `nil`. (Coherente con
  la regla durable de no usar `return None`/booleano silencioso como señal de
  fallo.)
- **Consecuencias**: la UI mapea 1:1 cada caso a su aviso; testeable con dobles.
- **Alternativas rechazadas**: propagar sólo `Bool success` (pierde el
  message/estado); lanzar excepción para el rechazo de negocio (confunde negocio
  con fallo técnico).

## ADR-3 — Tope de importe = `available_for_bids`

- **Contexto**: la vista Angular usa `max_bid`; el intent confirmó (Q1=A) el tope
  efectivo = disponible.
- **Decisión**: `BidAmountValidator` valida contra `[market_price,
  available_for_bids]`. El tope absoluto del backend (5e9) no se replica en la UI.
- **Consecuencias**: divergencia intencionada y documentada; coincide con el
  dinero realmente comprometible.
- **Alternativas rechazadas**: usar `max_bid` (permitiría pujas que el backend
  rechazaría por falta de disponible).

## ADR-4 — Sin dependencias nuevas

- **Contexto**: mandato coste 0 €, sólo SDK de Apple.
- **Decisión**: todo con SwiftUI/Foundation y el `DesignSystem` de F1/F2; los
  badges Sofascore/%titular se componen con tokens existentes.
- **Consecuencias**: `Package.swift` sigue con `dependencies: []`.
- **Alternativas rechazadas**: librerías de UI/charts de terceros.

## ADR-5 — `SofascoreService` dedicado (aislamiento de fallo)

- **Contexto**: el detalle Sofascore usa un endpoint aparte
  (`/sofascore/player/{name}`, no `/market/*`) y FR8.2 exige que su fallo no
  afecte a la lista ni a la capacidad de pujar.
- **Decisión**: la carga del detalle vive en un **`SofascoreService` actor
  dedicado**, separado de `MarketService`, con su propio resultado tipado; el
  estado del detalle es local al `SofascoreDetailSheet`.
- **Consecuencias**: aislamiento explícito; un fallo o latencia de Sofascore no
  bloquea ni ensucia el estado del Mercado.
- **Alternativas rechazadas**: meter la carga en `MarketService` (acopla dos
  endpoints de routers distintos y arriesga el aislamiento de fallo).

## ADR-6 — `SofascoreDetail` (DTO) y `SofascoreService` (actor) como componentes separados

- **Contexto**: la primera versión agrupaba el modelo `SofascoreDetail` y el
  actor `SofascoreService` bajo un único componente (C8), difuminando el dueño de
  la entidad `SofascoreDetail` (un mismo building block mezclaba un value object
  y un servicio con responsabilidades distintas).
- **Decisión**: separarlos en dos componentes. `SofascoreDetail` es el **dueño
  único** de la entidad del mismo nombre (identificada por `player_name`);
  `SofascoreService` es el actor de carga, que depende de `SofascoreDetail` pero
  no posee entidades.
- **Consecuencias**: la propiedad de la entidad queda inequívoca (una entidad =
  un componente dueño), auditable en el bloque `yaml` y en la tabla de Entity
  Ownership; el aislamiento de fallo (FR8.2) sigue intacto —el servicio sigue
  separado de `MarketService`.
- **Alternativas rechazadas**: mantener DTO y servicio en un solo componente
  (ownership ambigua, menos auditable); fusionar el servicio en `MarketService`
  (ya rechazado en ADR-5 por el acoplamiento y el riesgo al aislamiento FR8.2).

## Assumptions & Open Questions

None.
