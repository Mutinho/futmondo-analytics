# Performance Requirements — u1-durable-session

> NFR Requirements (Construction). Derivados de NFR2. Sin umbral numérico absoluto (medición
> en build), presupuesto de latencia relativo comprobable por diseño.

## Sources

- requirements.md (NFR2: sin umbral numérico en esta etapa; se valida por medición) [scope]
- functional-design/functional-spec.md (caché best-effort delante del servicio) [scope]
- nfr-requirements-questions.md (Q1-A) [Q1]

## Requisitos de rendimiento

| ID | Requisito | Target | Método de validación | Fuente |
|----|-----------|--------|----------------------|--------|
| NFR2.1 | La persistencia de sesión no añade más de **una** operación de BD por operación en el camino caliente. Una petición con la sesión en caché se sirve **sin** ir a BD. | ≤ 1 op BD por operación de sesión; 0 en cache-hit | Revisión de diseño + medición ligera en build (conteo de queries en test) | NFR2 |
| NFR2.2 | La reconstrucción de sesión (rehidratación) ocurre **como máximo una vez** por reinicio y usuario (no en cada petición). | 1 re-auth por (reinicio, usuario) | Test: N peticiones tras reinicio ⇒ 1 sola reconstrucción (idempotencia BR1.2) | NFR2, FR1.2 |

## Presupuesto y notas

- **Sin p95/p99 absoluto** en esta etapa: `requirements.md` difiere el umbral numérico a
  medición en diseño/build, y no hay infra de load-testing a coste 0€. Se fija el presupuesto
  como coste de BD por operación, no como tiempo absoluto.
- El caché en memoria (`SessionStore`, best-effort) absorbe el camino caliente; la BD solo se
  toca en miss o escritura, coherente con BR1.5 (autoridad BD) sin penalizar la lectura repetida.
- Anti-requisito descartado: "la sesión debe ser rápida" (no medible) → sustituido por NFR2.1/2.2.
