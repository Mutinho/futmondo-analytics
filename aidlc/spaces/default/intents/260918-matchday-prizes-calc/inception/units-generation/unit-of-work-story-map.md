# Units Generation — Story Map (matchday-prizes-calc)

No se produjeron user stories (etapa saltada: bug fix acotado). Se mapean los
requisitos funcionales (`FR`) a la unidad que los implementa.

| Requisito | Unit ID | Directory | Notas |
|---|---|---|---|
| FR1 (reparto ante empates) | U1 | u1-matchday-prizes-calc | Núcleo: PrizeCalculator |
| FR2 (conjunto premiable) | U1 | u1-matchday-prizes-calc | PrizeCalculator |
| FR3 (gating + retroactividad) | U1 | u1-matchday-prizes-calc | PrizeSyncOrchestrator |

## Concerns transversales

Ninguno: una sola unidad.

## Orden de implementación dentro de U1

1. Caracterización de todas las ramas de `sync_prizes` (red de seguridad, NFR1).
2. Extracción del cálculo puro (`PrizeCalculator`) y reducción de `sync_prizes`
   a orquestador.
3. Implementación de la regla de empate (FR1) y tests del nuevo contrato
   (test-after).

(El orden económico entre Bolts lo decide Delivery Planning; aquí solo se lista
el orden interno de la única unidad.)

## Verificación de cobertura

Todos los FR asignados a U1; U1 tiene requisitos asignados. OK.

## Assumptions & Open Questions

None.
