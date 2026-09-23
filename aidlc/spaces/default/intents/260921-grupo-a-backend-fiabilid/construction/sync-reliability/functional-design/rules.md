# Reglas de comportamiento — U1 sync-reliability

> Conversation language: Spanish.

## Reglas

- **BR1 (FR3.1)**: si un paso non-critical (`prizes`, `phantoms`) lanza durante la
  sync, su estado en `progress[step]` es `degraded` con un `reason`, y se emite un
  log estructurado. NUNCA `done` con un fallo enterrado.
- **BR2 (FR3.1)**: un paso que completa sin excepción conserva `status == "done"`
  (sin regresión de comportamiento).
- **BR3 (NFR1)**: la Tarea global puede terminar `completed` aunque un paso quede
  `degraded` (la sync termina; el paso non-critical se degrada). El consumidor de
  fiabilidad lee `progress[step].status`.
- **BR4 (FR6)**: `place_bid` rechaza con 422 si `price <= 0` (existente) o si
  `price > PRICE_SANITY_CAP` (nuevo), antes de proxyar a Futmondo.
- **BR5 (FR3.2)**: en los loci en alcance (arranque/migraciones + camino de sync),
  un fallo fatal se propaga con contexto; uno recuperable se registra y continúa.
  Prohibido capturar-y-silenciar.

## Sources

- `functional-spec.md` (FS1-FS4), `inception/requirements-analysis/requirements.md`.

## Assumptions & Open Questions

None.
