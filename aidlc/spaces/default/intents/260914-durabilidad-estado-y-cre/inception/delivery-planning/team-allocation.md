# Team Allocation — Durabilidad del estado y credenciales

> Asignación de Bolts a mob (un mob es el grupo que construye junto). Team Formation
> (etapa 1.5) no se ejecutó en este intent, así que todos los Bolts los ejecuta
> `aidlc-developer-agent` (AI). No hay Program Board (una sola línea de ejecución).

## Sources

- bolt-plan.md (Bolt 1 = U1, Bolt 2 = U2; en serie) [scope]
- ideation/ (sin team-formation/ — 1.5 no ejecutada) [scope]

## Asignación

| Bolt | Unidad | Mob / Owner | Modo |
|------|--------|-------------|------|
| Bolt 1 — Sesión durable | U1 (u1-durable-session) | `aidlc-developer-agent` (AI) | solo, en serie |
| Bolt 2 — Tareas durables | U2 (u2-durable-sync-tasks) | `aidlc-developer-agent` (AI) | solo, en serie |

## Notas

- **Sin Team Formation:** no hay equipos humanos formados; la construcción la ejecuta el
  agente desarrollador en una sola sesión, con aprobación humana en los gates.
- **Program Board:** no aplica (un solo owner, ejecución serie).
- **Way of Working:** trunk-based, base/destino `main`, squash-merge por Bolt.
