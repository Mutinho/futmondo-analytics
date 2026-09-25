# Scalability Design — u2-integrations (Integraciones)

U2 **no cambia la escalabilidad ni la topología**. Es una intervención de
fiabilidad acotada; se documenta el diseño heredado en lugar de inventar
estrategias de escalado.

Consume: `scalability-requirements.md`, `functional-spec.md`, `tech-stack-decisions.md`.
Perspectivas inline: arquitecto + plataforma (Fly.io).

## Diseño por requisito

### NFR-scale.1 — Sin alterar el modelo de carga

- **Diseño**: el endurecimiento de errores no cambia la concurrencia, el volumen
  de datos ni la frecuencia de escritura del sync. La transacción atómica de
  `team_prizes` opera sobre el mismo volumen que el borrado+repoblado actual.

## Sin cambio (heredado)

- **Topología Fly.io**: dos apps `min=max=1`, `shared-cpu-1x`/256 MB — sin
  auto-scaling; escala fija por diseño (coste 0 €).
- **Neon PostgreSQL (tier free)**: sin cambio en el uso; U2 no aumenta la carga.
- **Crons one-shot** (04:30 / 05:00 UTC): cadencia sin cambio.

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- Horizontal scaling / sharding / read replicas / colas de desacople →
  NO-APLICA (topología fija, coste 0 €, sin necesidad en el alcance de U2).
- Proyección de capacidad / multiplicadores de crecimiento → no aplican a esta
  intervención de fiabilidad.

## Assumptions & Open Questions

None.
