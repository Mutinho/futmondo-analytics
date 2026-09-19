# Requirements Analysis — Preguntas de clarificación

Intent: `frontend-coverage-gate` (scope `classic`, brownfield). Request autorizado: FR10 (cobertura de tests del frontend Angular) + FR17.1 (job `verify` del pipeline con tests significativos), orden FR10 → FR17.1, coste 0 €, sin reescrituras.

Las decisiones de práctica ya resueltas en Practices Discovery (denominador `coverage.all` + `include src/app/**`; umbral por métrica; ratcheting manual solo-arriba; config en `angular.json`; `skipTests` retirado en service/guard/interceptor/class/component; reglas duras; deuda diferida) NO se vuelven a preguntar. Estas preguntas cubren solo lo que queda abierto a nivel de requisito.

---

## Q1 — Criterio verificable de "significatividad" para FR17.1

FR17.1 exige tests "significativos" (no el anti-patrón `expect(true).toBe(true)`). Para que sea un requisito verificable con criterio pass/fail claro, ¿cómo lo fijamos?

- A. La **cobertura por métrica** (incluyendo `branches` y `functions`) actuando como proxy de significatividad: un test-espejo sin aserciones no mueve `branches`/`functions`, así que el umbral por métrica ya lo penaliza. Además, revisión humana en MR de que los specs sembrados llevan aserciones reales (payload, headers, estado). (recomendado)
- B. Añadir además una regla de lint/CI que falle ante specs sin `expect(...)` (verificación automática extra).
- C. Solo cobertura por métrica, sin requisito explícito de aserciones significativas.
- X. Other (please specify)

[Answer]: A

---

## Q2 — ¿El alcance de siembra de fase 1 es un requisito duro o una guía?

Practices Discovery fijó la fase 1 (Q4=B): los 10 servicios `core/services/*` + `core/guards/auth.guard.ts` + `core/interceptors/auth.interceptor.ts` + el componente bid-dialog del mercado. ¿Cómo lo tratamos a nivel de requisito?

- A. **Requisito duro**: la fase 1 DEBE cubrir esa lista completa antes de activar el umbral bloqueante (traza clara, criterio de aceptación por pieza). (recomendado)
- B. Guía priorizada: sembrar por prioridad P0/P1/P2 y activar el umbral cuando la línea base sea estable, sin exigir la lista completa de golpe.
- C. Mínimo duro (P0: `auth.guard` + `auth.service`) + resto como guía.
- X. Other (please specify)

[Answer]: C

---

## Q3 — Umbral inicial: ¿piso mínimo como requisito, o "medido y por debajo de base"?

El valor exacto del umbral se mide tras la siembra (ya decidido). ¿Quieres fijar además un **piso mínimo de arranque** como requisito, o dejarlo totalmente derivado de la medición?

- A. **Sin piso fijo**: el umbral inicial es exactamente "medido tras la siembra, fijado ligeramente por debajo de la base (colchón 2–5 pts), por métrica". El requisito es que exista y bloquee, no un número concreto. (recomendado)
- B. Fijar un piso mínimo simbólico por métrica (p. ej. ≥ el valor medido, redondeado hacia abajo) como requisito explícito.
- C. Fijar un objetivo de cobertura a medio plazo (p. ej. 80% líneas) como requisito aspiracional documentado, no bloqueante.
- X. Other (please specify)

[Answer]: A

---

## Q4 — "Definition of Done" del intent a nivel de requisito

¿Cuál es el criterio mínimo de "hecho" que debe cumplir el intent para considerarse completo?

- A. `angular.json` deja de nacer código de lógica sin spec (FR10.1); `ng test` mide y **exige** cobertura por métrica contra un umbral con denominador estable (FR10.2); ese umbral **bloquea** en `ci.yml` y en `verify` (FR17.1); los specs sembrados de fase 1 pasan con aserciones reales; la suite existente permanece en verde; coste 0 €. (recomendado)
- B. Lo anterior, pero permitiendo activar el umbral solo en `ci.yml` en esta entrega y `verify` en una posterior.
- C. Otro criterio de hecho.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Fuente de estado y trazabilidad

El estado actual está verificado en `docs/BACKLOG-cobertura-frontend-y-pipeline.md` (2026-09-18) y en el `code-quality-assessment.md` del RE. ¿Confirmas que esos son la fuente de verdad del estado base y que los requisitos deben trazar a FR10.1, FR10.2 y FR17.1 tal cual?

- A. Sí, trazar a FR10.1 / FR10.2 / FR17.1 y usar el backlog + `code-quality-assessment.md` como estado base verificado. (recomendado)
- B. Sí, pero quiero renumerar/añadir requisitos adicionales (indicar cuáles).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
