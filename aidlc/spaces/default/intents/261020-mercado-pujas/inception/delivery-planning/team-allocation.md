# Team Allocation — F3 Mercado

> Asignación de Bolts a mobs. Team Formation (1.5) no se ejecutó en este intent
> (single-maintainer), así que todos los Bolts los ejecuta la IA
> (`aidlc-developer-agent`). Con un solo equipo no hay Program Board (el tablero
> de coordinación entre varios equipos); esta asignación es trivial.

## Sources

- `.../inception/delivery-planning/bolt-plan.md`.
- `aidlc/spaces/default/memory/team.md`, `project.md` (single-maintainer, coste 0 €).

## Asignación

| Bolt | Units | Mob / propietario | Modo |
|---|---|---|---|
| Bolt 1 | u1-market | `aidlc-developer-agent` (IA) | Serial (una sola Unit) |

- **Equipos humanos**: ninguno (Team Formation no corrió; proyecto
  single-maintainer). No hay Program Board.
- **Ejecución**: una sesión de IA, serial (unit-major). No hay paralelismo entre
  Bolts (sólo hay uno).
- **Revisión**: la revisión de Construction la realiza el reviewer configurado en
  cada etapa (advisory/adversarial según corresponda); el humano (propietario)
  aprueba en los checkpoints de Unit.

## Assumptions & Open Questions

None.
