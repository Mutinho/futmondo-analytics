# Units Generation — Dependencias entre unidades (matchday-prizes-calc)

## DAG de dependencias

Una única unidad de trabajo, sin dependencias entre unidades.

```
U1 (matchday-prizes-calc)   [sin dependencias]
```

## Puntos de integración

- Interno a U1: `PrizeSyncOrchestrator` invoca `PrizeCalculator` (llamada
  síncrona en proceso, sin contrato de red nuevo).
- U1 no integra con otras unidades de este intent (no hay otras).
- Dependencias externas (no son unidades): API Futmondo (ingesta) y Neon
  PostgreSQL (`team_prizes`).

## Oportunidades de desarrollo en paralelo

No aplica: hay una sola unidad.

## Edge block (machine-readable)

```yaml
units:
  - name: matchday-prizes-calc
    kind: service
    depends_on: []
```

## Assumptions & Open Questions

None.
