# Rationale de riesgo y secuenciación — Fiabilidad de la sync

## Sources

- `bolt-plan.md`, `unit-of-work.md`, `requirements.md`.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Regresión del comportamiento OK de la sync al introducir `degraded` | Medio | Spec que verifica que un paso NO fallido sigue `done`; cambio aditivo |
| Ampliar accidentalmente el god-file | Medio | Helper en módulo estrecho; regla afirmada; review |
| Techo de `price` demasiado bajo rechaza pujas legítimas | Bajo | `PRICE_SANITY_CAP` como múltiplo holgado documentado (R-03) |
| `except` acotados cambian comportamiento de arranque | Medio | Distinguir recuperable/fatal por locus; specs; alcance acotado |
| Romper el gate de CI (pytest) | Alto | Suite existente en verde; specs nuevas significativas; verificar antes de merge |

## Secuenciación

Orden interno del Bolt 1 (test-after por capa): helper → cableado sync →
techo price → except. Independientes entre sí salvo que el cableado usa el helper.

## Assumptions & Open Questions

None.
