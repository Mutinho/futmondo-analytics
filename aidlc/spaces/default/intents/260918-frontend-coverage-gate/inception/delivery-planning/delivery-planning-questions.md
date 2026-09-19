# Delivery Planning — Preguntas

Intent: `frontend-coverage-gate` (scope `classic`, brownfield). Una sola unidad de trabajo (`U1` frontend-coverage-gate, `depends_on: []`), así que la secuencia de Bolts es un **único Bolt**. Las decisiones de práctica ya afirmadas (walking skeleton OFF; deploy on-merge; coste 0 €; orden interno FR10 → FR17.1) no se vuelven a preguntar. Estas preguntas cubren solo lo que queda abierto.

## Q1 — Preocupación principal para secuenciar (riesgo)

Un Bolt es una pasada de construcción sobre una pieza del trabajo que termina en algo que corre y se puede demostrar. Con un único Bolt, la secuencia externa es trivial; el orden que importa es el interno. ¿Cuál es tu mayor preocupación, para abordarla primero dentro del Bolt?

- A. Los **supuestos técnicos**: (A2) que el builder `@angular/build:unit-test` de Angular 22 acepte las opciones `coverage.*` en el target `test`, y (A3) que activar el umbral en `ng test` se propague al gate en `ci.yml` y `verify`. Abordarlos primero con un spike de cableado/medición antes de sembrar en masa. (recomendado)
- B. La **estabilidad del gate**: que el umbral inicial no rompa el gate bloqueante de inmediato (medir base tras siembra P0 y fijar por debajo).
- C. Otra preocupación.
- X. Other (please specify)

[Answer]: A

## Q2 — Staffing de Construcción

¿Cómo quieres dotar la fase de Construcción?

- A. **Aquí mismo, una unidad a la vez, aprobando sobre la marcha** (solo). Con una sola unidad es lo natural; construyo yo y tú apruebas en los gates. (recomendado)
- B. **Varios equipos, cada uno dueño de una unidad** con aprobación independiente. (Requiere orden por-unidad; con una sola unidad no aporta.)
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct