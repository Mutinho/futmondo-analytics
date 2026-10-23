# Bolt Plan — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (delivery-planning). Idioma: castellano; tokens técnicos verbatim en inglés.
> Walking skeleton OFF (sistema en producción; sin arranque de cero). Squash-merge trunk-based.

## Secuencia de Bolts

```yaml
units:
  - name: u1-budget-data
    kind: library
    depends_on: []
  - name: u2-budget-ui
    kind: ui
    depends_on: [u1-budget-data]
```

| Bolt | Unidad | Contenido | Checkpoint |
|------|--------|-----------|------------|
| Bolt 1 | `u1-budget-data` | DTOs, `MoneyFormatter`, `TeamBudgetSort`, `BudgetService`/`ChampionshipService` (fallback), `ActiveChampionshipStore` | `cd ios && swift build && swift test` verde |
| Bolt 2 | `u2-budget-ui` | `RootTabView`, `BudgetView`+`BudgetViewModel`, `BudgetRow`, `ChampionshipMenu` | `swift build` verde + validación en iPhone 13 Pro |

- **Sin walking skeleton** (team practice OFF): Bolt 1 es un Bolt normal.
- **Orden forzado por dependencia**: Bolt 1 antes que Bolt 2.
- Cada Bolt = una rama corta `feat(...)` squash-merge a `main`; el gate de CI aplica en el PR.

## Autonomía de construcción (a confirmar en el checkpoint)

Propuesta (como en F1): **autónomo hasta el checkpoint de cada unidad**, con un "ok" por summary. Se confirma al entrar en Construcción.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/units-generation/*`
- `aidlc/spaces/default/memory/team.md` (Walking Skeleton OFF, squash-merge, gate de CI)

## Assumptions & Open Questions

None.
