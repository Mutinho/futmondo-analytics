# Unit of Work — Story Map (F1: Login nativo end-to-end)

> Fase: inception (units-generation). Mapa unidad → historias/requisitos. Idioma: castellano;
> tokens técnicos verbatim en inglés.

| Unidad | Historias | Requisitos | Componentes |
|--------|-----------|------------|-------------|
| `backend-refresh-transport` | US-7 | FR-4, FR-9, NFR-1, NFR-3 | C6 |
| `ios-network-client` | US-8 (parcial US-4) | FR-7, NFR-2 | C1 |
| `ios-native-auth` | US-1, US-2, US-3, US-4, US-5, US-6 | FR-1, FR-2, FR-3, FR-5, FR-6, FR-8, NFR-1, NFR-2 | C2, C3, C4, C5 |

## Notas

- US-4 (refresh transparente) se reparte: el **mecanismo HTTP/reintento** vive en
  `ios-network-client` (C1) + `ios-native-auth` (C3 dueño del reintento); la **experiencia** en
  `ios-native-auth` (C4/C5).
- NFR-4 (idioma) es transversal a las tres unidades.
- La verificación manual en iPhone (NFR-3) cubre el flujo end-to-end una vez integradas las tres.

## Cobertura

Las 8 historias y los 9 FR quedan asignados a una unidad; sin historias ni requisitos huérfanos
(ver `traceability.json`).

## Sources

- [consumes] stories.md, requirements.md, components.md, unit-of-work.md.

## Assumptions & Open Questions

None.
