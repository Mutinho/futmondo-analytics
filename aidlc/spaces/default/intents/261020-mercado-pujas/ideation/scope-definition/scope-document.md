# Scope Document — F3 Mercado (app nativa iOS)

## Sources

- `.../ideation/intent-capture/intent-statement.md` — intent, alcance confirmado
  (Q1–Q4 = A).
- `.../ideation/feasibility/feasibility-assessment.md` y `constraint-register.md`
  — viabilidad y restricciones C1–C9.

## Objetivo del alcance

Entregar la **pantalla de Mercado** en la app nativa iOS (SwiftUI) como **segunda
pestaña** del `TabView` (tras Presupuesto), con **lectura** (banner + cards +
orden), **escritura** (pujar/cancelar) y **detalle Sofascore**, reproduciendo la
vista Angular y reutilizando la base de F1/F2. Sin cambios de backend.

## Dentro de alcance

- **Navegación**: `RootTabView` pasa de 1 a **2 pestañas** — "Presupuesto"
  (existente) + "Mercado" (nueva). Mercado es la 2ª sección.
- **Lectura de Mercado** (`GET /api/v1/market/today`):
  - Banner de usuario: Presupuesto, En pujas, Balance, Puja máxima, Disponible.
  - Lista de **cards** de jugador (campos 1:1 con la card Angular): avatar,
    nombre, equipo + logo, badge Sofascore, badge % titular, chip(s) de posición,
    grid (valor, tendencia, precio de mercado, puja sugerida, puntos, media),
    marca de favorito.
  - **Selector de orden** descendente por campo (value, change, sofascore_rating,
    starter_pct, suggested_bid, points, average).
  - Estados de carga / error / vacío.
- **Escritura**:
  - **Pujar**: diálogo con importe (default = puja sugerida; mín = precio de
    mercado; máx = disponible para pujas), validación inline, `POST /market/bid`,
    resultado (aceptada / rechazada por backend / error de red), refresco.
  - **Cancelar puja activa**: confirmación, `POST /market/cancelbid` con
    `current_bid_id`, resultado, refresco.
- **Detalle Sofascore**: sheet nativa con carga asíncrona (rating + stats,
  estados loading/error).

## Fuera de alcance

- La **vista de tabla** del Angular (nativo reproduce sólo cards).
- **Calculadora / Finanzas** (= F4, otro intent) y cualquier otra sección no
  portada.
- **Cambios de backend** o de contrato de API (sólo consumo).
- **Pestañas o secciones adicionales** más allá de Presupuesto + Mercado.
- **Distribución** (Apple Developer Program) — excepción acotada no activada.
- Migración a **asset catalog** (`actool` no disponible en WSL; tokens en código).

## Criterios de aceptación de alcance (verificables)

- Existe una 2ª pestaña "Mercado" en el `TabView`.
- La pantalla carga y muestra banner + cards + orden para el campeonato activo.
- El usuario puede pujar (con validación) y cancelar, con señal de resultado y
  refresco.
- El detalle Sofascore se abre como sheet con sus estados.
- Tema oscuro/neón y `DesignSystem` preservados.

## Assumptions & Open Questions

None.
