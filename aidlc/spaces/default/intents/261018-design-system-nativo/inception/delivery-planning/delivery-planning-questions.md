# Delivery Planning — Preguntas de secuenciación

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, xtool, WSJF) verbatim en inglés.
> Secuencia de Bolts (un Bolt = una pasada de construcción sobre una porción del trabajo que acaba en algo que corre). DAG: U1 (librería) → U2 (revestir login). Rellena cada `[Answer]:`.

## Q1. ¿Qué construir primero y con qué criterio?

- A. Orden por dependencias (el único posible aquí): Bolt 1 = U1 `u1-design-system` (librería: tokens + componentes + catálogo), Bolt 2 = U2 `u2-login-theming` (revestir login). U2 no puede empezar hasta tener U1.
- B. Otro criterio (indica cuál).
- X. Other (please specify)

[Answer]: A. Orden por dependencias: Bolt 1 = U1 (librería), Bolt 2 = U2 (revestir login).

## Q2. ¿Puntuar/rankear con un modelo formal (WSJF)?

- A. No: con 2 Units y dependencia estricta, el orden es forzado; no aporta un modelo de puntuación.
- B. Sí, aplicar WSJF.
- X. Other (please specify)

[Answer]: A. No; con 2 Units y dependencia estricta el orden es forzado.

## Q3. ¿Tamaño de un Bolt?

- A. Un Bolt = una Unit (Bolt 1 = U1, Bolt 2 = U2). Simple y alineado con el DAG.
- B. Agrupar ambas Units en un único Bolt.
- X. Other (please specify)

[Answer]: A. Un Bolt = una Unit (Bolt 1 = U1, Bolt 2 = U2).

## Q4. ¿Bolts en paralelo o en serie?

- A. En serie (U1 → U2 por dependencia; un único mantenedor).
- B. En paralelo.
- X. Other (please specify)

[Answer]: A. En serie (U1 → U2 por dependencia; un único mantenedor).

## Q5. ¿Dependencias externas que bloqueen (APIs, datos, aprobaciones, hand-offs)?

- A. Ninguna: todo es código cliente SwiftUI autocontenido, sin backend/CI nuevos ni terceros.
- B. Sí (indica cuáles).
- X. Other (please specify)

[Answer]: A. Ninguna; todo es código cliente SwiftUI autocontenido, sin backend/CI nuevos ni terceros.

## Q6. ¿Qué es lo que más te preocupa de esta construcción (para atacarlo pronto)?

- A. La fidelidad de reproducir el tema de Angular en SwiftUI (ya mitigada: spike/catálogo en U1 antes de revestir el login en U2).
- B. Revestir F1 sin regresión.
- C. Otra (indica cuál).
- X. Other (please specify)

[Answer]: A. La fidelidad de reproducir el tema de Angular en SwiftUI (mitigada: spike/catálogo en U1 antes de revestir el login en U2).

## Consolidated Summary Confirmation

Resumen de Delivery Planning:

- **Secuencia**: Bolt 1 = U1 `u1-design-system` (librería), Bolt 2 = U2 `u2-login-theming` (revestir login), en serie por el DAG. Sin WSJF, un Bolt por Unit.
- **Dependencias externas**: ninguna (código cliente SwiftUI autocontenido).
- **Riesgo prioritario**: fidelidad del tema de Angular, validado en el catálogo de U1 antes de U2.
- **Construcción**: unit-major, serial, con checkpoints; staffing **solo** (esta sesión).
- **Comando de verificación** (aprobado): `cd ios && swift build && swift test`; verificación visual/dispositivo manual en iPhone 13 Pro.
- **Verificación de frontera Inception→Construction**: PASS (trazabilidad completa).

¿Does this all look correct?

[Answer]: Looks correct
