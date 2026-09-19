# Asignación de Bolts a Equipos — Frontend Coverage Gate

Una **mob** es el pequeño grupo que construye un Bolt junto. En este intent (scope `classic`) la etapa de formación de equipos (1.5) no se ejecutó, así que no hay equipos humanos múltiples definidos.

## Staffing de Construcción (Q2=A)

- **Modo**: **solo** — la Construcción se dota aquí mismo, una unidad a la vez, con aprobación humana en cada gate. No hay reparto entre varios equipos (una sola unidad; nada que paralelizar).
- **Iteración de Construcción**: `stage-major` (por defecto) — cada etapa de diseño corre para la única unidad y luego la siguiente; code-generation al final.

## Asignación

| Bolt | Unidad | Ejecutor |
|------|--------|----------|
| Bolt 1 | `U1` frontend-coverage-gate | `aidlc-developer-agent` (IA), con gates de aprobación humana |

Todos los Bolts los ejecuta `aidlc-developer-agent`. Al haber un único Bolt y un único equipo, **no** hay Program Board (el Program Board es el análogo cuando hay más de un equipo).

## Assumptions & Open Questions

- None.
