# Performance Design — u1-durable-session

> Etapa NFR Design (Construction). Traduce los requisitos de rendimiento (NFR2.1, NFR2.2) en
> patrones concretos. Es diseño, no implementación: los snippets son ilustrativos (≤15 líneas).

## Sources

- nfr-requirements/performance-requirements.md (NFR2.1, NFR2.2) [scope]
- nfr-requirements/tech-stack-decisions.md (reutilizar `db_connection`, capa `stores/`) [scope]
- functional-design/functional-spec.md (caché best-effort, BR1.5 BD autoridad) [scope]
- nfr-design-questions.md (Q3-A lock BD, Q5-A purga perezosa) [Q3] [Q5]

## Presupuesto de rendimiento

El presupuesto NO es un tiempo absoluto (no hay infra de load-testing a coste 0€, `requirements.md`
difiere el umbral numérico). Se expresa como **coste de base de datos por operación de sesión**:

| Objetivo | Target | Cómo se logra |
|----------|--------|---------------|
| NFR2.1 | ≤ 1 operación de BD por operación de sesión; **0** en acierto de caché | Caché en memoria `SessionStore` delante de la BD (cache-aside) |
| NFR2.2 | 1 sola reconstrucción por (reinicio, usuario) | Idempotencia de `ensureSession` (BR1.2) + lock de BD serializa (Q3-A) |

## Estrategia de caché — cache-aside (lazy loading)

Patrón cache-aside sobre `SessionStore` (en memoria de proceso, best-effort). La BD es la autoridad
(BR1.5); la caché solo absorbe el camino caliente.

```text
Lectura de sesión (ensureSession / camino caliente):
  1. SessionStore.get(user_id) -> si HIT y active -> devolver (0 ops BD)   [NFR2.1: 0 en hit]
  2. si MISS -> SELECT de UserSession en BD (1 op)                          [NFR2.1: ≤1 op]
       - si active   -> poblar caché, devolver
       - si expired  -> DELETE perezoso (Q5-A) -> tratar como absent
       - si absent   -> rehidratar (ver reliability-design)
Escritura (login / rehidratación OK):
  - upsert UserSession en BD (autoridad) -> poblar/actualizar caché
```

Reglas de consistencia de caché:
- TTL de la entrada de caché ≤ TTL de sesión (12h, BR1.1). La expiración real la manda `expires_at`
  de la BD, no la caché.
- En discrepancia caché↔BD, gana la BD (BR1.5): la caché nunca sirve una sesión que la BD considera
  expirada/ausente.
- La caché es best-effort: si el proceso se reinicia y la caché queda vacía, el diseño degrada a
  1 lectura de BD (no a fallo). No es un almacén autoritativo.

## Pooling de conexiones

Se reutiliza `db_connection` existente (Neon PostgreSQL). No se introduce un pool nuevo ni se
cambia el driver (C1, coste 0€). El lock `SELECT ... FOR UPDATE` (Q3-A) mantiene la transacción
corta: solo abarca la lectura+eventual rehidratación de una fila por `user_id`, evitando contención
amplia. La rehidratación (llamada a Futmondo) es lo más lento del camino; ocurre **como máximo una
vez** por (reinicio, usuario) (NFR2.2), no en cada petición.

## Procesamiento asíncrono

FastAPI/async ya existente. La llamada de re-auth a Futmondo durante `rehydrating` es I/O de red:
se ejecuta de forma asíncrona sin bloquear el event loop. No se añade cola ni worker (coste 0€,
NFR3); el camino de rehidratación es sincrónico respecto a la petición que lo dispara, pero solo
para el primer uso tras reinicio.

## Anti-patrones evitados

- Reconstruir la sesión en cada petición (violaría NFR2.2) — evitado por idempotencia + caché.
- Caché sin TTL que se convierte en almacén de datos rancios — evitado atando el TTL a `expires_at`.
- Ir a BD en el acierto de caché — evitado por cache-aside (0 ops en hit, NFR2.1).

## Trazabilidad

| NFR | Solución de diseño |
|-----|--------------------|
| NFR2.1 | Cache-aside con `SessionStore`; 0 ops BD en hit, ≤1 en miss; pooling reutilizado |
| NFR2.2 | Idempotencia de `ensureSession` (BR1.2) + lock de BD (Q3-A): 1 reconstrucción por (reinicio, usuario) |
