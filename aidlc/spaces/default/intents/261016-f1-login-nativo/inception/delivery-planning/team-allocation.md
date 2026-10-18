# Team Allocation — F1: Login nativo end-to-end

> Fase: inception (delivery-planning). Idioma: castellano; tokens técnicos verbatim en inglés.

## Asignación

- **Equipo**: un único propietario-ejecutor (sin coordinación multi-equipo; team-formation se
  saltó por esta razón). Todos los bolts los ejecuta el mismo responsable, asistido por el
  developer agent en la generación de código.
- **Roles por bolt**:
  - Bolt 1 (backend): perfil backend Python/FastAPI + tests `pytest`.
  - Bolt 2 (cliente de red): perfil Swift/URLSession.
  - Bolt 3 (auth nativa): perfil Swift/SwiftUI + Keychain.

Todos los perfiles los cubre la misma persona; no hay dependencias de disponibilidad entre
personas.

## Sources

- [consumes] unit-of-work.md, team-practices.md; stakeholder-map de F1 (ejecutor único).

## Assumptions & Open Questions

None.
