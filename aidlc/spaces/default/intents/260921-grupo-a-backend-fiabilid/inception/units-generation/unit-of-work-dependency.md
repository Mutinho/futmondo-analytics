# Units Generation — Dependencias entre unidades

## Sources

- `unit-of-work.md` (U1 sync-reliability).

## Grafo de dependencias

Una sola unidad; sin dependencias entre unidades.

```yaml
units:
  - name: sync-reliability
    depends_on: []
```

```
U1 (sync-reliability)   [sin dependencias]
```

Orden de construcción: U1 única.

## Assumptions & Open Questions

None.
