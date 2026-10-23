# External Dependency Map — F3 Mercado

> Ítems externos que podrían bloquear un Bolt (APIs nuevas, ventanas de
> disponibilidad de datos, tiempos de aprobación, hand-offs de otro equipo),
> mapeados al Bolt que los consume. F3 está **totalmente autocontenido** en la
> capa nativa, así que este mapa está vacío.

## Sources

- `.../inception/delivery-planning/bolt-plan.md`.
- `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md`,
  `component-inventory.md` (contratos backend existentes).

## Mapa de dependencias externas

| Dependencia | Propietario | Lead time | Bolt bloqueado | Plan si se retrasa |
|---|---|---|---|---|
| (ninguna) | — | — | — | — |

## Notas

- F3 **consume contratos backend ya existentes e inalterados**
  (`GET /api/v1/market/today`, `POST /api/v1/market/bid`,
  `POST /api/v1/market/cancelbid`, `GET /api/v1/sofascore/player/{name}`). No hay
  API nueva, migración de datos, aprobación externa ni hand-off de otro equipo que
  pueda bloquear el Bolt.
- **Sin dependencias de pago ni servicios nuevos** (mandato coste 0 €): sólo SDK
  de Apple.
- La **publicación de la app en la App Store** (Apple Developer Program,
  excepción acotada de coste) **NO forma parte de este intent**: F3 entrega código
  nativo, no una release distribuida.

## Assumptions & Open Questions

None.
