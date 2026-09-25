# External Dependency Map — Fiabilidad backend (FR3.2 + FR4)

Ninguna dependencia externa bloquea la construcción (Q5=A). Las APIs de terceros
son dependencias en runtime, no de construcción: los tests usan dobles/fakes en
memoria (sin red, sin API real, sin credenciales). No hay hand-offs de otros
equipos ni aprobaciones externas.

| Ítem | Tipo | Bloquea | Owner | Mitigación |
|---|---|---|---|---|
| Sofascore API | runtime (tercero) | ninguno en construcción | — | tests con dobles; sin red |
| Futmondo API | runtime (tercero) | ninguno en construcción | — | tests con dobles; sin red |
| Neon PostgreSQL | runtime | ninguno en construcción | — | fixtures `_FakeInMemoryDB` (SQLite `:memory:`) |

Mapa ligero: el intent es AI-contenido, coste 0 €.

## Assumptions & Open Questions

None.
