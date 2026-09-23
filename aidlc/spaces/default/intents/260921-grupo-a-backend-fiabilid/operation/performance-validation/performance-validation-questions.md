# Preguntas — Performance Validation (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation. **Encuadre**: este intent NO
> tiene NFR de rendimiento formal (backend acotado y aditivo; ya documentado
> NO-APLICA en `build-and-test/performance-test-instructions.md`). Por tanto el
> **load testing NO-APLICA**; esta etapa valida las NFRs reales del intent
> (NFR1-NFR5) contra la evidencia existente. **Adaptación de stack**: sin
> CloudWatch/X-Ray (servicios de pago); evidencia por `pytest` + `fly logs` +
> healthcheck, coste 0 €. Respuestas determinadas por el intent (Operation:
> preguntas excepcionales).

## Q1 — ¿Patrones de tráfico esperados (steady/peak/burst)?

A. NO-APLICA — el intent no cambia el perfil de carga; sin NFR de tráfico
B. Definidos (especificar)
X. Other (please specify)

[Answer]: A. NO-APLICA. El intent (estado `degraded`, techo de `price`, `except` acotados) no introduce rutas calientes nuevas ni cambia el tráfico. No hay NFR de tráfico que validar.

## Q2 — ¿Percentiles de latencia objetivo (p50/p95/p99)?

A. NO-APLICA — sin objetivo de latencia; la latencia la domina la red a Futmondo (fuera de alcance)
B. Definidos
X. Other (please specify)

[Answer]: A. NO-APLICA. Sin NFR de latencia. Las operaciones tocadas (validación de entero, escritura de un dict de estado, log) son O(1) y no medibles como objetivo de percentil.

## Q3 — ¿Throughput a sostener?

A. NO-APLICA — sin NFR de throughput
B. Definido
X. Other (please specify)

[Answer]: A. NO-APLICA. El intent no tiene requisito de throughput.

## Q4 — ¿Cuellos de botella probables?

A. Ninguno introducido por el intent; los cambios son O(1) y aditivos
B. Identificados (especificar)
X. Other (please specify)

[Answer]: A. Ninguno introducido. El techo de `price` es una comparación de enteros; `record_degraded_step` escribe un dict y un log; el estrechamiento de `except` no añade coste. Sin regresión de rendimiento.

## Q5 — Validación de las NFRs reales del intent (NFR1-NFR5)

A. Validar NFR1 (fiabilidad observable), NFR2 (mantenibilidad), NFR3 (testabilidad), NFR4 (coste), NFR5 (seguridad) contra la evidencia de `pytest`/código/logs — SIN load testing
B. Otra cosa
X. Other (please specify)

[Answer]: A. Validar NFR1-NFR5 con la evidencia existente (suite 166 verde, código aditivo, tests significativos, coste 0 €, validación de `price` reforzada). El load testing no aplica; la matriz de validación se centra en las NFRs reales.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
