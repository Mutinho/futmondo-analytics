# Plan de Bolts — Fiabilidad de la sync

> Conversation language: Spanish. Lead: aidlc-delivery-agent. Consume
> `unit-of-work.md` (U1) y `unit-of-work-dependency.md`. Skeleton OFF (afirmado en
> `team.md`: sistema en producción con pipeline maduro; intervención acotada).

## Secuencia de Bolts

Una sola unidad de trabajo (U1 sync-reliability) → **un solo Bolt**. Sin
walking-skeleton (skeleton OFF); Bolt 1 se ejecuta como Bolt regular.

```yaml
units:
  - name: sync-reliability
    depends_on: []
```

| Bolt | Unidad | Contenido | Depende de | Skeleton |
|---|---|---|---|---|
| Bolt 1 | sync-reliability | FR3.1 (estado degradado + helper), FR3.2 (except acotados), FR6 (techo price) + specs `pytest` | — | No |

## Orden interno del Bolt (test-after por capa)

1. C1/C2 — `StepStatus.DEGRADED` + helper `record_degraded_step` + su spec.
2. C3 — cablear `prizes`/`phantoms` en `sync.py` + spec (estado `degraded` + log).
3. C5 — techo `PRICE_SANITY_CAP` en `place_bid` + spec (rechazo 422).
4. C4 — `except` acotados (arranque/migraciones + camino de sync) + specs.

## Sources

- `inception/units-generation/unit-of-work.md` (U1), `unit-of-work-dependency.md`.
- `team.md` (skeleton OFF; squash-merge; gate CI bloqueante).

## Assumptions & Open Questions

None.
