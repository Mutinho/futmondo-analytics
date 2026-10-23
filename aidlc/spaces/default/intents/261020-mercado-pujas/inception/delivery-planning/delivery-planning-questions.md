# Delivery Planning — Preguntas (F3 Mercado)

> Esta etapa planifica la **secuencia de Bolts** (un Bolt = una pasada de
> Construction sobre una o más Units, con su Definición de Hecho e hipótesis de
> confianza; la topología viene del DAG de Units Generation, aquí se elige el
> camino económico). Contexto: F3 tiene **una sola Unit** (`u1-market`,
> `depends_on: []`), la construye la IA (sin equipos humanos; single-maintainer),
> walking skeleton **OFF** (el sistema ya está en producción y la capa `ios/`
> existe). Esto colapsa casi todas las decisiones económicas.

## Q1 — ¿Qué construir primero (riesgo / valor / esqueleto / mezcla)?

- A. **No aplica un trade-off real**: hay una sola Unit, así que hay **un solo
  Bolt**. No hay "qué va primero" entre Units. Dentro del Bolt, el orden
  intra-unidad es test-after (lógica `FutmondoKit` → vistas SwiftUI).
- B. Otro (especificar).

[Answer]: A

## Q2 — ¿Modelo de scoring formal (WSJF-style)?

- A. **No**: con una sola Unit/Bolt, un modelo de scoring (WSJF) no aporta; no hay
  ranking que calcular.
- B. Sí (especificar pesos).

[Answer]: A

## Q3 — ¿Tamaño de un Bolt?

- A. **Un Bolt = la Unit `u1-market`** completa (lógica + vistas de la pantalla de
  Mercado).
- B. Otro (especificar).

[Answer]: A

## Q4 — ¿Bolts en paralelo o en serie?

- A. **No aplica**: un solo Bolt. Ejecución **serial** (unit-major), que es el
  valor por defecto de este workflow y el adecuado para una sola Unit.
- B. Otro (especificar).

[Answer]: A

## Q5 — ¿Dependencias externas que nos bloqueen?

- A. **Ninguna**: F3 consume contratos backend **ya existentes e inalterados**
  (`/api/v1/market/*`, `/api/v1/sofascore/player/{name}`); no hay APIs nuevas,
  datos, aprobaciones ni hand-offs de otro equipo. El mapa de dependencias
  externas queda vacío. (La publicación de la app en la App Store NO es parte de
  este intent.)
- B. Otro (especificar).

[Answer]: A

## Q6 — ¿Qué es lo que más preocupa del build (para atacarlo pronto)?

- A. **Riesgo principal = validación en dispositivo de la UI SwiftUI**: la lógica
  (`FutmondoKit`) es testeable en WSL con XCTest, pero las vistas (cards, banner,
  sheet de puja, sheet Sofascore) sólo se validan en dispositivo (iPhone 13 Pro).
  Mitigación: dentro del Bolt, cerrar y testear primero la lógica, luego iterar la
  UI en dispositivo. La **escritura** (pujar/cancelar) y el **aislamiento de fallo
  del detalle** (FR8.2) son los puntos de mayor cuidado funcional.
- B. Otro (especificar).

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Resumen del plan de entrega de F3 = Mercado, antes de generar los artefactos:

- **1 Bolt** — "Bolt" = una pasada de Construction sobre una pieza de trabajo que
  acaba en algo que corre. Este Bolt ejecuta la única unidad **`u1-market`** (la
  pantalla de Mercado nativa completa: lógica `FutmondoKit` + vistas `FutmondoApp`).
- **Secuenciación**: trivial (una sola Unit, `depends_on: []`); respeta el DAG sin
  desviación de orden topológico. Sin modelo de scoring (WSJF no aplica).
- **Ejecución**: **serial** (unit-major, valor por defecto del workflow).
- **Staffing**: lo construye la IA (`aidlc-developer-agent`); sin equipos humanos
  (single-maintainer). El mapa de dependencias externas queda **vacío**.
- **Definición de Hecho del Bolt**: lógica `FutmondoKit` implementada y en verde
  con XCTest (`swift test`); vistas SwiftUI validadas en dispositivo; suite
  existente (backend `pytest`, frontend `ng test`) sigue en verde en el gate de CI;
  US1–US7 cubiertas.
- **Hipótesis de confianza**: la pantalla de Mercado nativa carga `/market/today`,
  ordena, puja/cancela (con los 3 desenlaces tipados) y muestra el detalle
  Sofascore aislado, reproduciendo la vista Angular sobre la capa nativa de F1/F2
  sin cambios de backend.
- **Walking skeleton**: OFF (no aplica).
- **Artefactos a generar**: `bolt-plan.md`, `team-allocation.md`,
  `risk-and-sequencing-rationale.md`, `external-dependency-map.md`, más la
  verificación de frontera de fase (`phase-check-inception.md`).
- **Decisiones de Construction** (tras los artefactos): orden de iteración
  (unit-major, por defecto), comando de verificación (te lo propondré para
  aprobar) y staffing (una sesión IA vs equipos).

¿Todo correcto antes de generar los artefactos?

- **Looks correct** — confirmo y genero.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
